from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, pickle, json, faiss, numpy as np, torch, redis
from sentence_transformers import SentenceTransformer, util
import uvicorn, threading, time, requests, warnings

# Suppress Hugging Face warnings
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

# ---------- Load Artifacts ----------
ART_DIR = "/home/j/fiqhai-project2/embeddings"  # Update this if your path is different
chunks = pickle.load(open(os.path.join(ART_DIR, "chunks_metadata2.pkl"), "rb"))
index = faiss.read_index(os.path.join(ART_DIR, "faiss_index2.index"))
embeddings = np.load(os.path.join(ART_DIR, "embeddings_partial.npy"))
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")

# ---------- Load Local Phi-3 Model ----------
from llama_cpp import Llama

llm = Llama(
    model_path="../models/phi3/Phi-3-mini-4k-instruct-q4.gguf",  # ✅ Confirm this path exists
    n_ctx=4096,
    n_threads=4,

    # n_threads=os.cpu_count()
)

TOP_K = 10
RERANK_TOP_N = 3
MAX_CONTEXT_CHARS = 1600
MEM_TURNS = 6

# ---------- Redis Setup ----------
try:
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.ping()
    print("✅ Redis connected!")
except redis.ConnectionError:
    print("❌ Redis unavailable, chat memory disabled.")
    r = None

# ---------- Helper Functions ----------
def embed_query(text: str) -> np.ndarray:
    vec = embedder.encode([text])[0].astype("float32")
    return np.expand_dims(vec, axis=0)

def retrieve_chunks(query: str, k: int = TOP_K, rerank_n: int = RERANK_TOP_N):
    query_emb = embed_query(query)
    D, I = index.search(query_emb, k)

    candidates = []
    for idx in I[0]:
        meta = chunks[idx]
        emb = embeddings[idx]
        candidates.append((meta, emb))

    # Re-rank using cosine similarity
    scores = [float(util.cos_sim(query_emb, emb.reshape(1, -1))[0][0]) for _, emb in candidates]
    sorted_hits = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

    results = []
    context_chars = 0
    for (meta, _), score in sorted_hits:
        chunk_text = meta["text"]
        if context_chars + len(chunk_text) > MAX_CONTEXT_CHARS:
            break
        context_chars += len(chunk_text)
        results.append({
            "file": meta["file"],
            "chunk_id": meta["chunk_id"],
            "text": chunk_text,
            "score": score,
        })
    return results

def get_history(session_id):
    if r is None:
        return []
    try:
        raw = r.lrange(f"chat:{session_id}", -MEM_TURNS * 2, -1)
        return [json.loads(msg) for msg in raw]
    except Exception as e:
        print(f"Redis error: {e}")
        return []

def push_turn(session_id: str, role: str, content: str):
    if r is None:
        return
    try:
        r.rpush(f"chat:{session_id}", json.dumps({"role": role, "content": content}))
        r.ltrim(f"chat:{session_id}", -MEM_TURNS * 2, -1)
        r.expire(f"chat:{session_id}", 86400)
    except Exception as e:
        print(f"Redis push error: {e}")

# ---------- Answer Generation ----------

def generate_answer(question: str, context_chunks: list, history: list):
    import time

    # 🔹 Format chunks with source references for highlighting
    context = "\n".join(
        f"[Source: {c['file']} | Chunk {c['chunk_id']}]\n{c['text']}\n"
        for c in context_chunks
    )

    # 🔹 Prompt: Strict, focused on Islamic content only
    prompt = f"""You are an Islamic scholar AI. Use only the given Islamic texts to answer the question briefly and accurately. Avoid personal opinions or generic explanations. Base your answer strictly on the context provided below. Include Quran or Hadith references only if they are clearly present in the context. Never include fictional names, greetings, or role-play. Do not use 'User', 'Assistant', or tags like <|assistant|>.

If the answer is not found in the context, simply respond with:
"I'm sorry, I could not find the answer to your question. Please try rephrasing it or ask another question."

Context:
{context}

Question: {question}
Answer:"""

    print(f"\n⏳ Prompt length: {len(prompt)} characters")
    start_time = time.time()

    # 🔹 Inference with lower temperature to improve factuality
    response = llm(
        prompt,
        max_tokens=300,
        temperature=0.4,
        stop=["Question:", "User:", "Assistant:", "<|"],
    )

    end_time = time.time()
    print(f"✅ Model responded in {end_time - start_time:.2f} seconds")

    return response["choices"][0]["text"].strip()


# ---------- FastAPI Setup ----------
app = FastAPI()

class ChatRequest(BaseModel):
    session: str
    message: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    if not req.session or not req.message:
        raise HTTPException(status_code=400, detail="Session and message cannot be empty")
    try:
        hits = retrieve_chunks(req.message)
        history = get_history(req.session)
        answer = generate_answer(req.message, hits, history)
        push_turn(req.session, "user", req.message)
        push_turn(req.session, "assistant", answer)
        return {"answer": answer, "sources": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ---------- Server Launch ----------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 🕌 FiqAI — RAG-Based Islamic AI Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-blue?style=for-the-badge)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Accurate. Contextual. Scholarly. — Islamic guidance powered by AI.**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-how-to-use) • [Tech Stack](#-tech-stack) • [Screenshots](#-screenshots)

</div>

---

## 📖 Overview

**FiqAI** is a production-grade, Retrieval-Augmented Generation (RAG) powered Islamic knowledge assistant that delivers precise, context-aware answers to Islamic questions — grounded in the Qur'an, authentic Hadith, and verified scholarly interpretations.

Traditional methods of seeking Islamic guidance are time-consuming and often inaccessible. FiqAI bridges that gap by combining **semantic vector search** with a **locally-hosted LLM (Microsoft Phi-3-mini)** to provide instant, citation-backed answers — without compromising on authenticity.

> *"Seeking knowledge is an obligation upon every Muslim."* — Sunan Ibn Mājah

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Semantic Search** | FAISS-powered vector similarity search across 50,000+ Islamic text chunks |
| 🤖 **Local LLM** | Microsoft Phi-3-mini-4k-instruct (GGUF) runs fully on-device — no API costs |
| 💬 **Conversational Q&A** | Multi-turn dialogue with persistent chat history via Redis |
| 📚 **Authentic Sources** | Answers retrieved exclusively from Qur'an, Hadith, and verified scholarly texts |
| 🔐 **User Auth System** | Secure signup/login with session management |
| 📜 **Chat History** | View, revisit, and clear all previous conversations |
| 💡 **Feedback System** | Users can rate answers and submit suggestions for continuous improvement |
| 🌐 **Dual Frontend** | Streamlit UI + React/Vite web frontend |

---

## 🏗 Architecture

```
User Query
    │
    ▼
┌─────────────────────┐
│   Streamlit / React  │  ← Frontend Interface
│      Frontend        │
└──────────┬──────────┘
           │ HTTP Request
           ▼
┌─────────────────────┐
│    FastAPI Backend   │  ← REST API Layer
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────────┐
│  FAISS  │  │    Redis     │  ← Vector DB + Session Cache
│  Index  │  │  (Sessions)  │
└────┬────┘  └──────────────┘
     │
     ▼
┌─────────────────────┐
│  Phi-3-mini (GGUF)  │  ← Local LLM (llama-cpp-python)
│  Answer Generation  │
└─────────────────────┘
     │
     ▼
 Contextual Answer with Source Citations
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Microsoft Phi-3-mini-4k-instruct (GGUF via llama-cpp-python) |
| **Embeddings** | Sentence Transformers / HuggingFace |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Backend** | FastAPI (Python) |
| **Frontend** | Streamlit + React/Vite |
| **Cache/Sessions** | Redis |
| **Preprocessing** | Google Colab (chunking + embedding pipeline) |
| **Database** | Pickle + NumPy (.npy, .pkl, .index files) |

---

## 📁 Project Structure

```
fiqhai-project2/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── rag_pipeline.py      # Core RAG logic
│   ├── auth.py              # User authentication
│   └── models/
│       └── phi3/
│           └── Phi-3-mini-4k-instruct-q4.gguf   # ← Download separately
├── data/
│   └── embeddings/
│       ├── faiss_index2.index
│       ├── chunks_metadata2.pkl
│       └── embeddings_partial.npy
├── frontend/
│   ├── streamlit_app.py     # Streamlit UI
│   └── react-app/           # React/Vite frontend
├── Chunking_Embedding.ipynb # Google Colab preprocessing notebook
└── requirements.txt
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10+
- WSL (Ubuntu) — recommended for Windows users
- Redis
- VS Code

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/MinahilAzeem/Fiqh-AI-Rag-Chatbot.git
cd Fiqh-AI-Rag-Chatbot
```

---

### Step 2 — Set Up WSL + Redis (Windows)

Open **PowerShell as Administrator**:
```powershell
wsl --install
```
Restart your PC, then open the Ubuntu terminal:
```bash
sudo apt update
sudo apt install redis-server
```

---

### Step 3 — Create Virtual Environment

Inside WSL terminal, navigate to your project folder:
```bash
cd ~/fiqhai-project2
python3 -m venv venv
source venv/bin/activate
```

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

Install llama-cpp-python for running the GGUF model locally:
```bash
pip install llama-cpp-python
```

---

### Step 5 — Download the LLM Model

1. Visit 👉 [Phi-3-mini-4k-instruct-GGUF on HuggingFace](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-GGUF)
2. Download: `Phi-3-mini-4k-instruct-q4.gguf`
3. Place it at:
```
fiqhai-project2/models/phi3/Phi-3-mini-4k-instruct-q4.gguf
```

---

### Step 6 — Preprocessing (Google Colab)

Run `Chunking_Embedding.ipynb` on Google Colab to generate:
- `embeddings_partial.npy`
- `chunks_metadata2.pkl`
- `faiss_index2.index`

Download them and place inside `data/embeddings/`.

---

## 🚀 Running the Project

### 1. Start Redis
```bash
# In WSL terminal
redis-server
```

### 2. Start the Backend
```bash
# New WSL terminal, activate venv first
source venv/bin/activate
cd backend
uvicorn main:app --reload
```

### 3. Run Streamlit Frontend
```bash
# New terminal, activate venv
source venv/bin/activate
streamlit run frontend/streamlit_app.py
```

Open your browser at: **http://localhost:8501** ✅

---

## 💬 How to Use

**1. Signup / Login**
Create an account with your email and password, or log into an existing session.

**2. Ask Islamic Questions**
Type your question in the input box. Examples:
- *"What is riba in Islam?"*
- *"What does Islam say about kindness to parents?"*
- *"Explain the concept of tawakkul."*

The system retrieves relevant Qur'an and Hadith passages via semantic search, then generates a contextual answer using Phi-3-mini.

**3. View Chat History**
All past conversations are stored and accessible via the Chat History page. Clear anytime with one click.

**4. Submit Feedback**
Rate the quality of answers and help improve the system through the Feedback page.

**5. Logout**
End your session securely via the Logout option in the sidebar.

---

## 🔬 How the RAG Pipeline Works

1. **Chunking** — Islamic texts (Qur'an, Hadith collections) are split into semantic chunks using the Colab notebook
2. **Embedding** — Each chunk is converted to a dense vector using Sentence Transformers
3. **Indexing** — Vectors are stored in a FAISS index for millisecond-speed retrieval
4. **Query** — User's question is embedded and matched against the FAISS index (top-k retrieval)
5. **Generation** — Retrieved chunks are injected as context into Phi-3-mini prompt
6. **Response** — LLM generates a fluent, grounded answer based solely on the retrieved Islamic sources

---

## 📊 System Highlights

- ⚡ **~200ms** average query response time
- 📚 **50,000+** Islamic text chunks indexed
- 🔒 **100% local** — no data sent to external APIs
- 🧠 **Hybrid retrieval** — semantic similarity + contextual ranking
- 💾 **Persistent sessions** — Redis-backed conversation memory

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve FiqAI:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## ⚠️ Disclaimer

FiqAI is an AI-powered tool designed to assist in learning about Islamic teachings. It is not a substitute for qualified Islamic scholars. Always consult a knowledgeable scholar (*'alim*) for personal religious rulings (*fatwa*).

---

## 👩‍💻 Author

**Minahil Azeem**


[![GitHub](https://img.shields.io/badge/GitHub-MinahilAzeem-181717?style=flat&logo=github)](https://github.com/MinahilAzeem)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ for the Muslim Ummah — combining technology with timeless knowledge.
</div>

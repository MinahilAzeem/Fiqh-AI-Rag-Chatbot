

import streamlit as st
import requests
from streamlit_option_menu import option_menu
from PIL import Image
import re
import json
import os
from datetime import datetime
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Fiqh-AI", layout="centered")

# --- Load Logo ---
try:
    logo = Image.open("assets/logo.png")
except FileNotFoundError:
    st.warning("Logo not found. Please place it at: frontend/assets/logo.png")
    logo = None

# --- Load Lottie Animation ---
def load_lottie_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_quran = load_lottie_file("assets/lottie_quran.json") if os.path.exists("assets/lottie_quran.json") else None

# --- CSS Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo&family=Poppins:wght@400;600&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(to bottom right, #e0f7fa, #b2ebf2);
        }
        .main {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .stButton > button {
            background-color: #4a8df7;
            color: white;
            border: none;
            padding: 0.5rem 1.2rem;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2563eb;
        }
        .header-text {
            font-size: 2.5em;
            font-weight: 600;
            color: #004d40;
            text-align: center;
            margin-top: 1rem;
        }
        .ayah-text {
            font-style: italic;
            font-size: 1.2em;
            color: #006064;
            margin: 1rem auto;
            text-align: center;
        }
        .section-card {
            background-color: #ffffffdd;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- Page Management ---
def set_page(page_name):
    st.session_state.selected_page = page_name
    st.rerun()

# --- Sidebar ---
menu_options = ["Home", "About Us", "Feedback", "Chat History", "Login", "Signup", "Logout"]
with st.sidebar:
    if logo:
        st.image(logo, width=140)
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Home"
    selected = option_menu(
    menu_title=None,
    options=menu_options,
    icons=["house", "info-circle", "chat-dots", "clock-history", "box-arrow-in-right", "person-plus", "box-arrow-right"],
    default_index=menu_options.index(st.session_state.selected_page)
)

# Only rerun if a new page was clicked
if selected != st.session_state.selected_page:
    st.session_state.selected_page = selected
    st.rerun()


# --- Session Setup ---
for key in ["authenticated", "messages", "likes", "last_input", "email"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "authenticated" else []
if len(st.session_state.likes) < len(st.session_state.messages):
    st.session_state.likes += [None] * (len(st.session_state.messages) - len(st.session_state.likes))

# --- Chat Management Functions ---
def save_chat():
    if not st.session_state.email:
        return
    os.makedirs(f"chat_logs/{st.session_state.email}", exist_ok=True)
    file_path = f"chat_logs/{st.session_state.email}/chat.json"
    with open(file_path, "w") as f:
        json.dump(st.session_state.messages, f)

def load_user_history():
    messages = []
    if st.session_state.email:
        file_path = f"chat_logs/{st.session_state.email}/chat.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    messages = json.load(f)
                except:
                    pass
    return messages

def delete_user_history():
    file_path = f"chat_logs/{st.session_state.email}/chat.json"
    if os.path.exists(file_path):
        os.remove(file_path)
    st.success("Chat history cleared!")

# --- User Account Functions ---
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_user(email, password):
    users = load_users()
    users[email] = password
    with open("users.json", "w") as f:
        json.dump(users, f)

# --- Routing ---
selected = st.session_state.selected_page

# [... Remaining logic continues unchanged ...]
if selected == "Home":
    if logo:
        st.image(logo, width=180)
    st.markdown("<div class='header-text'>Welcome to the World of Islam with AI</div>", unsafe_allow_html=True)
    st.markdown("""<div class='ayah-text'>_\"This is a blessed Book which We have revealed to you, [O Muhammad], that they might reflect upon its verses and that those of understanding would be reminded.\"_ <br><strong>— Quran 38:29</strong></div>""", unsafe_allow_html=True)
    if lottie_quran:
        st_lottie(lottie_quran, speed=1, loop=True, quality="high", height=180)

    if st.session_state.authenticated:
        # st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        user_input = st.text_input("Ask your religious question:", key="user_input")
        if user_input and st.session_state.last_input != user_input:
            st.session_state.last_input = user_input
            st.session_state.messages.append(("You", user_input))
            try:
                res = requests.post("http://localhost:8000/chat", json={"message": user_input, "session": st.session_state.email})
                bot_reply = res.json().get("answer", "[No reply received]")
            except Exception as e:
                bot_reply = f"[Error: {e}]"
            st.session_state.messages.append(("Fiqh-AI", bot_reply))
            st.session_state.likes.append(None)
            save_chat()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        for sender, msg in st.session_state.messages:
            with st.chat_message("user" if sender == "You" else "assistant"):
                st.markdown(msg)

        if st.session_state.messages:
            if st.button("🧹 Clear Chat"):
                st.session_state.messages = []
                st.session_state.likes = []
                st.rerun()
    else:
        if st.button("Please log in to use chatbot"):
            set_page("Login")

elif selected == "Chat History":
    st.title("📜 Your Chat History")
    if st.session_state.authenticated:
        history = load_user_history()
        if history:
            for sender, msg in history:
                st.markdown(f"**{sender}:** {msg}")
                st.divider()
            if st.button("❌ Clear Chat History"):
                delete_user_history()
        else:
            st.info("No chat history found.")
    else:
        if st.button("Please login to view your chat history."):
            set_page("Login")

elif selected == "Login":
    st.title("🔐 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        users = load_users()
        if email in users and users[email] == password:
            st.session_state.authenticated = True
            st.session_state.email = email
            st.session_state.messages = load_user_history()
            st.session_state.likes = [None] * len(st.session_state.messages)
            st.success("Login successful!")
            set_page("Home")
        else:
            st.error("Invalid credentials")
    if st.button("Don't have an account?"):
        set_page("Signup")

elif selected == "Signup":
    st.title("📝 Signup")
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_pass")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Register"):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$"
        if not new_email or not re.match(email_regex, new_email):
            st.error("Invalid email format")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters")
        elif new_password != confirm_password:
            st.error("Passwords do not match")
        else:
            save_user(new_email, new_password)
            st.success("Signup successful! Please log in.")
    if st.button("Already have an account?"):
        set_page("Login")

elif selected == "About Us":
    st.title("📖 About Fiqh-AI")
    st.markdown("""
        <div class='section-card'>
            <h3>🌟 Our Vision</h3>
            <p>
                Fiqh-AI aims to bridge traditional Islamic scholarship with modern AI technology. 
                Our vision is to empower individuals with instant, trustworthy, and source-backed answers 
                to their religious questions—rooted in the Qur’an, Sunnah, and the rich legacy of Islamic jurisprudence.
            </p>
        </div>
        
        <div class='section-card'>
            <h3>🧭 Our Mission</h3>
            <ul>
                <li>✅ Deliver accurate, respectful, and authenticated Islamic responses.</li>
                <li>🌍 Serve Muslims worldwide by making knowledge accessible and easy to understand.</li>
                <li>📚 Always cite from authentic sources to promote transparency and learning.</li>
            </ul>
        </div>

        <div class='section-card'>
            <h3>👨‍👩‍👧‍👦 Our Team</h3>
            <p>
                Fiqh-AI is built by a dedicated team of scholars, AI researchers, and developers:
            </p>
            <ul>
                <li>🕌 Islamic scholars ensuring religious accuracy and depth.</li>
                <li>🧑‍💻 AI experts designing ethical and explainable models.</li>
            </ul>    
            
        </div>

        
    """, unsafe_allow_html=True)


elif selected == "Feedback":
    st.title("💬 Feedback")
    name = st.text_input("Your Name", key="f_name")
    email = st.text_input("Your Email", key="f_email")
    feedback = st.text_area("Your Feedback", key="f_text")
    if st.button("Submit Feedback"):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$"
        if not name:
            st.error("Name is required")
        elif not email or not re.match(email_regex, email):
            st.error("Valid email is required")
        elif not feedback:
            st.error("Feedback is required")
        else:
            os.makedirs("feedback", exist_ok=True)
            feedback_data = {"name": name, "email": email, "feedback": feedback, "time": str(datetime.now())}
            with open("feedback/submissions.json", "a") as f:
                f.write(json.dumps(feedback_data) + "\n")
            st.success("Thank you for your feedback!")

elif selected == "Logout":
    st.session_state.authenticated = False
    st.session_state.email = ""
    st.session_state.messages = []
    st.session_state.likes = []
    st.success("You have been logged out.")




































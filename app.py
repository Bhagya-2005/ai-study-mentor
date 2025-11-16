import streamlit as st
import sqlite3
import ollama
import json
import os
import time
from gtts import gTTS
from fpdf import FPDF
import matplotlib.pyplot as plt
import plotly.express as px

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect("users.db")
c = conn.cursor()

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# History table
c.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    input_text TEXT,
    output_text TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
conn.commit()

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "theme" not in st.session_state:
    st.session_state.theme = "🌞 Light"

# =========================
# AUTH FUNCTIONS
# =========================
def signup(email, password):
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        st.success("Sign up successful! 🎉 Please login now.")
    except sqlite3.IntegrityError:
        st.error("Email already exists ❌")

def login(email, password):
    c.execute("SELECT id FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        st.success("Login successful! ✅")
        st.experimental_rerun()
    else:
        st.error("Invalid credentials ❌")

# =========================
# LOGIN / SIGNUP PAGE
# =========================
if not st.session_state.logged_in:
    st.title("🔐 AI Study Mentor - Login / Sign Up")
    mode = st.radio("Choose Action:", ["Login", "Sign Up"])
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if mode == "Sign Up":
        if st.button("Sign Up"):
            if email.strip() == "" or password.strip() == "":
                st.error("Please fill all fields")
            else:
                signup(email, password)
    else:
        if st.button("Login"):
            if email.strip() == "" or password.strip() == "":
                st.error("Please fill all fields")
            else:
                login(email, password)
    st.stop()

# =========================
# THEME
# =========================
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.selectbox("Theme", ["🌞 Light", "🌙 Dark"])
st.session_state.theme = theme
if st.session_state.theme == "🌙 Dark":
    st.markdown(
        """
        <style>
        body {background-color: #0e1117; color: white;}
        .stButton>button {background-color:#30363d;color:white;}
        </style>
        """, unsafe_allow_html=True
    )

# =========================
# LOGOUT BUTTON
# =========================
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.success("Logged out! ✅")
    st.experimental_rerun()

# =========================
# PAGE NAVIGATION
# =========================
st.sidebar.title("📑 Navigation")
page = st.sidebar.radio("Go to", ["📊 Dashboard", "🧑‍🎓 Mentor Chat", "📝 Quiz", "📜 History"])
st.session_state.page = page

# =========================
# OLLAMA RESPONSE
# =========================
def generate_response(prompt):
    response = ollama.chat(
        model="tinyllama",  
        messages=[
            {"role": "system", "content": "You are a professional AI study mentor."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]

# =========================
# PDF EXPORT
# =========================
def save_as_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(190, 10, line)
    if not os.path.exists("PDFs"):
        os.makedirs("PDFs")
    file_path = "PDFs/study_plan.pdf"
    pdf.output(file_path)
    return file_path

# =========================
# TEXT TO SPEECH
# =========================
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("speech.mp3")
    st.audio("speech.mp3", format="audio/mp3")

# =========================
# LOAD USER HISTORY
# =========================
def load_history():
    c.execute("SELECT input_text, output_text FROM history WHERE user_id=?", (st.session_state.user_id,))
    return c.fetchall()

def save_history(user_id, input_text, output_text):
    c.execute("INSERT INTO history (user_id, input_text, output_text) VALUES (?, ?, ?)", 
              (user_id, input_text, output_text))
    conn.commit()

# =========================
# DASHBOARD PAGE
# =========================
if st.session_state.page == "📊 Dashboard":
    st.title("📊 Study Analytics Dashboard")
    
    # Example study hours (can be replaced by dynamic data)
    study_hours = [2, 3, 1, 4, 5, 2, 3]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    fig = px.line(x=days, y=study_hours, title="Weekly Study Hours", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📌 Habit Tracker")
    habits = ["Study 2 hours", "Avoid phone", "Revise notes", "Practice questions", "Wake up early"]
    progress_values = []
    for h in habits:
        val = st.slider(f"{h} ✅", 0, 100, 0)
        progress_values.append(val)
    st.button("Update Progress")
    for i, val in enumerate(progress_values):
        prog_bar = st.progress(0, text=f"{habits[i]}")
        for j in range(val+1):
            prog_bar.progress(j)
            time.sleep(0.01)
    st.success("Your habits are updated! 🎉")

# =========================
# MENTOR CHAT PAGE
# =========================
elif st.session_state.page == "🧑‍🎓 Mentor Chat":
    st.title("🧑‍🎓 AI Study Mentor")
    st.subheader("✍️ Describe your problem:")
    problem = st.text_area("Type here...")
    
    output_type = st.selectbox(
        "Select Output Type",
        ["Summary", "Detailed Plan", "Time Table", "Tips & Motivation", "Study Quiz"]
    )
    
    audio_file = st.file_uploader("🎤 Upload voice file (optional)", type=["mp3", "wav"])
    if audio_file:
        st.warning("Transcription not implemented. Please type your query.")
    
    if st.button("🚀 Generate"):
        if problem.strip() == "":
            st.error("Please type a problem.")
        else:
            st.success("Generating... Please wait.")
            with st.spinner("AI is thinking..."):
                if output_type == "Summary":
                    prompt = f"Give a short study summary for: {problem}"
                elif output_type == "Detailed Plan":
                    prompt = f"Give a very detailed step-by-step study plan for: {problem}"
                elif output_type == "Time Table":
                    prompt = f"Create a full weekly timetable for: {problem}"
                elif output_type == "Tips & Motivation":
                    prompt = f"Give motivation tips, consistency hacks & habits for: {problem}"
                elif output_type == "Study Quiz":
                    prompt = f"Create a 10-question quiz for: {problem}"
                
                output = generate_response(prompt)
                st.markdown(f"### ✅ Your AI Output:\n{output}")
                
                # Save to database
                save_history(st.session_state.user_id, problem, output)
                
                # PDF export
                pdf_path = save_as_pdf(output)
                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download PDF", f, file_name="study_plan.pdf")
                
                # Voice output
                if st.checkbox("🔊 Convert to Voice"):
                    speak(output)

# =========================
# QUIZ PAGE
# =========================
elif st.session_state.page == "📝 Quiz":
    st.title("📝 Study Quiz")
    topic = st.text_input("Enter topic for quiz")
    if st.button("Generate Quiz"):
        if topic.strip() == "":
            st.error("Enter a topic")
        else:
            prompt = f"Create a 10-question quiz on: {topic}"
            quiz = generate_response(prompt)
            st.markdown(f"### 📝 Quiz for {topic}:\n{quiz}")

# =========================
# HISTORY PAGE
# =========================
elif st.session_state.page == "📜 History":
    st.title("📜 Chat History")
    if st.button("🧹 Clear History"):
        c.execute("DELETE FROM history WHERE user_id=?", (st.session_state.user_id,))
        conn.commit()
        st.success("History cleared! ✅")
        st.experimental_rerun()
    user_history = load_history()
    for h in user_history:
        st.markdown(f"**🧑 User:** {h[0]}")
        st.markdown(f"**🤖 AI:** {h[1]}")
        st.write("---")

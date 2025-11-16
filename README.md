📚 AI Study Mentor

An interactive AI-powered study assistant built with Streamlit, designed to help students learn faster and smarter. It generates summaries, explanations, audio lessons, and organized study notes.

🚀 Features

📄 Upload PDF/DOCX/TXT study materials

🤖 AI summarization & explanations (Ollama / LLM models)

🗂 Save and view chat history

🔊 Convert responses to audio (gTTS + pydub)

📘 Export study notes to PDF

🎯 Clean, responsive UI in Streamlit

🛠 Tech Stack

Python 3

Streamlit

Ollama / LLM API

gTTS for speech

FPDF for PDF generation

pydub for audio playback

dotenv for environment variables

📦 Installation
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
pip install -r requirements.txt

▶️ Run the App
streamlit run app.py

🔑 Environment Setup

Create a .env file:

OLLAMA_API_KEY=your_key_here

📂 Project Structure
📁 AI-Study-Mentor
│── app.py
│── requirements.txt
│── chat_history.json
│── README.md
│── .env

🤝 Contributing

Pull requests are welcome!

📝 License

This project is licensed under the MIT License.

# MeetIQ – AI-Powered Meeting Analysis System

MeetIQ is an AI-powered meeting assistant designed to solve a common problem in the professional world, people attend countless meetings every day, but often forget important discussions, action items and decisions afterward.

This system allows users to upload meeting recordings or provide YouTube meeting links and the AI automatically:

- Transcribes the meeting
- Generates concise summaries
- Extracts action items
- Identifies key decisions
- Detects unresolved questions
- Enables conversational chat with the meeting using RAG (Retrieval-Augmented Generation)

MeetIQ transforms long meeting recordings into searchable, intelligent knowledge.

---

# 🚀 Features

✅ Upload Meeting Audio/Video Files  
✅ YouTube Meeting URL Support  
✅ AI-Powered Transcription using Whisper  
✅ Hindi/Hinglish to English Translation Support  
✅ Smart Meeting Summaries  
✅ Action Item Extraction  
✅ Key Decision Detection  
✅ Open Questions Extraction  
✅ Chat with Your Meeting using RAG  
✅ Vector Search with FAISS  
✅ Streamlit Interactive UI  
✅ Cloud Deployment on Hugging Face Spaces  

---

# 🧠 Problem Statement

In modern workplaces, professionals spend hours in meetings every week.

However:
- Important discussions get forgotten
- Action items are missed
- Decisions become unclear
- Team members struggle to revisit conversations

MeetIQ acts as an intelligent meeting memory assistant that converts meeting recordings into structured, searchable insights.

---

# 💡 Solution

MeetIQ uses Generative AI + Retrieval-Augmented Generation (RAG) to process meeting recordings and turn them into an interactive AI assistant.

Users simply:
1. Upload a meeting recording
2. Let the AI process it
3. Receive:
   - summaries
   - tasks
   - decisions
   - Q&A chat support

This significantly improves productivity and meeting recall.

---

# 🏗️ System Architecture

## Workflow

1. User uploads meeting recording or YouTube URL
2. Audio is extracted and chunked
3. Whisper transcribes audio locally
4. Hindi/Hinglish meetings are translated to English if required
5. LangChain LCEL pipelines generate:
   - summaries
   - action items
   - decisions
   - questions
6. Transcript is embedded using HuggingFace embeddings
7. FAISS vector store enables semantic retrieval
8. Users can chat with the meeting transcript using RAG

---

# ⚙️ Tech Stack

## Frontend
- Streamlit

## Backend
- Python

## AI / LLM
- Mistral AI
- LangChain LCEL
- Whisper

## RAG Pipeline
- FAISS
- HuggingFace Embeddings

## Audio Processing
- yt-dlp
- FFmpeg

## Deployment
- Hugging Face Spaces

---

# 📂 Project Structure

```bash
MeetIQ/
│
├── app.py
├── main.py
├── requirements.txt
├── packages.txt
├── runtime.txt
│
├── core/
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── extractor.py
│   ├── rag_engine.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
└── README.md
```

---

# 🔥 Key Functionalities

## 🎙️ AI Transcription
Uses Whisper for highly accurate speech-to-text transcription.

---

## 🌐 Hindi/Hinglish Support
Supports multilingual meeting processing using translation pipelines.

---

## 📝 AI Summarization
Automatically generates professional meeting summaries.

---

## ✅ Action Item Extraction
Extracts:
- tasks
- owners
- deadlines

from meeting discussions.

---

## 🔑 Key Decision Detection
Identifies important business decisions discussed during meetings.

---

## ❓ Open Question Detection
Finds unresolved questions and pending follow-ups.

---

## 💬 Conversational RAG Chat
Users can ask questions like:
- “What deadlines were discussed?”
- “Who is responsible for the deployment task?”
- “What decisions were finalized?”

The system retrieves relevant transcript chunks and answers intelligently.

---

# 🖥️ Demo Use Cases

### Example Queries
- “Summarize this meeting”
- “What were the key action items?”
- “Who is handling the frontend work?”
- “What pending issues were discussed?”

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/your-username/MeetIQ.git
cd MeetIQ
```

---

## Create Virtual Environment

```bash
py -m venv venv
```

Activate environment:

### Windows
```bash
venv\Scripts\activate
```

### Mac/Linux
```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
py -m pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create `.env` file:

```env
MISTRAL_API_KEY=your_api_key
SARVAM_API_KEY=your_api_key
SARVAM_STT_MODEL=saaras:v2.5
WHISPER_MODEL=base
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

---

# ☁️ Deployment

This project is deployed on Hugging Face Spaces.

---

# 📈 Future Improvements

- Speaker Diarization
- Real-time Meeting Assistant
- Zoom/Google Meet Integration
- Email Summary Automation
- Team Collaboration Dashboard
- Multi-language Support Expansion
- Meeting Analytics Dashboard

---

# 🎯 Impact

MeetIQ helps professionals:
- save time
- improve productivity
- retain meeting knowledge
- track action items effectively
- revisit discussions instantly

It acts as an AI-powered memory system for meetings.

---

# 👨‍💻 Author

Sahil Kumar

---

# ⭐ Final Note

MeetIQ is designed to bridge the gap between conversations and actionable knowledge by transforming raw meeting recordings into intelligent, searchable insights using Generative AI and RAG architecture.

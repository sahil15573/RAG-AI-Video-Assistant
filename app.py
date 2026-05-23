import streamlit as st
import time
import os
import tempfile

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions
)
from core.rag_engine import build_rag_chain, ask_question

# ─────────────────────────────────────────────────────────────
# Secrets
# ─────────────────────────────────────────────────────────────

MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
WHISPER_MODEL = st.secrets["WHISPER_MODEL"]
SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_STT_MODEL = st.secrets["SARVAM_STT_MODEL"]

# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --success: #10b981;
}

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    background: linear-gradient(
        135deg,
        #ffffff 0%,
        var(--accent-glow) 50%,
        var(--accent-2) 100%
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    color: var(--text-muted);
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
}

.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    background: var(--surface-2);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.dot-active {
    background: var(--accent-glow);
}

.dot-done {
    background: var(--success);
}

.dot-pending {
    background: var(--border);
}

.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    max-height: 400px;
    overflow-y: auto;
}

.chat-bubble {
    padding: 0.75rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}

.user-bubble {
    background: rgba(124,58,237,0.15);
}

.bot-bubble {
    background: rgba(6,182,212,0.12);
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────────

for key, default in {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def step_status(steps, key):
    s = steps.get(key, "pending")

    if s == "active":
        return "dot-active"

    if s == "done":
        return "dot-done"

    return "dot-pending"


def render_step_bar(label, key, icon):
    css = step_status(st.session_state.pipeline_steps, key)

    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:

    st.markdown(
        '<div class="hero-title" style="font-size:1.8rem">🎬 AI Video</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-sub">Meeting Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://youtube.com/watch?v=..."
    )

    uploaded_file = st.file_uploader(
        "Upload Audio / Video",
        type=["mp3", "wav", "mp4", "m4a", "mov"]
    )

    language = st.selectbox(
        "Language",
        ["english", "hinglish"],
        index=0
    )

    run_btn = st.button(
        "⚡ Analyse",
        use_container_width=True
    )

    source = None

    if youtube_url.strip():
        source = youtube_url.strip()

    elif uploaded_file is not None:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:

            tmp_file.write(uploaded_file.read())
            source = tmp_file.name

    if st.session_state.pipeline_done:

        st.markdown("---")

        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)

# ─────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="hero-title">AI Video Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-sub">Transcribe · Summarise · Chat with Meetings</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Run Pipeline
# ─────────────────────────────────────────────────────────────

if run_btn:

    if not source:
        st.error("Please upload a file or enter a YouTube URL.")

    else:

        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:

            with progress_placeholder.container():
                st.info("⚙️ Pipeline running...")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")

            action_items = extract_action_items(transcript)

            decisions = extract_key_decisions(transcript)

            questions = extract_questions(transcript)

            update_step("extract", "done")

            update_step("rag", "active")

            rag_chain = build_rag_chain(transcript)

            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }

            st.session_state.pipeline_done = True

            progress_placeholder.success("✅ Analysis complete!")

            time.sleep(1)

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ─────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────

if st.session_state.result:

    r = st.session_state.result

    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Meeting Title</div>
        <h2>{r['title']}</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div>{r['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        with st.expander("📝 Full Transcript"):

            st.markdown(
                f'<div class="transcript-box">{r["transcript"]}</div>',
                unsafe_allow_html=True
            )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div>{r['action_items']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div>{r['key_decisions']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div>{r['open_questions']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("💬 Chat with Meeting")

    if st.session_state.chat_history:

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:

            if msg["role"] == "user":

                st.markdown(f"""
                <div class="chat-bubble user-bubble">
                    <b>You:</b><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div class="chat-bubble bot-bubble">
                    <b>Assistant:</b><br>{msg['content']}
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    user_input = st.text_input(
        "Ask a question about the meeting"
    )

    if st.button("Send") and user_input.strip():

        with st.spinner("Thinking..."):

            answer = ask_question(
                r["rag_chain"],
                user_input.strip()
            )

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

else:

    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem">
        <div style="font-size:4rem">🎬</div>

        <h2 style="margin-top:1rem">
            Ready to Analyse
        </h2>

        <p style="color:#888">
            Upload a meeting recording or paste a YouTube URL
            to generate summaries, action items, and chat
            with your meeting transcript.
        </p>
    </div>
    """, unsafe_allow_html=True)
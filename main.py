# main.py
import streamlit as st

# ------------------------------
# Dependency auto-install (safe)
# ------------------------------
import sys, subprocess

def install_package(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

try:
    import google.generativeai as genai
except ImportError:
    install_package("google-generativeai")
    import google.generativeai as genai

# ------------------------------
# Streamlit page config
# ------------------------------
st.set_page_config(
    page_title="STEM Super Tutor",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------
# Check API Key
# ------------------------------
if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "❌ GEMINI_API_KEY not found!\n\n"
        "Please add it in `.streamlit/secrets.toml` or Streamlit Cloud secrets:\n\n"
        'GEMINI_API_KEY = "your_valid_api_key_here"'
    )
    st.stop()

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.title("⚙️ Tutor Settings")
    st.markdown("---")

    subject = st.selectbox(
        "📚 Subject",
        ["General STEM", "Mathematics", "Physics", "Chemistry", "Computer Science"]
    )

    personality = st.select_slider(
        "🎭 Explanation Style",
        options=["Strict/Formal", "Balanced", "Fun/Analogy-Heavy"],
        value="Balanced"
    )

    uploaded_file = st.file_uploader(
        "📁 Upload a file (txt, py, js, cpp, pdf)",
        type=["txt", "py", "js", "cpp", "pdf"]
    )

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.experimental_rerun()

# ------------------------------
# System prompt
# ------------------------------
subject_prompts = {
    "General STEM": "a world-class STEM professor",
    "Mathematics": "a Fields Medal–winning mathematician focused on proofs",
    "Physics": "a theoretical physicist emphasizing intuition",
    "Chemistry": "a master chemist explaining reactions clearly",
    "Computer Science": "a senior software architect focused on clean algorithms"
}

SYSTEM_PROMPT = rf"""
You are **STEM Super Tutor**, {subject_prompts[subject]}.

Guidelines:
1. Tone: {personality}
2. Always use LaTeX for math.
3. Explain concepts step-by-step.
4. Use bold headings, lists, and code blocks.
5. End every answer with a **guided follow-up question**.
6. Prioritize {subject} concepts.
"""

MODEL_NAME = "gemini-2.0-flash-exp"

# ------------------------------
# Initialize chat session
# ------------------------------
if "chat" not in st.session_state or st.session_state.chat is None:
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_PROMPT
        )
        st.session_state.chat = model.start_chat(history=[])
    except Exception as e:
        st.error(f"❌ Error initializing Gemini model: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------------
# UI
# ------------------------------
st.title(f"🚀 STEM Super Tutor — {subject}")
st.markdown("---")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------------
# Chat input
# ------------------------------
prompt = st.chat_input("Ask your question...")

if prompt:
    full_prompt = prompt

    # Include uploaded file content if available
    if uploaded_file:
        try:
            content = uploaded_file.read().decode("utf-8", errors="ignore")
            full_prompt = f"Context from uploaded file ({uploaded_file.name}):\n\n{content}\n\nUser question:\n{prompt}"
        except Exception as e:
            st.error(f"File read error: {e}")

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Thinking..."):
            try:
                response = st.session_state.chat.send_message(full_prompt)
                answer = response.text
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                st.error(f"❌ Gemini error: {e}")

import streamlit as st
from openai import OpenAI
import os

# Page configuration
st.set_page_config(page_title="Solar Pro 2 Learning Assistant", page_icon="📚", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Solar Pro 2 Learning Assistant")

# Sidebar for API Key (or use secrets)
with st.sidebar:
    # Try to get API key from secrets first, then environment, then input
    api_key = st.secrets.get("upstage_api_key")
    if not api_key:
        api_key = os.environ.get("upstage_api_key")
    if not api_key:
        api_key = st.text_input("Upstage API Key", key="chatbot_api_key", type="password")
        st.markdown("[Get your API key](https://console.upstage.ai/)")
    
    st.markdown("---")
    st.markdown("### Learning Guide")
    st.markdown("This assistant uses **Bloom's Taxonomy** to guide your learning:")
    st.markdown("1. **Recall**: Remembering facts")
    st.markdown("2. **Inference**: Understanding meaning")
    st.markdown("3. **Critical Thinking**: Analyzing and evaluating")
    st.markdown("4. **Creative Thinking**: Creating new ideas")

# Layout: Split screen
col1, col2 = st.columns([1, 1])

# Left Column: Reading Material
with col1:
    st.header("📖 Reading Material")
    try:
        with open("marterial.md", "r", encoding="utf-8") as f:
            material_content = f.read()
            st.markdown(material_content)
    except FileNotFoundError:
        st.error("Reading material (marterial.md) not found.")
        material_content = ""

# Right Column: Chatbot
with col2:
    st.header("🤖 AI Tutor")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial system message
        st.session_state.messages.append({
            "role": "system", 
            "content": """You are a helpful AI tutor for students. 
            Your goal is to guide the student's learning based on the provided reading material.
            Do not just give answers. Ask questions to stimulate thinking.
            Follow Bloom's Taxonomy in this order:
            1. Factual Recall: Ask questions about specific details in the text.
            2. Inference: Ask questions that require understanding the context or hidden meanings.
            3. Critical Thinking: Ask questions that require analyzing characters, motivations, or themes.
            4. Creative Thinking: Ask questions that encourage the student to imagine new scenarios or endings.
            
            Start by asking a factual question about the text."""
        })
        # Add a welcome message from the assistant
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your AI tutor. I've read the story with you. Let's talk about it. First, can you tell me who the main character is and where she came from?"
        })

    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Type your answer or question here..."):
        if not api_key:
            st.info("Please add your Upstage API Key to continue.")
            st.stop()

        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.upstage.ai/v1"
            )

            # Display assistant response
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model="solar-pro2", # Correct model name based on solar pro2.md
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"An error occurred: {e}")

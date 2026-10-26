import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"

st.set_page_config(page_title="Gemini AI Chatbot", page_icon="💬")
st.title("💬 My Gemini AI Chatbot")
st.caption("Ask a question and chat with Gemini.")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY is missing. Add it to your .env file, then restart Streamlit.")
    st.stop()

# Keep the conversation in Streamlit session state.
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini expects previous assistant messages to use the role "model".
    history = []
    for message in st.session_state.messages:
        history.append({
            "role": "model" if message["role"] == "assistant" else "user",
            "parts": [{"text": message["content"]}],
        })

    try:
        with st.chat_message("assistant"):
            with st.spinner("Gemini is thinking..."):
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=history,
                )
                answer = response.text or "Gemini returned an empty response."
                st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as exc:
        st.error(f"Gemini API error: {exc}")
        # Remove the unanswered user message so it isn't resent as history.
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop()

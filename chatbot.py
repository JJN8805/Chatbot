import streamlit as st
import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyDRGA")  # Replace with your Gemini API key

# File to store chat history
HISTORY_FILE = "chat_history.txt"

# Function to load chat history from file
def load_chat_history():
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 2):
                role = lines[i].strip()
                text = lines[i+1].strip() if i+1 < len(lines) else ""
                history.append({"role": role, "text": text})
    return history

# Function to save chat history to file
def save_chat_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for msg in messages:
            f.write(f"{msg['role']}\n{msg['text']}\n")

# Function to clear chat history file
def clear_chat_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# Load previous chat history
previous_history = load_chat_history()

# Initialize chat model
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Set up session state
if "chat" not in st.session_state:
    # ✅ Fix: use correct format expected by Gemini: {"role": ..., "parts": [...]}
    formatted_history = [{"role": msg["role"], "parts": [msg["text"]]} for msg in previous_history]
    st.session_state.chat = model.start_chat(history=formatted_history)

if "messages" not in st.session_state:
    st.session_state.messages = previous_history

# UI layout
st.title("CHATBOT 🤖")

# ✅ Show the path of the chat history file
#st.caption(f"📄 Chat history file: `{os.path.abspath(HISTORY_FILE)}`")

# Clear button
if st.button("🗑️ Clear Chat"):
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    clear_chat_history()
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])

# Input box
if prompt := st.chat_input("Say something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "text": prompt})

    # Send message to Gemini
    response = st.session_state.chat.send_message(prompt)

    # Display assistant response
    st.chat_message("assistant").markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "text": response.text})

    # Save updated chat to file
    save_chat_history(st.session_state.messages)

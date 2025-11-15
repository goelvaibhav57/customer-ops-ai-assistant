from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from graph.state import AgentState
from graph.builder import build_graph
import json
import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import os

graph = build_graph()

st.title("🔎 Chatbot with Memory")

# 2. Conversation memory setup
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []

# 3. Display previous Q&A (memory)
if st.session_state.chat_memory:
    st.markdown("**Conversation History:**")
    for role, msg in st.session_state.chat_memory:
        emoji = "🧑" if role == "User" else "🤖"
        st.markdown(f"{emoji} **{role}:** {msg}")

# 4. User input
question = st.text_input("Ask a question:")

# 5. On button, add to memory and generate answer
if st.button("Ask"):
    if question:
        thread_id = "session_2"
        st.session_state.chat_memory.append(("User", question))
        state = graph.invoke({"query": question}, config={"thread_id": thread_id})
        bot_reply = state.get('answer')

        # Add bot reply to memory
        st.session_state.chat_memory.append(("Bot", bot_reply))

        # Show latest bot reply
        st.markdown(f" **Bot:** {bot_reply}")

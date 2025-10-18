#!/usr/bin/env python3
"""
Global Chat Widget for PTCC

This component renders a persistent chat interface.
It uses st.session_state to maintain conversation history across page navigations.
The chat history is in a collapsible expander, and the input is a native, floating Streamlit component.
"""

import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8001"

def render_global_chat():
    """
    Renders a persistent chat interface by separating the history (in an expander) 
    from the input (a native, floating component).
    """

    # 1. Initialize session state if it doesn't exist
    if 'global_chat_history' not in st.session_state:
        st.session_state.global_chat_history = [{
            "role": "assistant",
            "content": "Hello! I am your global AI assistant. Ask me anything!"
        }]

    # 2. Display chat history inside a collapsible expander
    with st.expander("🤖 AI Assistant Chat", expanded=True):
        for message in st.session_state.global_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 3. Handle the chat input, which is a native floating component.
    # This part is called at the top level of the script, not inside the expander.
    if user_input := st.chat_input("What would you like to ask?"):
        # Append user message to history
        st.session_state.global_chat_history.append({"role": "user", "content": user_input})

        # Get AI response
        with st.spinner("Assistant is thinking..."):
            try:
                history = st.session_state.global_chat_history
                response = requests.post(
                    f"{API_URL}/api/chat/",
                    json={"message": user_input, "conversation_history": history},
                    timeout=30
                )
                response.raise_for_status()  # Raise an exception for bad status codes
                result = response.json()
                assistant_response = result.get("response", "I had trouble responding to that.")
            except requests.exceptions.RequestException as e:
                assistant_response = f"⚠️ Sorry, I couldn't connect to the assistant. Please check if the backend is running. (Error: {e})"
            except Exception as e:
                assistant_response = f"An unexpected error occurred: {e}"

        # Append assistant's response to history
        st.session_state.global_chat_history.append({"role": "assistant", "content": assistant_response})
        
        # Rerun to display the new messages in the expander
        st.rerun()

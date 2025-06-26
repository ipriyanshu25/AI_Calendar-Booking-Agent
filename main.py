# main.py

import streamlit as st
import requests
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TailorTalk - Calendar Booking Agent",
    page_icon="📅",
    layout="wide"
)

st.title("📅 TailorTalk - Calendar Booking Agent")
st.markdown("*Your AI assistant for booking appointments*")

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your personal booking assistant. I can help you schedule appointments on your calendar. What would you like to book?"}
    ]

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Sidebar with instructions
with st.sidebar:
    st.header("📋 How to Use")
    st.markdown("""
    **Try these examples:**
    - "Do you have any free time this Friday?"
    - "I want to schedule a call for tomorrow afternoon"
    - "Book a meeting between 3-5 PM next week"
    - "What's available on Monday morning?"
    
    **Features:**
    - ✅ Natural language understanding
    - ✅ Calendar availability checking
    - ✅ Smart time slot suggestions
    - ✅ Automatic booking confirmation
    """)
    
    st.header("🔧 System Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Backend API: Online")
        else:
            st.error("❌ Backend API: Error")
    except:
        st.error("❌ Backend API: Offline")
        st.warning("Make sure to run: `python backend/api.py`")

# Chat Interface
st.header("💬 Chat with Your Booking Agent")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    agent_response = response.json()["response"]
                    st.markdown(agent_response)
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})
                else:
                    error_msg = "Sorry, I encountered an error. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except requests.exceptions.RequestException:
                error_msg = "❌ Unable to connect to the backend. Please make sure the API server is running."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clear chat button
if st.button("🗑️ Clear Chat", type="secondary"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your personal booking assistant. I can help you schedule appointments on your calendar. What would you like to book?"}
    ]
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Built with FastAPI, LangGraph, and Streamlit*")
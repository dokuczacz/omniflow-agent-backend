import streamlit as st
import requests
import json
from datetime import datetime
import time
import os

# === CONFIGURATION ===
BACKEND_URL = "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api"
FUNCTION_KEY = os.environ.get("AZURE_FUNCTION_KEY", "")

# Set page config
st.set_page_config(
    page_title="OmniFlow Assistant - Simple",
    page_icon="🚀",
    layout="wide"
)

# === SESSION STATE INITIALIZATION ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "debug_logs" not in st.session_state:
    st.session_state.debug_logs = []
if "response_times" not in st.session_state:
    st.session_state.response_times = []
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "Unknown"
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# === CONFIGURATION SIDEBAR (Minimal) ===
st.sidebar.title("⚙️ Settings")

user_id = st.sidebar.text_input(
    "User ID",
    value="default_user",
    help="Your unique identifier"
)

categories = ["TM", "PS", "LO", "GEN", "ID", "PE", "UI", "ML", "SYS"]
selected_category = st.sidebar.selectbox(
    "Category",
    categories,
    help="Knowledge domain"
)

# === HELPER FUNCTIONS ===
def add_debug_log(message: str, level: str = "INFO"):
    """Add a debug log entry"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.debug_logs.append({
        "time": timestamp,
        "level": level,
        "message": message
    })
    # Keep only last 10 logs
    if len(st.session_state.debug_logs) > 10:
        st.session_state.debug_logs.pop(0)

def call_backend(endpoint: str, payload: dict) -> dict:
    """Call Azure backend with timing and error tracking"""
    headers = {
        "X-User-Id": user_id,
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    add_debug_log(f"Calling {endpoint}...", "INFO")
    
    try:
        url = f"{BACKEND_URL}/{endpoint}?code={FUNCTION_KEY}"
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        elapsed_time = time.time() - start_time
        
        # Track response time
        st.session_state.response_times.append({
            "endpoint": endpoint,
            "time": elapsed_time,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        # Keep only last 5 response times
        if len(st.session_state.response_times) > 5:
            st.session_state.response_times.pop(0)
        
        response.raise_for_status()
        st.session_state.backend_status = "✅ Connected"
        st.session_state.last_error = None
        add_debug_log(f"{endpoint} completed in {elapsed_time:.2f}s", "SUCCESS")
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        elapsed_time = time.time() - start_time
        error_msg = str(e)
        st.session_state.backend_status = "❌ Error"
        st.session_state.last_error = error_msg
        add_debug_log(f"{endpoint} failed: {error_msg}", "ERROR")
        return {"error": error_msg}

def send_to_llm(message_content: str) -> str:
    """Send message to LLM via backend"""
    payload = {
        "message": message_content,
        "user_id": user_id,
        "thread_id": st.session_state.get("thread_id")
    }
    
    result = call_backend("tool_call_handler", payload)
    
    if "response" in result:
        if "thread_id" in result:
            st.session_state.thread_id = result["thread_id"]
        return result["response"]
    elif "error" in result:
        return f"❌ Error: {result['error']}"
    return "❌ Error communicating with assistant"

# === DEBUGGING PANEL ===
st.title("🚀 OmniFlow Assistant")

# Debugging toolbar at the top
debug_col1, debug_col2, debug_col3, debug_col4 = st.columns([2, 2, 2, 4])

with debug_col1:
    st.metric("Backend", st.session_state.backend_status)

with debug_col2:
    avg_response_time = 0
    if st.session_state.response_times:
        avg_response_time = sum(r["time"] for r in st.session_state.response_times) / len(st.session_state.response_times)
    st.metric("Avg Response", f"{avg_response_time:.2f}s")

with debug_col3:
    st.metric("Messages", len(st.session_state.messages))

with debug_col4:
    if st.session_state.last_error:
        st.error(f"Last Error: {st.session_state.last_error[:50]}...")

# Expandable debug panel
with st.expander("🔍 Debug Panel", expanded=False):
    debug_tab1, debug_tab2, debug_tab3 = st.tabs(["📊 Response Times", "📝 Debug Logs", "ℹ️ System Info"])
    
    with debug_tab1:
        st.subheader("Recent Response Times")
        if st.session_state.response_times:
            for rt in reversed(st.session_state.response_times):
                st.text(f"[{rt['timestamp']}] {rt['endpoint']}: {rt['time']:.2f}s")
        else:
            st.text("No data yet")
    
    with debug_tab2:
        st.subheader("Debug Logs")
        if st.session_state.debug_logs:
            for log in reversed(st.session_state.debug_logs):
                level_color = {
                    "INFO": "🔵",
                    "SUCCESS": "🟢",
                    "ERROR": "🔴",
                    "WARNING": "🟡"
                }.get(log["level"], "⚪")
                st.text(f"{level_color} [{log['time']}] {log['message']}")
        else:
            st.text("No logs yet")
    
    with debug_tab3:
        st.subheader("System Information")
        st.text(f"User ID: {user_id}")
        st.text(f"Category: {selected_category}")
        st.text(f"Thread ID: {st.session_state.thread_id or 'None'}")
        st.text(f"Backend URL: {BACKEND_URL}")
        st.text(f"Total Messages: {len(st.session_state.messages)}")

st.markdown("---")

# === MAIN CHAT INTERFACE ===
st.subheader("💬 Chat Interface")

# Display chat history in a scrollable container
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input at the bottom
prompt = st.chat_input("Type your message here...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get LLM response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = send_to_llm(prompt)
        st.write(response)
    
    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# === FOOTER ===
st.markdown("---")
st.caption(f"OmniFlow Assistant | User: {user_id} | Category: {selected_category} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

import streamlit as st
import requests
from datetime import datetime

from chat_widget import render_global_chat

st.set_page_config(
    page_title="Classroom Copilot",
    page_icon="🤖",
    layout="wide"
)

# Navigation sidebar
with st.sidebar:
    # PTCC branding at top
    st.markdown("### 🏫 PTCC")
    st.markdown("Personal Teaching Command Center")
    st.markdown("---")
    
    # Main navigation
    st.markdown("### 📚 Navigation")
    st.markdown("[📋 Dashboard](/)")
    st.markdown("[📄 Briefing](/Briefing)")
    st.markdown("[🔍 Search](/Search)")
    st.markdown("[👥 Students](/Students)")
    st.markdown("---")
    st.markdown("[🤖 Classroom Copilot](/classroom_copilot)")
    st.markdown("[⚙️ Settings](/Settings)")
    st.markdown("---")
    
    # Apps section at bottom
    st.markdown("### 📱 Apps")
    if st.button("📱 Lesson Console", use_container_width=True):
        import webbrowser
        webbrowser.open("http://localhost:5174")

st.title("🤖 Classroom Copilot")
st.markdown("Chat with your AI classroom copilot for instant insights")

API_URL = "http://localhost:8001"

try:
    status_response = requests.get(f"{API_URL}/api/teacher-assistant/status", timeout=5)
    status_data = status_response.json()
    is_enabled = status_data.get("status") == "enabled"
except:
    is_enabled = False
    status_data = {"status": "unknown"}

if not is_enabled:
    st.warning("⚠️ Classroom Copilot is DISABLED")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Enable to Get Started")
        st.write("Click the button on the right to activate AI features:")
        st.write("- 💬 Chat with your assistant")
        st.write("- 🎯 Smart Student Analysis")
        st.write("- ⚠️ At-Risk Detection")
        st.write("- 📊 Behavior Pattern Recognition")
        st.write("- 🛤️ Learning Path Suggestions")
    
    with col2:
        st.markdown("### Activation")
        with st.expander("⚙️ Configure API Key"):
            api_key_input = st.text_input(
                "Gemini API Key (for testing)",
                type="password",
                help="Paste your Gemini API key here for local testing"
            )
        
        if st.button("🚀 Enable Classroom Copilot", use_container_width=True):
            with st.spinner("Activating..."):
                try:
                    params = {}
                    if api_key_input:
                        params["api_key"] = api_key_input
                    
                    response = requests.post(
                        f"{API_URL}/api/teacher-assistant/enable",
                        params=params,
                        timeout=30
                    )
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.success("✅ Activated!")
                        st.balloons()
                        st.rerun()
                    else:
                        if result.get("code") == "MISSING_API_KEY":
                            st.warning("⚙️ API key needed - Enter it above and try again")
                        else:
                            st.error(f"Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
else:
    st.success("✅ Classroom Copilot is ACTIVE and Ready!")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Add welcome message
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": "👋 Hello! I'm your AI Classroom Copilot. I can help you analyze student data, identify at-risk students, and provide insights about behavior patterns. What would you like to know about your students?"
        })
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input and suggestions
    # Quick query examples
    st.markdown("**💡 Try asking:**")
    quick_queries = [
        "What time is assembly?",
        "When is my next class?",
        "Show me high-support students today",
        "What's in the briefing from 3 days ago?",
    ]
    
    for query in quick_queries:
        if st.button(f"💬 {query}", key=f"quick_{query[:10]}", use_container_width=True):
            st.session_state.pending_briefing_query = query
            st.rerun()

    st.markdown("---")

    # Optional search filters
    with st.expander("🔍 Search Filters", expanded=False):
        doc_type_filter = st.multiselect(
            "Document Types",
            ["email", "briefing", "policy", "planning", "general"],
            default=[],
            key="doc_type_filter",
            help="Filter search by document type"
        )
        time_filter = st.selectbox(
            "Time Range",
            ["all_time", "today", "this_week", "last_week", "this_month", "this_term"],
            index=0,
            key="time_filter",
            help="Filter by document date"
        )
        results_limit = st.slider(
            "Max Results",
            1, 10, 5,
            key="results_limit",
            help="Number of results to return"
        )
    
    # Chat input
    with st.form(key="briefing_chat_form", clear_on_submit=True):
        # Check for pending query from quick buttons
        default_query = st.session_state.get('pending_briefing_query', '')
        if 'pending_briefing_query' in st.session_state:
            del st.session_state.pending_briefing_query
        
        user_input = st.text_area(
            "Ask a question:",
            value=default_query,
            height=80,
            key="briefing_chat_input",
            placeholder="e.g., What time is assembly? or Show me students with recent incidents"
        )
        
        submitted = st.form_submit_button("🚀 Ask AI", type="primary", use_container_width=True)
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get response from Gemini
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Call chat endpoint for conversational interface
                    response = requests.post(
                        f"{API_URL}/api/chat/",
                        json={
                            "message": user_input,
                            "conversation_history": st.session_state.chat_history,
                            "context_data": {},
                            "enable_agents": True,
                            "enable_search": True
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        assistant_response = result.get(
                            "response",
                            result.get("message", "No response available")
                        )
                    else:
                        assistant_response = "Unable to process your request. Please try again."
                    
                    st.markdown(assistant_response)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    error_msg = f"⚠️ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_history = [{
            "role": "assistant", 
            "content": "👋 Hello! I'm your AI Classroom Copilot. I can help you analyze student data, identify at-risk students, and provide insights about behavior patterns. What would you like to know about your students?"
        }]
        st.rerun()

render_global_chat()

st.markdown("---")
st.markdown("### 🔒 Privacy-Preserving Safeguarding System")
st.markdown("""
The Privacy-Preserving Safeguarding System uses a 6-stage pipeline to analyze student data while maintaining complete privacy and GDPR/FERPA compliance.

**Pipeline Stages:**
1. **Tokenization** - Replace all PII with anonymous tokens
2. **Pattern Extraction** - Analyze behavior patterns from multiple sources
3. **Risk Assessment** - Categorize risk levels (low/medium/high)
4. **External LLM Analysis** - Send only anonymized data to Gemini
5. **Result Localization** - Map analysis back to student context locally
6. **Report Generation** - Create actionable insights with privacy guarantees

**Privacy Guarantees:**
- Student names never sent externally
- All processing local to your school
- Token mappings stored locally only
- Complete audit trail maintained
- GDPR and FERPA compliant
""")

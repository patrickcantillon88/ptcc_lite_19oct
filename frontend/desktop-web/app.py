#!/usr/bin/env python3
"""
PTCC Desktop Web Frontend
Streamlit-based dashboard for teachers
"""

import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure Streamlit page
st.set_page_config(
    page_title="PTCC - Personal Teaching Command Center",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE = "http://localhost:8005"
API_TIMEOUT = 30  # seconds for long-running operations like document upload

def fetch_api(endpoint, params=None):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to PTCC backend. Please ensure it's running on http://localhost:8005")
        return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def format_briefing_section(title, content, icon="📋"):
    """Format a briefing section with consistent styling"""
    st.markdown(f"### {icon} {title}")
    if content:
        if isinstance(content, list):
            for item in content:
                st.markdown(f"- {item}")
        else:
            st.markdown(content)
    else:
        st.markdown("*No items*")
    st.markdown("---")

def generate_synthetic_timetable():
    """Generate synthetic timetable from student data"""
    # Fetch all students to determine classes
    students_data = fetch_api("/api/students/")
    
    if not students_data:
        return []
    
    # Extract unique classes
    classes = list(set([s['class_code'] for s in students_data]))
    
    # Get today's day of week
    today = datetime.now()
    day_name = today.strftime("%A")
    
    # Define period structure
    periods = [
        {"period": 1, "start": "08:30", "end": "09:30"},
        {"period": 2, "start": "09:35", "end": "10:35"},
        {"period": 3, "start": "10:55", "end": "11:55"},
        {"period": 4, "start": "12:00", "end": "13:00"},
        {"period": 5, "start": "14:00", "end": "15:00"},
    ]
    
    # Subject rotation (simple pattern)
    subjects = ["Computing", "ICT", "Computer Science", "Digital Literacy"]
    rooms = ["G12", "G14", "Lab 1", "Lab 2", "G11"]
    
    # Generate schedule (demo: 2-3 classes per day)
    import random
    random.seed(today.day)  # Consistent per day
    
    schedule = []
    selected_classes = random.sample(classes, min(3, len(classes)))
    
    for i, class_code in enumerate(selected_classes):
        period = periods[i]
        class_students = [s for s in students_data if s['class_code'] == class_code]
        
        schedule.append({
            "period": period["period"],
            "start_time": period["start"],
            "end_time": period["end"],
            "class_code": class_code,
            "subject": subjects[i % len(subjects)],
            "room": rooms[i % len(rooms)],
            "student_count": len(class_students),
            "high_support_count": len([s for s in class_students if s.get('support_level', 0) >= 2]),
            "recent_incidents": 0  # Would fetch from logs
        })
    
    return schedule

def show_briefing():
    """Show unified daily briefing + AI assistant page"""
    st.title("📅 Daily Briefing & AI Assistant")
    
    # Data source toggle
    col_toggle1, col_toggle2, col_toggle3 = st.columns([2, 1, 1])
    
    with col_toggle1:
        st.markdown(f"### {datetime.now().strftime('%A, %B %d, %Y')}")
    
    with col_toggle2:
        data_source = st.selectbox(
            "Data Source",
            ["📁 Uploaded Documents", "🔗 Live API (Coming Soon)"],
            key="briefing_data_source",
            help="Toggle between uploaded documents and live school systems"
        )
    
    with col_toggle3:
        if st.button("🔄 Refresh", key="refresh_briefing"):
            st.rerun()
    
    st.markdown("---")
    
    # Main layout: briefing content (left) + AI assistant (right)
    col_main, col_assistant = st.columns([2, 1])
    
    with col_main:
        show_briefing_content_unified(data_source)
    
    with col_assistant:
        show_ai_assistant_sidebar()

def show_briefing_content_unified(data_source):
    """Show unified briefing content with document uploads"""
    
    # Document upload section
    with st.expander("📤 Upload Documents", expanded=False):
        st.markdown("Upload planning notes, emails, or briefing documents for AI analysis")
        
        col_up1, col_up2 = st.columns([3, 1])
        
        with col_up1:
            uploaded_files = st.file_uploader(
                "Choose files",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                key="briefing_docs"
            )
        
        with col_up2:
            doc_type_input = st.selectbox(
                "Document Type",
                ["Auto-detect", "email", "briefing", "policy", "planning", "general"],
                key="doc_type_selector"
            )
        
        # Upload button and processing
        if uploaded_files:
            if st.button("📤 Upload Documents", type="primary", key="process_docs"):
                upload_results = []
                for uploaded_file in uploaded_files:
                    with st.spinner(f"Uploading {uploaded_file.name}..."):
                        try:
                            # Prepare file for upload
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            data = {}
                            if doc_type_input != "Auto-detect":
                                data["doc_type"] = doc_type_input
                            
                            # Make API call
                            response = requests.post(
                                f"{API_BASE}/api/documents/upload",
                                files=files,
                                data=data,
                                timeout=API_TIMEOUT
                            )
                            response.raise_for_status()
                            result = response.json()
                            upload_results.append({"success": True, "filename": uploaded_file.name, "result": result})
                            
                        except requests.exceptions.ConnectionError:
                            upload_results.append({
                                "success": False,
                                "filename": uploaded_file.name,
                                "error": "Cannot connect to backend. Please ensure it's running at http://localhost:8005"
                            })
                        except requests.exceptions.Timeout:
                            upload_results.append({
                                "success": False,
                                "filename": uploaded_file.name,
                                "error": "Upload timed out. File may be too large."
                            })
                        except requests.exceptions.RequestException as e:
                            upload_results.append({
                                "success": False,
                                "filename": uploaded_file.name,
                                "error": str(e)
                            })
                
                # Show results
                success_count = sum(1 for r in upload_results if r["success"])
                if success_count > 0:
                    st.success(f"✅ Successfully uploaded {success_count} of {len(upload_results)} documents")
                    for result in upload_results:
                        if result["success"]:
                            doc_info = result["result"]
                            st.info(f"📄 {result['filename']} → {doc_info.get('doc_type', 'unknown')} ({doc_info.get('word_count', 0)} words)")
                
                for result in upload_results:
                    if not result["success"]:
                        st.error(f"❌ {result['filename']}: {result['error']}")
        
        # Show document library (real data from backend)
        st.markdown("---")
        st.markdown("**📚 Document Library:**")
        
        col_refresh, col_empty = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 Refresh", key="refresh_docs"):
                st.rerun()
        
        try:
            response = requests.get(f"{API_BASE}/api/documents/list", timeout=10)
            response.raise_for_status()
            doc_data = response.json()
            
            if doc_data.get("documents"):
                documents = doc_data["documents"]
                st.caption(f"Total documents: {doc_data.get('total_documents', len(documents))}")
                
                for doc in documents:
                    col_doc, col_delete = st.columns([5, 1])
                    with col_doc:
                        doc_type_icon = {"email": "📧", "briefing": "📋", "policy": "📜", "planning": "📝", "general": "📄"}.get(doc.get("doc_type"), "📄")
                        st.markdown(
                            f"{doc_type_icon} **{doc.get('filename', 'Unknown')}** "
                            f"({doc.get('doc_type', 'unknown')}) - "
                            f"{doc.get('word_count', 0)} words"
                        )
                        if doc.get("uploaded_at"):
                            st.caption(f"Uploaded: {doc['uploaded_at'][:10]}")
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{doc.get('id')}", help="Delete document"):
                            try:
                                del_response = requests.delete(
                                    f"{API_BASE}/api/documents/{doc.get('id')}",
                                    timeout=10
                                )
                                del_response.raise_for_status()
                                st.success(f"Deleted {doc.get('filename')}")
                                st.rerun()
                            except requests.exceptions.RequestException as e:
                                st.error(f"Failed to delete: {str(e)}")
            else:
                st.info("📭 No documents uploaded yet. Upload your first document above!")
                
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to backend at http://localhost:8005. Please start the backend server.")
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Failed to load documents: {str(e)}")
    
    st.markdown("---")
    
    # Get briefing data
    briefing_data = fetch_api("/api/briefing/today")
    
    if not briefing_data:
        # Use synthetic data if API unavailable
        st.info("💡 Using synthetic schedule data (API unavailable)")
        briefing_data = {
            'day_name': datetime.now().strftime("%A"),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'metadata': {'classes_today': 0, 'total_students': 0},
            'schedule': generate_synthetic_timetable(),
            'student_alerts': {},
            'duty_assignments': [],
            'reminders': [],
            'communications': [],
            'insights': []
        }

    # Briefing header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### {briefing_data['day_name']}, {briefing_data['date']}")
    with col2:
        st.metric("Classes Today", briefing_data['metadata']['classes_today'])
    with col3:
        st.metric("Total Students", briefing_data['metadata']['total_students'])

    # Schedule
    if briefing_data['schedule']:
        st.markdown("## 📚 Today's Schedule")

        for period in briefing_data['schedule']:
            with st.expander(f"{period['start_time']}-{period['end_time']} | {period['class_code']} {period['subject']} | Room {period['room']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Students", period['student_count'])
                with col2:
                    if period['high_support_count'] > 0:
                        st.metric("High Support", period['high_support_count'], delta=None, delta_color="normal")
                with col3:
                    if period['recent_incidents'] > 0:
                        st.metric("Recent Incidents", period['recent_incidents'], delta=None, delta_color="inverse")

    # Student Alerts
    if briefing_data['student_alerts']:
        st.markdown("## ⚠️ Student Alerts")

        for class_code, alerts in briefing_data['student_alerts'].items():
            with st.expander(f"Class {class_code} ({len(alerts)} alerts)"):
                for alert in alerts:
                    alert_types = [a['type'].replace('_', ' ').title() for a in alert['alerts']]
                    st.markdown(f"**{alert['student_name']}**: {', '.join(alert_types)}")

    # Duty Assignments
    if briefing_data['duty_assignments']:
        st.markdown("## 👔 Duty Assignments")

        for duty in briefing_data['duty_assignments']:
            st.markdown(f"- **{duty['duty_type']}**: {duty['location']} ({duty['start_time']}-{duty['end_time']})")
            if duty['notes']:
                st.markdown(f"  *{duty['notes']}*")

    # Reminders
    if briefing_data['reminders']:
        st.markdown("## 🔔 Reminders")

        for reminder in briefing_data['reminders']:
            st.markdown(f"- **{reminder['title']}**: {reminder['message']}")

    # Urgent Communications
    urgent_comms = [c for c in briefing_data['communications'] if c.get('urgent')]
    if urgent_comms:
        st.markdown("## 🚨 Urgent Communications")

        for comm in urgent_comms:
            st.markdown(f"- **{comm['subject']}** ({comm.get('campus', 'Both')})")
            st.markdown(f"  From: {comm['sender']}")

    # Insights
    if briefing_data['insights']:
        st.markdown("## 💡 Insights")

        for insight in briefing_data['insights']:
            st.markdown(f"- {insight}")

def show_ai_assistant_sidebar():
    """Compact AI assistant sidebar for quick queries"""
    st.markdown("### 🤖 AI Assistant")
    st.markdown("*Ask about schedules, documents, or students*")
    
    # Initialize session state for chat
    if 'briefing_chat_history' not in st.session_state:
        st.session_state.briefing_chat_history = []
    if 'briefing_chat_context' not in st.session_state:
        st.session_state.briefing_chat_context = {}
    
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
    
    # Display chat history (compact, last 3 messages)
    if st.session_state.briefing_chat_history:
        recent_messages = st.session_state.briefing_chat_history[-3:]
        for msg in recent_messages:
            if msg['role'] == 'user':
                st.markdown(f"👤 **You:** {msg['content'][:100]}..." if len(msg['content']) > 100 else f"👤 **You:** {msg['content']}")
            else:
                st.markdown(f"🤖 **AI:** {msg['content'][:150]}..." if len(msg['content']) > 150 else f"🤖 **AI:** {msg['content']}")
                
                # Show document citations if available
                if msg.get('citations'):
                    st.caption(f"📚 Sources: {', '.join(msg['citations'])}")
                
                # Show time context if available
                if msg.get('time_context'):
                    st.caption(f"⏰ Context: {msg['time_context']}")
        
        if len(st.session_state.briefing_chat_history) > 3:
            st.caption(f"...{len(st.session_state.briefing_chat_history) - 3} earlier messages")
    
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
        
        if submitted and user_input.strip():
            # Add user message to history
            st.session_state.briefing_chat_history.append({
                'role': 'user',
                'content': user_input.strip(),
                'timestamp': datetime.now().isoformat()
            })
            
            # Real document search using backend RAG API
            with st.spinner("🤖 Searching documents..."):
                try:
                    # Prepare search parameters
                    search_params = {
                        "query": user_input.strip(),
                        "limit": st.session_state.get("results_limit", 5)
                    }
                    
                    # Add optional filters
                    if st.session_state.get("doc_type_filter"):
                        search_params["doc_types"] = ",".join(st.session_state["doc_type_filter"])
                    
                    if st.session_state.get("time_filter") and st.session_state["time_filter"] != "all_time":
                        search_params["time_context"] = st.session_state["time_filter"]
                    
                    # Call document search API
                    response = requests.get(
                        f"{API_BASE}/api/documents/search",
                        params=search_params,
                        timeout=15
                    )
                    response.raise_for_status()
                    search_results = response.json()
                    
                    # Process search results
                    if search_results.get("results") and len(search_results["results"]) > 0:
                        results = search_results["results"]
                        
                        # Build response from search results
                        response_text = f"Found {len(results)} relevant document(s):\n\n"
                        citations = []
                        
                        for i, result in enumerate(results[:3], 1):  # Show top 3
                            filename = result.get("filename", "Unknown")
                            doc_type = result.get("doc_type", "unknown")
                            excerpt = result.get("excerpt", "")
                            relevance = result.get("relevance_score", 0)
                            doc_date = result.get("doc_date", "")
                            
                            # Truncate excerpt
                            if len(excerpt) > 200:
                                excerpt = excerpt[:200] + "..."
                            
                            response_text += f"**{i}. {filename}** ({doc_type})\n"
                            response_text += f"{excerpt}\n"
                            response_text += f"Relevance: {relevance:.1%}\n\n"
                            
                            # Build citation
                            citation = f"{filename} ({doc_type})"
                            if doc_date:
                                citation += f" - {doc_date[:10]}"
                            citations.append(citation)
                        
                        if len(results) > 3:
                            response_text += f"\n...and {len(results) - 3} more result(s)"
                        
                        time_context = search_results.get("time_context", "All documents")
                    else:
                        response_text = f"🔍 No documents found matching '{user_input.strip()}'.\n\n"
                        response_text += "Try:\n"
                        response_text += "- Uploading more documents\n"
                        response_text += "- Using different keywords\n"
                        response_text += "- Being more specific in your query"
                        citations = []
                        time_context = "No results"
                    
                except requests.exceptions.ConnectionError:
                    response_text = "⚠️ Cannot connect to backend. Please ensure the backend is running at http://localhost:8005"
                    citations = ["Connection Error"]
                    time_context = "Error"
                except requests.exceptions.Timeout:
                    response_text = "⏱️ Search timed out. Please try again with a simpler query."
                    citations = ["Timeout"]
                    time_context = "Error"
                except requests.exceptions.RequestException as e:
                    response_text = f"❌ Search failed: {str(e)}"
                    citations = ["Error"]
                    time_context = "Error"
                
                # Add AI response to history
                st.session_state.briefing_chat_history.append({
                    'role': 'assistant',
                    'content': response_text,
                    'timestamp': datetime.now().isoformat(),
                    'citations': citations,
                    'time_context': time_context
                })
                
                st.rerun()
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.briefing_chat_history = []
        st.session_state.briefing_chat_context = {}
        st.rerun()

def show_students():
    """Show students page"""
    st.title("👥 Students")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        class_filter = st.selectbox("Class", ["All"] + [f"{i}{j}" for i in range(7, 12) for j in ["A", "B"]])
    with col2:
        year_filter = st.selectbox("Year", ["All"] + [str(i) for i in range(7, 12)])
    with col3:
        campus_filter = st.selectbox("Campus", ["All", "A", "B"])
    with col4:
        support_filter = st.selectbox("Support Level", ["All", "0", "1", "2", "3"])
    
    # Build query params
    params = {}
    if class_filter != "All":
        params["class_code"] = class_filter
    if year_filter != "All":
        params["year_group"] = year_filter
    if campus_filter != "All":
        params["campus"] = campus_filter
    if support_filter != "All":
        params["support_level"] = int(support_filter)
    
    # Fetch students
    students_data = fetch_api("/api/students/", params)
    
    if not students_data:
        st.warning("Could not load students data")
        return
    
    if students_data:
        # Convert to DataFrame
        df = pd.DataFrame(students_data)
        
        # Add support level color coding
        def support_color(level):
            colors = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴"}
            return colors.get(level, "⚪")
        
        df["Support"] = df["support_level"].apply(support_color)
        
        # Display table
        st.dataframe(
            df[["name", "class_code", "year_group", "campus", "Support", "support_notes"]],
            column_config={
                "name": "Student Name",
                "class_code": "Class",
                "year_group": "Year",
                "campus": "Campus",
                "Support": "Support Level",
                "support_notes": "Support Notes"
            },
            use_container_width=True
        )
        
        # Student details
        if len(df) > 0:
            selected_student = st.selectbox("Select student for details", df["name"])
            
            if selected_student:
                student_id = df[df["name"] == selected_student]["id"].iloc[0]
                student_detail = fetch_api(f"/api/students/{student_id}")
                
                if student_detail:
                    st.markdown("### Student Details")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Name:** {student_detail['name']}")
                        st.markdown(f"**Class:** {student_detail['class_code']}")
                        st.markdown(f"**Year:** {student_detail['year_group']}")
                        st.markdown(f"**Campus:** {student_detail['campus']}")
                    with col2:
                        st.markdown(f"**Support Level:** {student_detail['support_level']}")
                        if student_detail['support_notes']:
                            st.markdown(f"**Support Notes:** {student_detail['support_notes']}")
                        if student_detail['performance_trend']:
                            st.markdown(f"**Performance Trend:** {student_detail['performance_trend'].title()}")
                    
                    # Recent logs
                    if student_detail['logs']:
                        st.markdown("#### Recent Logs")
                        logs_df = pd.DataFrame(student_detail['logs'])
                        # Handle various timestamp formats
                        try:
                            logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], infer_datetime_format=True).dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            # Fallback to string representation if parsing fails
                            logs_df['timestamp'] = logs_df['timestamp'].astype(str)
                        st.dataframe(
                            logs_df[['timestamp', 'log_type', 'category', 'note']],
                            column_config={
                                "timestamp": "Date/Time",
                                "log_type": "Type",
                                "category": "Category",
                                "note": "Note"
                            },
                            use_container_width=True
                        )
                    
                    # Recent assessments
                    if student_detail['assessments']:
                        st.markdown("#### Recent Assessments")
                        assessments_df = pd.DataFrame(student_detail['assessments'])
                        # Handle various date formats
                        try:
                            assessments_df['date'] = pd.to_datetime(assessments_df['date'], infer_datetime_format=True).dt.strftime('%Y-%m-%d')
                        except:
                            # Fallback to string representation if parsing fails
                            assessments_df['date'] = assessments_df['date'].astype(str)
                        st.dataframe(
                            assessments_df[['date', 'assessment_type', 'subject', 'score', 'max_score', 'percentage']],
                            column_config={
                                "date": "Date",
                                "assessment_type": "Type",
                                "subject": "Subject",
                                "score": "Score",
                                "max_score": "Max Score",
                                "percentage": "Percentage"
                            },
                            use_container_width=True
                        )

def show_search():
    """Show search page"""
    st.title("🔍 Search")
    
    # Search input
    query = st.text_input("Enter search query", placeholder="Search for students, logs, assessments...")
    
    if query:
        # Search options
        col1, col2 = st.columns(2)
        with col1:
            include_students = st.checkbox("Students", value=True)
            include_logs = st.checkbox("Logs", value=True)
            include_assessments = st.checkbox("Assessments", value=True)
        with col2:
            include_communications = st.checkbox("Communications", value=True)
            limit = st.slider("Results limit", 5, 50, 10)
        
        # Build filters
        filters = []
        if include_students:
            filters.append("students")
        if include_logs:
            filters.append("logs")
        if include_assessments:
            filters.append("assessments")
        if include_communications:
            filters.append("communications")
        
        params = {
            "q": query,
            "limit": limit,
            "filters": ",".join(filters) if filters else ""
        }
        
        # Perform search
        search_results = fetch_api("/api/search/", params)
        
        if search_results and search_results.get("results"):
            st.markdown(f"### Found {search_results['total_count']} results ({search_results['search_time_ms']}ms)")
            
            for result in search_results['results']:
                with st.expander(f"**{result['title']}** ({result['type'].title()}) - Relevance: {result['relevance_score']:.2f}"):
                    st.markdown(f"**Source:** {result['source']}")
                    st.markdown(f"**Content:** {result['content']}")
                    
                    # Show metadata
                    if result['metadata']:
                        st.markdown("**Details:**")
                        for key, value in result['metadata'].items():
                            if key not in ['id', 'type'] and value:
                                st.markdown(f"- {key.replace('_', ' ').title()}: {value}")
        else:
            st.info("No results found")

def show_import():
    """Show import page"""
    st.title("📁 Import Data")
    
    tab1, tab2 = st.tabs(["Single File", "Directory"])
    
    with tab1:
        st.markdown("### Import Single File")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["xlsx", "xls", "pdf", "docx"],
            help="Supported formats: Excel (.xlsx, .xls), PDF (.pdf), Word (.docx)"
        )
        
        if uploaded_file:
            st.markdown(f"**File:** {uploaded_file.name}")
            
            # File type detection
            file_ext = uploaded_file.name.split('.')[-1].lower()
            if file_ext in ['xlsx', 'xls']:
                file_type = st.selectbox("File Type", ["Auto-detect", "Class List", "Assessment", "Timetable", "Other"])
            else:
                file_type = "Auto-detect"
            
            index_for_search = st.checkbox("Index for search", value=True)
            
            if st.button("Import File"):
                with st.spinner("Importing file..."):
                    # Prepare file for upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "file_type": file_type if file_type != "Auto-detect" else "",
                        "auto_detect": file_type == "Auto-detect",
                        "index_for_search": index_for_search
                    }
                    
                    try:
                        response = requests.post(f"{API_BASE}/api/import/file", files=files, data=data)
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            st.json(result['processed_data'])
                        else:
                            st.error(f"❌ Import failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    with tab2:
        st.markdown("### Import Directory")
        directory_path = st.text_input("Directory Path", placeholder="/path/to/your/files")
        file_pattern = st.text_input("File Pattern", value="*", help="Use wildcards like *.xlsx")
        
        if directory_path and os.path.exists(directory_path):
            st.markdown(f"**Directory exists:** {directory_path}")
            
            # List files that would be imported
            import glob
            pattern = os.path.join(directory_path, file_pattern)
            file_paths = glob.glob(pattern)
            allowed_extensions = ['.xlsx', '.xls', '.pdf', '.docx']
            file_paths = [f for f in file_paths if os.path.splitext(f)[1].lower() in allowed_extensions]
            
            if file_paths:
                st.markdown(f"**Found {len(file_paths)} files to import:**")
                for file_path in file_paths[:10]:  # Show first 10
                    st.markdown(f"- {os.path.basename(file_path)}")
                if len(file_paths) > 10:
                    st.markdown(f"... and {len(file_paths) - 10} more files")
                
                if st.button("Import Directory"):
                    with st.spinner("Importing files..."):
                        try:
                            response = requests.post(
                                f"{API_BASE}/api/import/directory",
                                params={
                                    "directory_path": directory_path,
                                    "file_pattern": file_pattern,
                                    "auto_detect": True,
                                    "index_for_search": True
                                }
                            )
                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"✅ {result['message']}")
                                
                                # Show results
                                successful = sum(1 for r in result['results'] if r['success'])
                                st.metric("Successful", successful)
                                st.metric("Failed", len(result['results']) - successful)
                                
                                # Show details for failed imports
                                failed_results = [r for r in result['results'] if not r['success']]
                                if failed_results:
                                    st.markdown("#### Failed Imports:")
                                    for failed in failed_results:
                                        st.markdown(f"- **{failed['file_name']}**: {failed['message']}")
                            else:
                                st.error(f"❌ Import failed: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
            else:
                st.warning("No supported files found in directory")
        elif directory_path:
            st.error("Directory does not exist")

def show_settings():
    """Show settings page"""
    st.title("⚙️ Settings")

    # System status
    st.markdown("## System Status")

    health = fetch_api("/health")
    if health:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("API Status", health['status'])
        with col2:
            st.metric("Database", health['database'])
        with col3:
            st.metric("Version", health['version'])

    # Search index status
    st.markdown("## Search Index Status")

    index_status = fetch_api("/api/search/index/status")
    if index_status:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Index Status", index_status['status'])
            st.metric("Total Items", index_status['total_items'])
        with col2:
            st.markdown("**Collections:**")
            for name, info in index_status['collections'].items():
                st.markdown(f"- {name}: {info['count']} items ({info['status']})")

        if st.button("Rebuild Search Index"):
            with st.spinner("Rebuilding index..."):
                try:
                    response = requests.post(f"{API_BASE}/api/search/index/rebuild")
                    if response.status_code == 200:
                        st.success("✅ Search index rebuilt successfully")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to rebuild index: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # Import status
    st.markdown("## Import Status")

    import_status = fetch_api("/api/import/status")
    if import_status:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Database Records:**")
            for table, count in import_status['database_status'].items():
                st.markdown(f"- {table.title()}: {count}")
        with col2:
            st.metric("Processed Files", import_status['processed_files'])

def show_agents():
    """Show AI Agents page"""
    st.title("🤖 AI Teacher Tools")

    # Get available agents
    agents_data = fetch_api("/api/agents/available")

    if not agents_data:
        st.warning("Could not load agents data")
        return

    if agents_data and agents_data.get('agents'):
        st.markdown("## Available AI Agents")
        st.markdown(f"**Total Agents:** {agents_data.get('total', 0)}")

        # Organize agents by category dynamically
        categories = {}
        for agent in agents_data['agents']:
            category = agent.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(agent)

        # Create tabs for different agent categories
        if categories:
            tabs = st.tabs(list(categories.keys()))

            for i, (category, agents_in_category) in enumerate(categories.items()):
                with tabs[i]:
                    st.markdown(f"### {category}")

                    for agent in agents_in_category:
                        agent_id = agent['id']
                        with st.expander(f"🔧 {agent['name']}"):
                            st.markdown(f"**Description:** {agent['description']}")
                            if agent.get('model'):
                                st.markdown(f"**Model:** {agent['model']}")
                            if agent.get('capabilities'):
                                st.markdown(f"**Capabilities:** {', '.join(agent['capabilities'])}")

                            # Agent-specific interfaces
                            if agent_id == "at-risk-identifier":
                                show_at_risk_agent()
                            elif agent_id == "behavior-manager":
                                show_behavior_agent()
                            elif agent_id == "learning-path-creator":
                                show_learning_path_agent()
                            elif agent_id == "lesson_planner" or "lesson" in agent_id.lower():
                                show_lesson_planner_agent()
                            elif agent_id == "assessment_generator" or "assessment" in agent_id.lower():
                                show_assessment_generator_agent()
                            elif agent_id == "feedback_composer" or "feedback" in agent_id.lower():
                                show_feedback_composer_agent()
                            elif agent_id == "curriculum_advisor" or "curriculum" in agent_id.lower():
                                show_curriculum_advisor_agent()
                            elif agent_id == "differentiation_specialist" or "differentiation" in agent_id.lower():
                                show_differentiation_specialist_agent()
                            else:
                                # Generic agent info for agents without specific UI
                                st.info(f"This agent is registered and ready to use via the API.")
                                if agent.get('endpoints'):
                                    st.markdown("**API Endpoints:**")
                                    for endpoint in agent['endpoints']:
                                        st.code(f"{endpoint.get('method', 'N/A')} {endpoint.get('path', 'N/A')}", language="text")

    # Agent health status
    st.markdown("## Agent Health Status")
    health = fetch_api("/api/agents/health")

    if health:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Agents", health['total_agents'])
        with col2:
            st.metric("Healthy Agents", health['healthy_agents'])

        # Show individual agent status
        st.markdown("**Agent Status:**")
        for agent_name, status in health.get('agents', {}).items():
            if status == "healthy":
                st.success(f"✅ {agent_name}: {status}")
            else:
                st.error(f"❌ {agent_name}: {status}")

def get_available_classes():
    """Get list of available classes from the database"""
    students_data = fetch_api("/api/students/")
    if students_data:
        # Extract unique class codes and sort them
        classes = sorted(list(set([s.get('class_code', '') for s in students_data if s.get('class_code')])))
        return classes if classes else ["No classes found"]
    return ["No classes found"]

def show_at_risk_agent():
    """Show At-Risk Student Identification interface"""
    st.markdown("#### 🛡️ At-Risk Student Identification")

    analysis_type = st.selectbox(
        "Analysis Type",
        ["Individual Student", "Class Analysis", "System Overview"],
        key="at_risk_type"
    )

    if analysis_type == "Individual Student":
        # Get student list for selection
        students_data = fetch_api("/api/students/")
        if students_data:
            student_names = [s['name'] for s in students_data]
            selected_student = st.selectbox("Select Student", student_names, key="at_risk_student")

            if selected_student and st.button("Analyze Student", key="at_risk_analyze"):
                # Find student ID
                student_id = next(s['id'] for s in students_data if s['name'] == selected_student)

                # Call at-risk analysis API
                analysis_request = {
                    "student_id": student_id,
                    "analysis_type": "individual"
                }

                try:
                    response = requests.post(f"{API_BASE}/api/agents/at-risk/analyze", json=analysis_request)
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis Complete!")
                        st.text_area("Analysis Result", result['result'], height=200)
                    else:
                        st.error(f"❌ Analysis failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    elif analysis_type == "Class Analysis":
        # Get class list dynamically from database
        available_classes = get_available_classes()
        class_filter = st.selectbox("Select Class", available_classes, key="at_risk_class")

        if st.button("Analyze Class", key="at_risk_class_analyze"):
            analysis_request = {
                "class_code": class_filter,
                "analysis_type": "class"
            }

            try:
                response = requests.post(f"{API_BASE}/api/agents/at-risk/analyze", json=analysis_request)
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Class Analysis Complete!")
                    st.text_area("Class Analysis", result['result'], height=300)
                else:
                    st.error(f"❌ Analysis failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    else:  # System Overview
        if st.button("Generate System Overview", key="at_risk_system"):
            analysis_request = {
                "analysis_type": "system"
            }

            try:
                response = requests.post(f"{API_BASE}/api/agents/at-risk/analyze", json=analysis_request)
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ System Overview Complete!")
                    st.text_area("System Overview", result['result'], height=250)
                else:
                    st.error(f"❌ Analysis failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_behavior_agent():
    """Show Classroom Behavior Management interface"""
    st.markdown("#### 📊 Classroom Behavior Management")

    # Get class list dynamically from database
    available_classes = get_available_classes()
    class_filter = st.selectbox("Select Class", available_classes, key="behavior_class")

    analysis_type = st.radio(
        "Analysis Type",
        ["Comprehensive Analysis", "Behavior Insights", "Trends Only"],
        key="behavior_type"
    )

    if st.button("Analyze Behavior", key="behavior_analyze"):
        request_data = {
            "class_code": class_filter,
            "analysis_type": "comprehensive" if analysis_type == "Comprehensive Analysis" else "insights"
        }

        try:
            response = requests.post(f"{API_BASE}/api/agents/behavior/analyze", json=request_data)
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Behavior Analysis Complete!")
                st.text_area("Behavior Analysis", result['result'], height=300)
            else:
                st.error(f"❌ Analysis failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

def show_learning_path_agent():
    """Show Personalized Learning Path interface"""
    st.markdown("#### 🎯 Personalized Learning Path Creator")

    path_type = st.selectbox(
        "Path Type",
        ["Individual Student", "Class Overview"],
        key="learning_path_type"
    )

    if path_type == "Individual Student":
        # Get student list for selection
        students_data = fetch_api("/api/students/")
        if students_data:
            student_names = [s['name'] for s in students_data]
            selected_student = st.selectbox("Select Student", student_names, key="learning_path_student")

            if selected_student and st.button("Create Learning Path", key="learning_path_create"):
                # Find student ID
                student_id = next(s['id'] for s in students_data if s['name'] == selected_student)

                # Call learning path API
                path_request = {
                    "student_id": student_id,
                    "path_type": "individual"
                }

                try:
                    response = requests.post(f"{API_BASE}/api/agents/learning-path/create", json=path_request)
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Learning Path Created!")
                        st.text_area("Learning Path", result['result'], height=400)
                    else:
                        st.error(f"❌ Learning path creation failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    else:  # Class Overview
        # Get class list dynamically from database
        available_classes = get_available_classes()
        class_filter = st.selectbox("Select Class", available_classes, key="learning_path_class")

        if st.button("Analyze Class Learning Paths", key="learning_path_class_analyze"):
            path_request = {
                "class_code": class_filter,
                "path_type": "class"
            }

            try:
                response = requests.post(f"{API_BASE}/api/agents/learning-path/create", json=path_request)
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Class Analysis Complete!")
                    st.text_area("Class Learning Analysis", result['result'], height=300)
                else:
                    st.error(f"❌ Analysis failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_lesson_planner_agent():
    """Show Lesson Planning Assistant interface"""
    st.markdown("#### 📚 Lesson Planning Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject", placeholder="e.g., Mathematics, Science", key="lesson_subject")
        topic = st.text_input("Topic", placeholder="e.g., Fractions, Photosynthesis", key="lesson_topic")
        grade_level = st.selectbox("Grade Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11"], key="lesson_grade")
    
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=15, max_value=180, value=45, step=15, key="lesson_duration")
        lesson_type = st.selectbox("Lesson Type", ["Introduction", "Practice", "Assessment", "Review", "Project-Based"], key="lesson_type")
    
    learning_objectives = st.text_area("Learning Objectives (optional)", 
                                       placeholder="What should students learn?", 
                                       height=100, 
                                       key="lesson_objectives")
    
    if st.button("Generate Lesson Plan", key="lesson_plan_generate", type="primary"):
        if subject and topic:
            with st.spinner("Creating lesson plan..."):
                request_data = {
                    "subject": subject,
                    "topic": topic,
                    "grade_level": grade_level,
                    "duration": duration,
                    "lesson_type": lesson_type,
                    "objectives": learning_objectives
                }
                
                try:
                    # Using orchestration API
                    response = requests.post(
                        f"{API_BASE}/api/orchestration/execute",
                        json={
                            "agent_id": "lesson_planner",
                            "task_type": "create_lesson_plan",
                            "input_data": request_data
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Lesson Plan Created!")
                        
                        # Display result
                        if 'output' in result and 'result' in result['output']:
                            st.markdown("### 📝 Lesson Plan")
                            st.markdown(result['output']['result'])
                        elif 'result' in result:
                            st.markdown("### 📝 Lesson Plan")
                            st.markdown(result['result'])
                        else:
                            st.json(result)
                        
                        # Show metadata if available
                        if 'execution_time_ms' in result:
                            st.caption(f"Generated in {result['execution_time_ms']}ms")
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter both subject and topic")

def show_assessment_generator_agent():
    """Show Assessment Generator interface"""
    st.markdown("#### 📝 Assessment Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject", placeholder="e.g., History, Chemistry", key="assessment_subject")
        topic = st.text_input("Topic", placeholder="e.g., World War II, Chemical Bonds", key="assessment_topic")
        grade_level = st.selectbox("Grade Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11"], key="assessment_grade")
    
    with col2:
        assessment_type = st.selectbox("Assessment Type", 
                                       ["Multiple Choice", "Short Answer", "Essay", "Mixed", "Project Rubric"], 
                                       key="assessment_type")
        question_count = st.number_input("Number of Questions", min_value=1, max_value=50, value=10, key="question_count")
        difficulty = st.select_slider("Difficulty Level", 
                                     options=["Easy", "Medium", "Hard", "Mixed"], 
                                     value="Medium", 
                                     key="difficulty")
    
    include_rubric = st.checkbox("Include Grading Rubric", value=True, key="include_rubric")
    
    if st.button("Generate Assessment", key="assessment_generate", type="primary"):
        if subject and topic:
            with st.spinner("Generating assessment..."):
                request_data = {
                    "subject": subject,
                    "topic": topic,
                    "grade_level": grade_level,
                    "assessment_type": assessment_type,
                    "question_count": question_count,
                    "difficulty": difficulty,
                    "include_rubric": include_rubric
                }
                
                try:
                    response = requests.post(
                        f"{API_BASE}/api/orchestration/execute",
                        json={
                            "agent_id": "assessment_generator",
                            "task_type": "generate_questions",
                            "input_data": request_data
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Assessment Generated!")
                        
                        if 'output' in result and 'result' in result['output']:
                            st.markdown("### 📋 Assessment")
                            st.markdown(result['output']['result'])
                        elif 'result' in result:
                            st.markdown("### 📋 Assessment")
                            st.markdown(result['result'])
                        else:
                            st.json(result)
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter both subject and topic")

def show_feedback_composer_agent():
    """Show Feedback Composer interface"""
    st.markdown("#### 💬 Feedback Composer")
    
    # Student selection
    students_data = fetch_api("/api/students/")
    if students_data:
        col1, col2 = st.columns(2)
        
        with col1:
            student_names = [s['name'] for s in students_data]
            selected_student = st.selectbox("Select Student", student_names, key="feedback_student")
        
        with col2:
            feedback_type = st.selectbox("Feedback Type", 
                                        ["Assignment", "Assessment", "Behavior", "Progress Report", "General"], 
                                        key="feedback_type")
        
        # Context inputs
        assignment_name = st.text_input("Assignment/Assessment Name", 
                                       placeholder="e.g., Chapter 5 Quiz, Science Project", 
                                       key="assignment_name")
        
        col3, col4 = st.columns(2)
        with col3:
            performance_level = st.select_slider("Performance Level", 
                                                options=["Below Expectations", "Approaching", "Meeting", "Exceeding"], 
                                                value="Meeting", 
                                                key="performance")
        with col4:
            tone = st.selectbox("Tone", ["Encouraging", "Professional", "Constructive", "Celebratory"], key="tone")
        
        additional_notes = st.text_area("Additional Notes/Context", 
                                       placeholder="Any specific points to address?", 
                                       height=100, 
                                       key="feedback_notes")
        
        if st.button("Compose Feedback", key="feedback_compose", type="primary"):
            student_id = next(s['id'] for s in students_data if s['name'] == selected_student)
            
            with st.spinner("Composing personalized feedback..."):
                request_data = {
                    "student_id": student_id,
                    "student_name": selected_student,
                    "feedback_type": feedback_type,
                    "assignment_name": assignment_name,
                    "performance_level": performance_level,
                    "tone": tone,
                    "additional_notes": additional_notes
                }
                
                try:
                    response = requests.post(
                        f"{API_BASE}/api/orchestration/execute",
                        json={
                            "agent_id": "feedback_composer",
                            "task_type": "compose_feedback",
                            "input_data": request_data
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Feedback Composed!")
                        
                        if 'output' in result and 'result' in result['output']:
                            st.markdown("### 📨 Personalized Feedback")
                            feedback_text = result['output']['result']
                            st.text_area("Feedback (editable)", feedback_text, height=300, key="feedback_output")
                            
                            # Copy button
                            if st.button("📋 Copy to Clipboard", key="copy_feedback"):
                                st.info("Feedback copied! (Paste where needed)")
                        elif 'result' in result:
                            st.markdown("### 📨 Personalized Feedback")
                            st.text_area("Feedback (editable)", result['result'], height=300, key="feedback_output2")
                        else:
                            st.json(result)
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    else:
        st.warning("Could not load student data")

def show_curriculum_advisor_agent():
    """Show Curriculum Advisor interface"""
    st.markdown("#### 🗺️ Curriculum Advisor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject", placeholder="e.g., Mathematics, English", key="curriculum_subject")
        grade_level = st.selectbox("Grade Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11"], key="curriculum_grade")
    
    with col2:
        time_period = st.selectbox("Planning Period", 
                                  ["One Week", "One Month", "One Quarter", "One Semester", "Full Year"], 
                                  key="time_period")
        focus_area = st.text_input("Focus Area (optional)", 
                                  placeholder="e.g., Reading Comprehension, Algebra", 
                                  key="focus_area")
    
    current_standards = st.text_area("Current Standards/Requirements (optional)", 
                                    placeholder="List any specific standards to address", 
                                    height=100, 
                                    key="standards")
    
    advice_type = st.radio("What do you need?", 
                          ["Complete Curriculum Plan", "Topic Sequencing", "Resource Recommendations", "Standards Alignment"], 
                          key="advice_type")
    
    if st.button("Get Curriculum Advice", key="curriculum_advice", type="primary"):
        if subject:
            with st.spinner("Analyzing curriculum needs..."):
                request_data = {
                    "subject": subject,
                    "grade_level": grade_level,
                    "time_period": time_period,
                    "focus_area": focus_area,
                    "standards": current_standards,
                    "advice_type": advice_type
                }
                
                try:
                    response = requests.post(
                        f"{API_BASE}/api/orchestration/execute",
                        json={
                            "agent_id": "curriculum_advisor",
                            "task_type": "suggest_curriculum",
                            "input_data": request_data
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Curriculum Plan Generated!")
                        
                        if 'output' in result and 'result' in result['output']:
                            st.markdown("### 📚 Curriculum Recommendations")
                            st.markdown(result['output']['result'])
                        elif 'result' in result:
                            st.markdown("### 📚 Curriculum Recommendations")
                            st.markdown(result['result'])
                        else:
                            st.json(result)
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter a subject")

def show_differentiation_specialist_agent():
    """Show Differentiation Specialist interface"""
    st.markdown("#### 🎨 Differentiation Specialist")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject", placeholder="e.g., Science, History", key="diff_subject")
        topic = st.text_input("Topic/Lesson", placeholder="e.g., Cell Division, Ancient Rome", key="diff_topic")
        grade_level = st.selectbox("Grade Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11"], key="diff_grade")
    
    with col2:
        differentiation_type = st.selectbox("Differentiation Focus", 
                                          ["Content", "Process", "Product", "All Three"], 
                                          key="diff_type")
        student_need = st.multiselect("Student Needs", 
                                     ["Below Grade Level", "On Grade Level", "Above Grade Level", 
                                      "English Language Learners", "Special Education", "Gifted/Talented"],
                                     default=["Below Grade Level", "On Grade Level", "Above Grade Level"],
                                     key="student_needs")
    
    learning_styles = st.multiselect("Learning Styles to Address", 
                                    ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"],
                                    default=["Visual", "Auditory", "Kinesthetic"],
                                    key="learning_styles")
    
    specific_challenges = st.text_area("Specific Challenges/Context", 
                                      placeholder="Describe any specific challenges or needs", 
                                      height=100, 
                                      key="challenges")
    
    if st.button("Generate Differentiation Strategies", key="diff_generate", type="primary"):
        if subject and topic:
            with st.spinner("Creating differentiated materials..."):
                request_data = {
                    "subject": subject,
                    "topic": topic,
                    "grade_level": grade_level,
                    "differentiation_type": differentiation_type,
                    "student_needs": student_need,
                    "learning_styles": learning_styles,
                    "challenges": specific_challenges
                }
                
                try:
                    response = requests.post(
                        f"{API_BASE}/api/orchestration/execute",
                        json={
                            "agent_id": "differentiation_specialist",
                            "task_type": "differentiate_instruction",
                            "input_data": request_data
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Differentiation Strategies Generated!")
                        
                        if 'output' in result and 'result' in result['output']:
                            st.markdown("### 🎯 Differentiated Instruction Plan")
                            st.markdown(result['output']['result'])
                        elif 'result' in result:
                            st.markdown("### 🎯 Differentiated Instruction Plan")
                            st.markdown(result['result'])
                        else:
                            st.json(result)
                    else:
                        st.error(f"❌ Failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter both subject and topic")

def show_classroom_tools():
    """Show Classroom Management Tools page"""
    st.title("📊 Classroom Management Tools")
    st.markdown("Data-driven tools to support classroom management and student interventions")
    
    # Create tabs for different tools
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚨 Intervention Priority",
        "📈 Progress Dashboard",
        "🪑 Seating Chart",
        "👥 Group Formation",
        "🎯 Differentiation"
    ])
    
    with tab1:
        show_intervention_priority()
    
    with tab2:
        show_progress_dashboard()
    
    with tab3:
        show_seating_chart()
    
    with tab4:
        show_group_formation()
    
    with tab5:
        show_differentiation_support()

def show_cca_comments():
    """Show CCA Comments Management page"""
    st.title("🎵 CCA Comments")
    st.markdown("Manage Co-Curricular Activities behavior comments for students")
    
    # Two-column layout: Search/List on left, Comment Manager on right
    col_main, col_detail = st.columns([1, 2])
    
    with col_main:
        st.markdown("### 🔍 Student Search")
        
        # Search input
        search_query = st.text_input(
            "Search by name or form",
            placeholder="e.g., Emma or 4B",
            key="cca_search"
        )
        
        # Fetch students
        params = {"q": search_query} if search_query else {"q": ""}
        students_data = fetch_api("/api/cca/students/search", params)
        
        if not students_data:
            st.warning("Could not load students")
            return
        
        # Display students grouped by form
        if students_data.get('students_by_form'):
            st.markdown(f"**Found {students_data['total']} students**")
            
            # Session state for selected student
            if 'selected_cca_student' not in st.session_state:
                st.session_state.selected_cca_student = None
            
            for form, students in sorted(students_data['students_by_form'].items()):
                with st.expander(f"🎫 {form} ({len(students)} students)", expanded=len(students_data['students_by_form']) <= 2):
                    for student in students:
                        # Student button with comment count
                        comment_indicator = f" 📝 {student['comment_count']}" if student['comment_count'] > 0 else ""
                        
                        if st.button(
                            f"{student['name']}{comment_indicator}",
                            key=f"select_{student['id']}",
                            use_container_width=True
                        ):
                            st.session_state.selected_cca_student = student['id']
                            st.rerun()
        else:
            st.info("No students found")
        
        # CSV Import/Export section
        st.markdown("---")
        st.markdown("### 📊 Data Management")
        
        # CSV Import
        uploaded_file = st.file_uploader(
            "Import CCA Comments CSV",
            type=["csv"],
            help="Upload CSV file with CCA comments",
            key="cca_csv_upload"
        )
        
        if uploaded_file and st.button("⬆️ Import CSV", key="import_cca_csv"):
            with st.spinner("Importing CSV..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    response = requests.post(f"{API_BASE}/api/cca/import/csv", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Imported {result['imported']} comments")
                        if result['skipped'] > 0:
                            st.warning(f"Skipped {result['skipped']} rows")
                        if result.get('errors'):
                            with st.expander("View Errors"):
                                for error in result['errors']:
                                    st.text(error)
                        st.rerun()
                    else:
                        st.error(f"❌ Import failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # CSV Export
        if st.button("⬇️ Export to CSV", key="export_cca_csv"):
            with st.spinner("Generating CSV..."):
                try:
                    response = requests.get(f"{API_BASE}/api/cca/export/csv")
                    if response.status_code == 200:
                        result = response.json()
                        st.download_button(
                            label="💾 Download CSV",
                            data=result['csv_content'],
                            file_name=result['filename'],
                            mime="text/csv"
                        )
                    else:
                        st.error(f"❌ Export failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Right column: Comment Manager
    with col_detail:
        if st.session_state.selected_cca_student:
            show_cca_comment_manager(st.session_state.selected_cca_student)
        else:
            st.info("⬅️ Select a student from the list to manage their CCA comments")
            
            # Show CCA subjects info
            st.markdown("### 📋 Available CCA Subjects")
            subjects_data = fetch_api("/api/cca/subjects")
            if subjects_data and subjects_data.get('subjects'):
                cols = st.columns(3)
                for i, subject in enumerate(subjects_data['subjects']):
                    with cols[i % 3]:
                        st.markdown(f"• {subject}")

def show_cca_comment_manager(student_id: int):
    """Show comment manager for a selected student"""
    
    # Fetch student CCA comments
    comments_data = fetch_api(f"/api/cca/students/{student_id}/comments")
    
    if not comments_data:
        st.error("Could not load student comments")
        return
    
    # Student header
    st.markdown(f"## 🎯 {comments_data['student_name']}")
    st.markdown(f"**Form:** {comments_data['form']}")
    
    # Back button
    if st.button("← Back to Student List", key="back_to_list"):
        st.session_state.selected_cca_student = None
        st.rerun()
    
    st.markdown("---")
    
    # Display comments by subject
    comments_by_subject = comments_data.get('comments_by_subject', {})
    
    # Session state for dialog
    if 'cca_edit_dialog' not in st.session_state:
        st.session_state.cca_edit_dialog = None
    
    for subject, comment_data in comments_by_subject.items():
        with st.expander(f"📝 {subject}", expanded=comment_data is not None):
            if comment_data:
                # Display existing comment
                comment_type = comment_data['type']
                
                # Color code by type
                type_colors = {
                    'positive': '🟢',
                    'neutral': '🟡',
                    'concern': '🔴'
                }
                type_icon = type_colors.get(comment_type, '⚪')
                
                st.markdown(f"**Type:** {type_icon} {comment_type.title()}")
                st.markdown(f"**Comment:**")
                st.text_area(
                    "Comment",
                    value=comment_data['comment'],
                    height=100,
                    disabled=True,
                    key=f"view_{subject}",
                    label_visibility="collapsed"
                )
                st.caption(f"Last updated: {comment_data['timestamp'][:10]}")
                
                # Action buttons
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✏️ Edit", key=f"edit_{subject}", use_container_width=True):
                        st.session_state.cca_edit_dialog = {
                            'subject': subject,
                            'comment_id': comment_data['id'],
                            'comment': comment_data['comment'],
                            'type': comment_type,
                            'mode': 'edit'
                        }
                        st.rerun()
                with col_b:
                    if st.button("🗑️ Delete", key=f"delete_{subject}", use_container_width=True):
                        try:
                            response = requests.delete(f"{API_BASE}/api/cca/comments/{comment_data['id']}")
                            if response.status_code == 200:
                                st.success("Comment deleted")
                                st.rerun()
                            else:
                                st.error(f"Delete failed: {response.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                # No comment yet
                st.info("No comment for this subject")
                if st.button(f"➕ Add Comment", key=f"add_{subject}", use_container_width=True):
                    st.session_state.cca_edit_dialog = {
                        'subject': subject,
                        'comment_id': None,
                        'comment': '',
                        'type': 'neutral',
                        'mode': 'add'
                    }
                    st.rerun()
    
    # Edit/Add dialog
    if st.session_state.cca_edit_dialog:
        dialog_data = st.session_state.cca_edit_dialog
        
        st.markdown("---")
        st.markdown(f"### {'✏️ Edit' if dialog_data['mode'] == 'edit' else '➕ Add'} Comment - {dialog_data['subject']}")
        
        with st.form(key="cca_comment_form"):
            comment_text = st.text_area(
                "Comment",
                value=dialog_data['comment'],
                height=150,
                placeholder="Enter CCA comment..."
            )
            
            comment_type = st.selectbox(
                "Comment Type",
                options=['positive', 'neutral', 'concern'],
                index=['positive', 'neutral', 'concern'].index(dialog_data['type'])
            )
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button("✅ Save", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submitted and comment_text.strip():
                try:
                    if dialog_data['mode'] == 'edit':
                        # Update existing comment
                        response = requests.put(
                            f"{API_BASE}/api/cca/comments/{dialog_data['comment_id']}",
                            params={
                                "comment": comment_text,
                                "comment_type": comment_type
                            }
                        )
                    else:
                        # Create new comment
                        response = requests.post(
                            f"{API_BASE}/api/cca/comments",
                            json={
                                "student_id": student_id,
                                "cca_subject": dialog_data['subject'],
                                "comment": comment_text,
                                "comment_type": comment_type
                            }
                        )
                    
                    if response.status_code in [200, 201]:
                        st.success("✅ Comment saved!")
                        st.session_state.cca_edit_dialog = None
                        st.rerun()
                    else:
                        st.error(f"❌ Save failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            
            if cancelled:
                st.session_state.cca_edit_dialog = None
                st.rerun()

def show_differentiation_support():
    """Show Differentiation Decision Support"""
    st.markdown("### 🎯 Differentiation Decision Support")
    st.markdown("Identify students' learning levels and plan differentiated instruction based on assessment data")
    
    # Configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get available classes
        classes_data = fetch_api("/api/classroom-tools/classes")
        available_classes = []
        if classes_data and classes_data.get('classes'):
            available_classes = classes_data['classes']
        
        if not available_classes:
            st.warning("No classes found")
            return
        
        class_filter = st.selectbox("Select Class", available_classes, key="diff_class")
    
    with col2:
        subject_filter = st.text_input("Subject (optional)", placeholder="e.g., Math, English", key="diff_subject")
    
    # Analyze button
    if st.button("✨ Analyze Class for Differentiation", type="primary", key="analyze_diff"):
        params = {"class_code": class_filter}
        if subject_filter:
            params["subject"] = subject_filter
        
        with st.spinner("Analyzing student performance and learning needs..."):
            diff_data = fetch_api("/api/classroom-tools/differentiation-support", params)
        
        if not diff_data or diff_data.get('error'):
            st.error("Could not analyze class. Please try again.")
            return
        
        # Display results
        st.markdown("---")
        st.markdown(f"### 📊 Analysis Results for {diff_data['class_code']}")
        st.markdown(f"**Subject:** {diff_data['subject']}")
        
        # Summary metrics
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        with col_s1:
            st.metric("Total Students", diff_data['total_students'])
        with col_s2:
            st.metric("Extension", diff_data['summary']['extension_count'], help="Students ready for challenge")
        with col_s3:
            st.metric("On-Level", diff_data['summary']['on_level_count'], help="Meeting grade level")
        with col_s4:
            st.metric("Need Support", diff_data['summary']['support_count'], help="Below grade level")
        with col_s5:
            avg_score = diff_data['summary'].get('avg_class_score')
            st.metric("Class Avg", f"{avg_score}%" if avg_score else "N/A")
        
        st.markdown("---")
        
        # Suggested groupings for instruction
        st.markdown("## 🎯 Suggested Instructional Groups")
        
        if diff_data.get('suggested_groups'):
            for group in diff_data['suggested_groups']:
                # Color code by level
                level_colors = {
                    "extension": "🟢",
                    "on_level": "🟡",
                    "support": "🟠",
                    "high_support": "🔴"
                }
                icon = level_colors.get(group['level'], "⚪")
                
                with st.expander(
                    f"{icon} {group['group_name']} ({group['student_count']} students)",
                    expanded=True
                ):
                    st.markdown(f"**Focus:** {group['focus']}")
                    
                    # Students in group
                    st.markdown("**Students:**")
                    student_cols = st.columns(3)
                    for i, student_name in enumerate(group['students']):
                        with student_cols[i % 3]:
                            st.markdown(f"• {student_name}")
                    
                    # Teaching strategies
                    st.markdown("**Recommended Strategies:**")
                    for strategy in group['strategies']:
                        st.markdown(f"✅ {strategy}")
        else:
            st.info("No groupings could be generated (insufficient assessment data)")
        
        st.markdown("---")
        
        # Detailed student breakdown
        st.markdown("## 📝 Individual Student Details")
        
        # Create tabs for each performance level
        detail_tabs = st.tabs([
            f"🟢 Extension ({diff_data['summary']['extension_count']})",
            f"🟡 On-Level ({diff_data['summary']['on_level_count']})",
            f"🔴 Need Support ({diff_data['summary']['support_count']})"
        ])
        
        # Extension students
        with detail_tabs[0]:
            extension_students = diff_data['students_by_level']['extension']
            if extension_students:
                for student in extension_students:
                    with st.expander(f"{student['student_name']} - Avg: {student['avg_score']}%"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**Average Score:** {student['avg_score']}%")
                            st.markdown(f"**Trend:** {student['trend'].replace('_', ' ').title()}")
                            st.markdown(f"**Assessments:** {student['assessment_count']}")
                        with col_b:
                            st.markdown("**Needs:**")
                            for need in student['needs']:
                                st.markdown(f"- {need}")
                        
                        st.markdown("**Recommendations:**")
                        for rec in student['recommendations']:
                            st.markdown(f"• {rec}")
            else:
                st.info("No students at extension level")
        
        # On-level students
        with detail_tabs[1]:
            on_level_students = diff_data['students_by_level']['on_level']
            if on_level_students:
                for student in on_level_students:
                    with st.expander(f"{student['student_name']} - Avg: {student['avg_score']}%"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**Average Score:** {student['avg_score']}%")
                            st.markdown(f"**Trend:** {student['trend'].replace('_', ' ').title()}")
                            st.markdown(f"**Assessments:** {student['assessment_count']}")
                        with col_b:
                            st.markdown("**Needs:**")
                            for need in student['needs']:
                                st.markdown(f"- {need}")
                        
                        st.markdown("**Recommendations:**")
                        for rec in student['recommendations']:
                            st.markdown(f"• {rec}")
            else:
                st.info("No students at on-level")
        
        # Support needed students
        with detail_tabs[2]:
            support_students = diff_data['students_by_level']['support_needed']
            if support_students:
                for student in support_students:
                    # Highlight urgent cases
                    is_urgent = "declining" in student['trend'] or student['support_level'] >= 2
                    name_display = f"⚠️ {student['student_name']}" if is_urgent else student['student_name']
                    
                    with st.expander(f"{name_display} - Avg: {student['avg_score'] or 'N/A'}%"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown(f"**Average Score:** {student['avg_score'] or 'No data'}%")
                            st.markdown(f"**Trend:** {student['trend'].replace('_', ' ').title()}")
                            st.markdown(f"**Support Level:** {student['support_level']}")
                            st.markdown(f"**Assessments:** {student['assessment_count']}")
                        with col_b:
                            st.markdown("**Needs:**")
                            for need in student['needs']:
                                if "Declining" in need or "High support" in need:
                                    st.error(need)
                                else:
                                    st.markdown(f"- {need}")
                        
                        if student.get('gaps'):
                            st.markdown("**Specific Gaps:**")
                            for gap in student['gaps']:
                                st.markdown(f"• {gap}")
                        
                        st.markdown("**Recommendations:**")
                        for rec in student['recommendations']:
                            if "Urgent" in rec or "1-on-1" in rec:
                                st.warning(rec)
                            else:
                                st.markdown(f"• {rec}")
            else:
                st.success("No students currently need support!")
        
        # Export/Action buttons
        st.markdown("---")
        col_action1, col_action2 = st.columns(2)
        with col_action1:
            if st.button("📋 Copy Groups to Clipboard"):
                st.info("Copy functionality - Coming Soon")
        with col_action2:
            if st.button("📊 Export to CSV"):
                st.info("Export functionality - Coming Soon")

def show_seating_chart():
    """Show Seating Chart Optimizer"""
    st.markdown("### 🪑 Seating Chart Optimizer")
    st.markdown("Generate optimal seating arrangements based on behavior data, support needs, and learning patterns")
    
    # Configuration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Get available classes
        classes_data = fetch_api("/api/classroom-tools/classes")
        available_classes = []
        if classes_data and classes_data.get('classes'):
            available_classes = classes_data['classes']
        
        if not available_classes:
            st.warning("No classes found")
            return
        
        class_filter = st.selectbox("Select Class", available_classes, key="seating_class")
    
    with col2:
        rows = st.number_input("Rows", min_value=3, max_value=10, value=5, key="seating_rows")
    
    with col3:
        cols = st.number_input("Columns", min_value=3, max_value=10, value=6, key="seating_cols")
    
    with col4:
        strategy = st.selectbox(
            "Strategy",
            ["behavior_optimized", "support_distributed", "mixed_ability", "random"],
            format_func=lambda x: {
                "behavior_optimized": "Behavior Optimized",
                "support_distributed": "Support Distributed",
                "mixed_ability": "Mixed Ability",
                "random": "Random"
            }[x],
            key="seating_strategy"
        )
    
    # Strategy descriptions
    strategy_descriptions = {
        "behavior_optimized": "⚠️ Minimize behavioral conflicts - high-incident students at front/corners for monitoring",
        "support_distributed": "🫂 Distribute support needs evenly across the room for balanced teacher attention",
        "mixed_ability": "🎯 Mix high and low performers in snake pattern for peer learning",
        "random": "🎲 Random assignment for baseline comparison"
    }
    st.info(strategy_descriptions[strategy])
    
    # Generate button
    if st.button("✨ Generate Seating Chart", type="primary", key="generate_seating"):
        params = {
            "class_code": class_filter,
            "rows": rows,
            "cols": cols,
            "strategy": strategy
        }
        
        with st.spinner("Analyzing students and creating optimal seating arrangement..."):
            seating_data = fetch_api("/api/classroom-tools/seating-chart", params)
        
        if not seating_data or seating_data.get('error'):
            st.error("Could not generate seating chart. Please try again.")
            return
        
        # Display results
        st.markdown("---")
        st.markdown(f"### 📍 Seating Chart for {seating_data['class_code']}")
        st.markdown(f"**Strategy:** {strategy_descriptions[strategy]}")
        st.markdown(
            f"**Dimensions:** {seating_data['dimensions']['rows']} rows × "
            f"{seating_data['dimensions']['cols']} columns = "
            f"{seating_data['dimensions']['total_seats']} seats"
        )
        st.markdown(f"**Students:** {seating_data['student_count']} | **Empty Seats:** {seating_data['empty_seats']}")
        
        if seating_data.get('rationale'):
            st.success(f"✅ {seating_data['rationale']}")
        
        # Stats
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Total Support Needs", seating_data['stats']['total_support_needs'])
        with col_s2:
            st.metric("High Incident Students", seating_data['stats']['high_incident_count'])
        with col_s3:
            avg_support = sum(seating_data['stats']['support_per_row']) / len(seating_data['stats']['support_per_row'])
            st.metric("Avg Support per Row", f"{avg_support:.1f}")
        
        st.markdown("---")
        st.markdown("#### 🗺️ Seating Arrangement")
        st.markdown("**(Front of Classroom)**")
        
        # Display seating grid
        seating_grid = seating_data['seating_grid']
        
        # Create visual grid
        for row_idx, row in enumerate(seating_grid):
            cols_display = st.columns(len(row))
            
            for col_idx, seat in enumerate(row):
                with cols_display[col_idx]:
                    if seat is None:
                        # Empty seat
                        st.markdown(
                            f"<div style='padding: 10px; border: 1px dashed #ccc; "
                            f"border-radius: 5px; text-align: center; min-height: 80px; "
                            f"background-color: #f9f9f9;'>"
                            f"<span style='color: #ccc;'>— Empty —</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        # Student seat
                        # Color based on support level
                        support_colors = {
                            0: "#d4edda",  # Green - no support
                            1: "#fff3cd",  # Yellow - low support
                            2: "#ffe5cc",  # Orange - medium support
                            3: "#f8d7da"   # Red - high support
                        }
                        bg_color = support_colors.get(seat['support_level'], "#ffffff")
                        
                        # Border color for incidents
                        border_color = "#dc3545" if seat['has_incidents'] else "#6c757d"
                        border_width = "3px" if seat['has_incidents'] else "1px"
                        
                        # Format name
                        name_parts = seat['name'].split()
                        short_name = f"{name_parts[0][0]}. {name_parts[-1]}" if len(name_parts) > 1 else seat['name']
                        
                        # Behavior indicator
                        behavior_icon = "🟢" if seat['behavior_score'] >= 0 else "🔴"
                        
                        st.markdown(
                            f"<div style='padding: 8px; border: {border_width} solid {border_color}; "
                            f"border-radius: 5px; background-color: {bg_color}; "
                            f"min-height: 80px; text-align: center;'>"
                            f"<div style='font-weight: bold; font-size: 0.9em;'>{short_name}</div>"
                            f"<div style='font-size: 0.75em; margin-top: 4px;'>"
                            f"{behavior_icon} {seat['behavior_score']:+d} | "
                            f"Supp: {seat['support_level']}</div>"
                            f"<div style='font-size: 0.7em; color: #666;'>Avg: {seat['avg_score']}%</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
        
        st.markdown("---")
        
        # Legend
        st.markdown("#### 🏷️ Legend")
        col_l1, col_l2 = st.columns(2)
        
        with col_l1:
            st.markdown("**Background Colors (Support Level):**")
            st.markdown("🟢 Green = No support (0)")
            st.markdown("🟡 Yellow = Low support (1)")
            st.markdown("🟠 Orange = Medium support (2)")
            st.markdown("🔴 Red = High support (3)")
        
        with col_l2:
            st.markdown("**Indicators:**")
            st.markdown("🔴 Red border = High behavioral incidents (>5)")
            st.markdown("🟢 Green circle = Positive behavior score")
            st.markdown("🔴 Red circle = Negative behavior score")
            st.markdown("Supp = Support level | Avg = Assessment average")
        
        # Support per row breakdown
        with st.expander("📊 Support Distribution by Row", expanded=False):
            row_labels = [f"Row {i+1}" for i in range(len(seating_data['stats']['support_per_row']))]
            support_df = pd.DataFrame({
                'Row': row_labels,
                'Total Support Level': seating_data['stats']['support_per_row']
            })
            st.bar_chart(support_df.set_index('Row'))
        
        # Export options
        st.markdown("---")
        col_action1, col_action2, col_action3 = st.columns(3)
        with col_action1:
            if st.button("📝 Copy to Clipboard"):
                st.info("Copy functionality - Coming Soon")
        with col_action2:
            if st.button("🖨️ Print Seating Chart"):
                st.info("Print functionality - Coming Soon")
        with col_action3:
            if st.button("💾 Save Layout"):
                st.info("Save functionality - Coming Soon")

def show_group_formation():
    """Show Group Formation Tool"""
    st.markdown("### 👥 Student Group Formation")
    st.markdown("Generate optimal student groups based on assessment data, behavior patterns, and support needs")
    
    # Configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get available classes
        classes_data = fetch_api("/api/classroom-tools/classes")
        available_classes = []
        if classes_data and classes_data.get('classes'):
            available_classes = classes_data['classes']
        
        if not available_classes:
            st.warning("No classes found")
            return
        
        class_filter = st.selectbox("Select Class", available_classes, key="group_class")
    
    with col2:
        group_size = st.number_input("Group Size", min_value=2, max_value=10, value=4, key="group_size")
    
    with col3:
        strategy = st.selectbox(
            "Grouping Strategy",
            ["mixed_ability", "similar_ability", "behavioral_balance", "support_aware"],
            format_func=lambda x: {
                "mixed_ability": "Mixed Ability",
                "similar_ability": "Similar Ability",
                "behavioral_balance": "Behavioral Balance",
                "support_aware": "Support Aware"
            }[x],
            key="group_strategy"
        )
    
    # Strategy descriptions
    strategy_descriptions = {
        "mixed_ability": "🎯 Mix high and low performers to promote peer learning",
        "similar_ability": "📚 Group similar performers for targeted instruction",
        "behavioral_balance": "⚖️ Distribute behavioral dynamics evenly across groups",
        "support_aware": "🫂 Distribute support needs evenly for teacher management"
    }
    st.info(strategy_descriptions[strategy])
    
    # Generate groups button
    if st.button("✨ Generate Groups", type="primary", key="generate_groups"):
        # Fetch group formations
        params = {
            "class_code": class_filter,
            "group_size": group_size,
            "strategy": strategy
        }
        
        with st.spinner("Analyzing students and creating optimal groups..."):
            groups_data = fetch_api("/api/classroom-tools/group-formation", params)
        
        if not groups_data or groups_data.get('error'):
            st.error("Could not generate groups. Please try again.")
            return
        
        # Display results
        st.markdown("---")
        st.markdown(f"### 🎯 Generated Groups for {groups_data['class_code']}")
        st.markdown(f"**Strategy:** {strategy_descriptions[strategy]}")
        st.markdown(f"**Total Students:** {groups_data['total_students']} | **Groups Created:** {groups_data['num_groups']}")
        
        if groups_data.get('rationale'):
            st.success(f"✅ {groups_data['rationale']}")
        
        st.markdown("---")
        
        # Display each group
        for group in groups_data.get('groups', []):
            with st.expander(
                f"👥 Group {group['group_number']} - {group['group_stats']['size']} students "
                f"(Avg Score: {group['group_stats']['avg_assessment_score']}%)",
                expanded=True
            ):
                # Group statistics
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric(
                        "Avg Assessment Score",
                        f"{group['group_stats']['avg_assessment_score']}%"
                    )
                with col_stat2:
                    st.metric(
                        "Total Support Level",
                        group['group_stats']['total_support_level']
                    )
                with col_stat3:
                    st.metric(
                        "Avg Behavior Score",
                        f"+{group['group_stats']['avg_behavior_score']:.1f}" 
                        if group['group_stats']['avg_behavior_score'] >= 0 
                        else f"{group['group_stats']['avg_behavior_score']:.1f}"
                    )
                
                # Group members
                st.markdown("**Members:**")
                for member in group['members']:
                    # Color code support level
                    support_icon = {
                        0: "🟢",
                        1: "🟡",
                        2: "🟠",
                        3: "🔴"
                    }.get(member['support_level'], "⚪")
                    
                    behavior_icon = "🟢" if member['behavior_score'] >= 0 else "🔴"
                    
                    st.markdown(
                        f"{support_icon} **{member['name']}** - "
                        f"Avg: {member['avg_score']}% | "
                        f"Behavior: {behavior_icon} {member['behavior_score']:+d} | "
                        f"Support: Level {member['support_level']}"
                    )
        
        # Export/Print options
        st.markdown("---")
        col_action1, col_action2 = st.columns(2)
        with col_action1:
            if st.button("📝 Copy to Clipboard"):
                st.info("Copy functionality - Coming Soon")
        with col_action2:
            if st.button("📊 Export to CSV"):
                st.info("Export functionality - Coming Soon")

def show_progress_dashboard():
    """Show Progress Tracking Dashboard"""
    st.markdown("### 📈 Progress Tracking Dashboard")
    st.markdown("Visual analytics showing class and student progress over time")
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Get available classes
        classes_data = fetch_api("/api/classroom-tools/classes")
        available_classes = ["All Classes"]
        if classes_data and classes_data.get('classes'):
            available_classes.extend(classes_data['classes'])
        
        class_filter = st.selectbox("Select Class", available_classes, key="dashboard_class")
    
    with col2:
        days = st.selectbox("Time Period", [7, 14, 30, 60, 90], index=2, key="dashboard_days")
    
    with col3:
        behavior_filter = st.selectbox(
            "Behavior Type",
            ["All Behavior", "Classroom Only", "CCA Only"],
            key="dashboard_behavior_type"
        )
    
    with col4:
        if st.button("🔄 Refresh", key="dashboard_refresh"):
            st.rerun()
    
    # Fetch dashboard data
    params = {"days": days}
    if class_filter != "All Classes":
        params["class_code"] = class_filter
    
    # Map behavior filter to API parameter
    behavior_type_map = {
        "All Behavior": "all",
        "Classroom Only": "classroom",
        "CCA Only": "cca"
    }
    params["behavior_type"] = behavior_type_map.get(behavior_filter, "all")
    
    dashboard_data = fetch_api("/api/classroom-tools/progress-dashboard", params)
    
    if not dashboard_data or dashboard_data.get('error'):
        st.warning("Could not load dashboard data")
        return
    
    # Display summary metrics
    st.markdown("---")
    st.markdown(f"**{dashboard_data['class_code']}** | {dashboard_data['student_count']} students | Last {days} days")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric(
            "Net Behavior Score",
            dashboard_data['summary']['net_behavior_score'],
            delta=None
        )
    with col_b:
        st.metric(
            "Positive Logs",
            dashboard_data['summary']['total_positive_logs']
        )
    with col_c:
        st.metric(
            "Negative Logs",
            dashboard_data['summary']['total_negative_logs']
        )
    with col_d:
        avg_score = dashboard_data['summary'].get('average_class_score')
        st.metric(
            "Avg Assessment Score",
            f"{avg_score}%" if avg_score else "N/A"
        )
    
    st.markdown("---")
    
    # Behavior trend chart
    if dashboard_data.get('behavior_trend'):
        st.markdown("#### 📊 Behavior Trends Over Time")
        
        behavior_df = pd.DataFrame(dashboard_data['behavior_trend'])
        if not behavior_df.empty:
            behavior_df['date'] = pd.to_datetime(behavior_df['date'])
            behavior_df = behavior_df.set_index('date')
            
            # Create chart
            st.line_chart(behavior_df, use_container_width=True)
        else:
            st.info("No behavior data available for this period")
    
    st.markdown("---")
    
    # Assessment trend chart
    if dashboard_data.get('assessment_trend'):
        st.markdown("#### 📝 Assessment Score Trends")
        
        assessment_df = pd.DataFrame(dashboard_data['assessment_trend'])
        if not assessment_df.empty:
            assessment_df['date'] = pd.to_datetime(assessment_df['date'])
            assessment_df = assessment_df.set_index('date')
            
            # Remove date column if it exists
            numeric_cols = assessment_df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                st.line_chart(assessment_df[numeric_cols], use_container_width=True)
            else:
                st.info("No assessment data available for this period")
        else:
            st.info("No assessment data available for this period")
    
    st.markdown("---")
    
    # Support level distribution
    if dashboard_data.get('support_distribution'):
        st.markdown("#### 🎯 Support Level Distribution")
        
        support_dist = dashboard_data['support_distribution']
        support_labels = {0: "None (0)", 1: "Low (1)", 2: "Medium (2)", 3: "High (3)"}
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        cols = [col_s1, col_s2, col_s3, col_s4]
        
        for i, (level, count) in enumerate(sorted(support_dist.items())):
            with cols[i]:
                st.metric(support_labels.get(int(level), f"Level {level}"), count)
    
    st.markdown("---")
    
    # Top performers and needs attention
    col_perf, col_attn = st.columns(2)
    
    with col_perf:
        st.markdown("#### ⭐ Top Performers (Behavior)")
        if dashboard_data.get('top_performers'):
            for student in dashboard_data['top_performers'][:5]:
                if student['net_behavior'] > 0:
                    st.markdown(
                        f"**{student['student_name']}** ({student['class_code']}) - "
                        f"Net: +{student['net_behavior']} "
                        f"({student['positive_count']}+ / {student['negative_count']}-)"
                    )
        else:
            st.info("No data available")
    
    with col_attn:
        st.markdown("#### ⚠️ Needs Attention (Behavior)")
        if dashboard_data.get('needs_attention'):
            for student in dashboard_data['needs_attention'][:5]:
                st.markdown(
                    f"**{student['student_name']}** ({student['class_code']}) - "
                    f"Net: {student['net_behavior']} "
                    f"({student['positive_count']}+ / {student['negative_count']}-)"
                )
        else:
            st.success("No students currently need attention!")
    
    st.markdown("---")
    
    # Full student list with expandable details
    with st.expander("📋 All Students - Detailed View", expanded=False):
        if dashboard_data.get('student_summaries'):
            students_df = pd.DataFrame(dashboard_data['student_summaries'])
            st.dataframe(
                students_df[[
                    'student_name', 'class_code', 'positive_count', 
                    'negative_count', 'net_behavior', 'average_score', 'support_level'
                ]],
                column_config={
                    "student_name": "Student",
                    "class_code": "Class",
                    "positive_count": "Positive",
                    "negative_count": "Negative",
                    "net_behavior": "Net Score",
                    "average_score": "Avg %",
                    "support_level": "Support"
                },
                use_container_width=True
            )

def show_intervention_priority():
    """Show Intervention Priority List"""
    st.markdown("### 🚨 Students Needing Intervention")
    st.markdown("Prioritized list based on behavior patterns, assessment trends, and support needs")
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Get available classes
        classes_data = fetch_api("/api/classroom-tools/classes")
        available_classes = ["All Classes"]
        if classes_data and classes_data.get('classes'):
            available_classes.extend(classes_data['classes'])
        
        class_filter = st.selectbox("Filter by Class", available_classes, key="intervention_class")
    
    with col2:
        limit = st.number_input("Max Results", min_value=5, max_value=50, value=20, key="intervention_limit")
    
    with col3:
        behavior_filter = st.selectbox(
            "Behavior Type",
            ["All Behavior", "Classroom Only", "CCA Only"],
            key="intervention_behavior_type"
        )
    
    with col4:
        if st.button("🔄 Refresh", key="intervention_refresh"):
            st.rerun()
    
    # Fetch intervention data
    params = {"limit": limit}
    if class_filter != "All Classes":
        params["class_code"] = class_filter
    
    # Map behavior filter to API parameter
    behavior_type_map = {
        "All Behavior": "all",
        "Classroom Only": "classroom",
        "CCA Only": "cca"
    }
    params["behavior_type"] = behavior_type_map.get(behavior_filter, "all")
    
    intervention_data = fetch_api("/api/classroom-tools/intervention-priority", params)
    
    if not intervention_data:
        st.warning("Could not load intervention data")
        return
    
    # Display summary
    st.markdown(f"**Analysis Date:** {intervention_data.get('analysis_date', 'N/A')[:10]}")
    st.markdown(f"**Students Flagged:** {intervention_data.get('total_count', 0)}")
    
    if intervention_data.get('students'):
        st.markdown("---")
        
        # Display each student
        for i, student in enumerate(intervention_data['students'], 1):
            priority_score = student['priority_score']
            
            # Color code by priority
            if priority_score >= 50:
                priority_color = "🔴"
                priority_label = "URGENT"
            elif priority_score >= 30:
                priority_color = "🟠"
                priority_label = "HIGH"
            elif priority_score >= 15:
                priority_color = "🟡"
                priority_label = "MEDIUM"
            else:
                priority_color = "🟢"
                priority_label = "LOW"
            
            with st.expander(
                f"{priority_color} #{i} - {student['student_name']} ({student['class_code']}) - {priority_label} Priority",
                expanded=(i <= 3)  # Expand top 3
            ):
                # Student info
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Priority Score", f"{priority_score:.1f}")
                with col_b:
                    st.metric("Recent Incidents", student['recent_incidents'])
                with col_c:
                    days = student.get('days_since_positive')
                    st.metric("Days Since Positive", days if days is not None else "N/A")
                
                # Risk factors
                st.markdown("**Risk Factors:**")
                for factor in student['risk_factors']:
                    st.markdown(f"- {factor}")
                
                # Recommended actions
                st.markdown("**Recommended Actions:**")
                for action in student['recommended_actions']:
                    if "URGENT" in action:
                        st.error(f"⚠️ {action}")
                    else:
                        st.markdown(f"- {action}")
                
                # Quick action buttons
                st.markdown("---")
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    if st.button("View Student Details", key=f"view_{student['student_id']}"):
                        st.info(f"Navigate to student profile for {student['student_name']}")
                with col_y:
                    if st.button("Log Intervention", key=f"log_{student['student_id']}"):
                        st.info("Intervention logging - Coming Soon")
                with col_z:
                    if st.button("Contact Parent", key=f"contact_{student['student_id']}"):
                        st.info("Parent communication - Coming Soon")
        
        # Export option
        st.markdown("---")
        if st.button("📋 Export to CSV"):
            st.info("Export functionality - Coming Soon")
    else:
        st.success("✅ No students currently flagged for intervention!")

def show_ict_behavior():
    """Show ICT Behavior Management - Track strikes and positive behavior during lessons"""
    st.title("💻 ICT Behavior Management")
    st.markdown("**Real-time behavior tracking with automatic consequences for ICT lessons**")
    
    # Initialize session state
    if 'ict_session_id' not in st.session_state:
        st.session_state.ict_session_id = None
    if 'ict_class_code' not in st.session_state:
        st.session_state.ict_class_code = None
    if 'ict_lesson_active' not in st.session_state:
        st.session_state.ict_lesson_active = False
    
    # Check if lesson is active
    if not st.session_state.ict_lesson_active:
        # Lesson start interface
        st.markdown("### 🎬 Start a New Lesson")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            class_code = st.selectbox(
                "Select Class",
                ["7A", "7B", "8A", "8B", "9A", "9B", "10A", "10B", "11A", "11B"],
                key="ict_class_select"
            )
        
        with col2:
            if st.button("▶️ Start Lesson", type="primary", key="start_lesson"):
                with st.spinner("Starting lesson..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/api/ict-behavior/lesson/start",
                            json={"class_code": class_code}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.ict_session_id = result['session_id']
                            st.session_state.ict_class_code = result['class_code']
                            st.session_state.ict_lesson_active = True
                            st.success(f"✅ Lesson started for {result['student_count']} students!")
                            st.rerun()
                        else:
                            st.error(f"Failed to start lesson: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Information panel
        st.markdown("---")
        st.markdown("### ℹ️ How it Works")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("**Strike System**")
            st.markdown("- ⚠️ **Strike 1**: Verbal Warning")
            st.markdown("- ⚠️⚠️ **Strike 2**: Final Warning")
            st.markdown("- 🚫 **Strike 3**: Device Time-out")
        
        with col_b:
            st.markdown("**Positive Behavior**")
            st.markdown("- Award house points")
            st.markdown("- Track excellence")
            st.markdown("- Build positive culture")
        
        with col_c:
            st.markdown("**Admin Actions**")
            st.markdown("- Flag admin notification")
            st.markdown("- Mark HOD consultation")
            st.markdown("- Schedule parent meetings")
    
    else:
        # Active lesson interface
        session_id = st.session_state.ict_session_id
        class_code = st.session_state.ict_class_code
        
        # Header
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### 🟢 **ACTIVE LESSON** - Class {class_code}")
            st.caption(f"Session: {session_id}")
        
        with col2:
            if st.button("🔄 Refresh", key="refresh_lesson"):
                st.rerun()
        
        with col3:
            if st.button("⏹️ End Lesson", type="secondary", key="end_lesson"):
                with st.spinner("Ending lesson..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/api/ict-behavior/lesson/end",
                            params={"session_id": session_id}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Lesson ended. {result['total_logs']} logs archived.")
                            st.session_state.ict_lesson_active = False
                            st.session_state.ict_session_id = None
                            st.session_state.ict_class_code = None
                            st.rerun()
                        else:
                            st.error(f"Failed to end lesson: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        # Fetch current lesson state
        try:
            response = requests.get(
                f"{API_BASE}/api/ict-behavior/lesson/current",
                params={"session_id": session_id, "class_code": class_code}
            )
            
            if response.status_code == 200:
                lesson_data = response.json()
                students = lesson_data.get('students', [])
                
                # Summary metrics
                total_strikes = sum(s['current_strikes'] for s in students)
                total_positive = sum(s['positive_count'] for s in students)
                total_house_points = sum(s['total_house_points'] for s in students)
                
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    st.metric("Total Students", len(students))
                with col_m2:
                    st.metric("Total Strikes", total_strikes, delta=None, delta_color="inverse")
                with col_m3:
                    st.metric("Positive Behaviors", total_positive, delta=None, delta_color="normal")
                with col_m4:
                    st.metric("House Points Awarded", total_house_points)
                
                st.markdown("---")
                st.markdown("### 👥 Student Tracking")
                
                # Display students
                for student in students:
                    strikes = student['current_strikes']
                    
                    # Determine status indicator
                    if strikes == 0:
                        status_icon = "✅"
                        status_color = "normal"
                    elif strikes == 1:
                        status_icon = "⚠️"
                        status_color = "off"
                    elif strikes == 2:
                        status_icon = "⚠️⚠️"
                        status_color = "off"
                    else:
                        status_icon = "🚫"
                        status_color = "inverse"
                    
                    with st.expander(
                        f"{status_icon} {student['student_name']} ({student['house']}) - {strikes} strike(s) | +{student['positive_count']} positive",
                        expanded=(strikes >= 2)  # Auto-expand students with 2+ strikes
                    ):
                        # Quick action buttons
                        st.markdown("**Quick Actions:**")
                        
                        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                        
                        with col_s1:
                            if st.button("⚠️ Strike 1", key=f"strike1_{student['student_id']}", disabled=(strikes >= 3)):
                                st.session_state[f"strike_student_{student['student_id']}"] = 1
                                st.rerun()
                        
                        with col_s2:
                            if st.button("⚠️⚠️ Strike 2", key=f"strike2_{student['student_id']}", disabled=(strikes >= 3)):
                                st.session_state[f"strike_student_{student['student_id']}"] = 2
                                st.rerun()
                        
                        with col_s3:
                            if st.button("🚫 Strike 3", key=f"strike3_{student['student_id']}", disabled=(strikes >= 3)):
                                st.session_state[f"strike_student_{student['student_id']}"] = 3
                                st.rerun()
                        
                        with col_s4:
                            if st.button("✨ Positive", key=f"positive_{student['student_id']}", type="primary"):
                                st.session_state[f"positive_student_{student['student_id']}"] = True
                                st.rerun()
                        
                        # Handle strike logging
                        strike_key = f"strike_student_{student['student_id']}"
                        if strike_key in st.session_state:
                            strike_level = st.session_state[strike_key]
                            del st.session_state[strike_key]
                            
                            st.markdown("---")
                            st.markdown(f"**Log Strike {strike_level}:**")
                            
                            with st.form(key=f"strike_form_{student['student_id']}_{strike_level}"):
                                description = st.text_area(
                                    "Description",
                                    placeholder="Briefly describe the behavior...",
                                    key=f"strike_desc_{student['student_id']}_{strike_level}"
                                )
                                
                                col_f1, col_f2, col_f3 = st.columns(3)
                                
                                with col_f1:
                                    admin_notified = st.checkbox("Admin Notified", key=f"admin_{student['student_id']}")
                                with col_f2:
                                    hod_consulted = st.checkbox("HOD Consulted", key=f"hod_{student['student_id']}")
                                with col_f3:
                                    parent_meeting = st.checkbox("Parent Meeting", key=f"parent_{student['student_id']}")
                                
                                if st.form_submit_button("Log Strike", type="primary"):
                                    if not description.strip():
                                        st.error("Please provide a description")
                                    else:
                                        try:
                                            response = requests.post(
                                                f"{API_BASE}/api/ict-behavior/strike",
                                                params={"session_id": session_id},
                                                json={
                                                    "student_id": student['student_id'],
                                                    "class_code": class_code,
                                                    "description": description,
                                                    "strike_level": strike_level,
                                                    "admin_notified": admin_notified,
                                                    "hod_consulted": hod_consulted,
                                                    "parent_meeting_scheduled": parent_meeting
                                                }
                                            )
                                            
                                            if response.status_code == 200:
                                                result = response.json()
                                                st.success(f"✅ {result['message']}")
                                                st.rerun()
                                            else:
                                                st.error(f"Failed to log strike: {response.text}")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                        
                        # Handle positive logging
                        positive_key = f"positive_student_{student['student_id']}"
                        if positive_key in st.session_state:
                            del st.session_state[positive_key]
                            
                            st.markdown("---")
                            st.markdown("**Log Positive Behavior:**")
                            
                            with st.form(key=f"positive_form_{student['student_id']}"):
                                description = st.text_area(
                                    "Description",
                                    placeholder="What did they do well?",
                                    key=f"pos_desc_{student['student_id']}"
                                )
                                
                                house_points = st.number_input(
                                    "House Points",
                                    min_value=1,
                                    max_value=5,
                                    value=1,
                                    key=f"pos_points_{student['student_id']}"
                                )
                                
                                if st.form_submit_button("Award Points", type="primary"):
                                    if not description.strip():
                                        st.error("Please provide a description")
                                    else:
                                        try:
                                            response = requests.post(
                                                f"{API_BASE}/api/ict-behavior/positive",
                                                params={"session_id": session_id},
                                                json={
                                                    "student_id": student['student_id'],
                                                    "class_code": class_code,
                                                    "description": description,
                                                    "house_points": int(house_points)
                                                }
                                            )
                                            
                                            if response.status_code == 200:
                                                result = response.json()
                                                st.success(f"✅ {result['message']}")
                                                st.rerun()
                                            else:
                                                st.error(f"Failed to log positive: {response.text}")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                        
                        # Display strike history
                        if student['strike_history']:
                            st.markdown("---")
                            st.markdown("**Strike History (This Lesson):**")
                            
                            for strike in student['strike_history']:
                                st.markdown(f"- **Strike {strike['strike_level']}**: {strike['description']}")
                                st.caption(f"  {strike['consequence']} | {strike['timestamp'][:16]}")
                                
                                # Show admin flags
                                flags = []
                                if strike['admin_notified']:
                                    flags.append("👤 Admin")
                                if strike['hod_consulted']:
                                    flags.append("👔 HOD")
                                if strike['parent_meeting_scheduled']:
                                    flags.append("👪 Parent")
                                
                                if flags:
                                    st.caption(f"  Escalated: {' | '.join(flags)}")
            
            else:
                st.error(f"Failed to fetch lesson state: {response.text}")
        
        except Exception as e:
            st.error(f"Error fetching lesson state: {str(e)}")

def show_quiz_analytics():
    """Show Quiz Analytics - Upload CSVs and view performance trends"""
    st.markdown("## 📊 Quiz Analytics")
    st.markdown("Upload quiz results and track student performance over time")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Quiz", "📈 Performance Trends", "🎯 Progress Levels", "⚠️ At-Risk Students"])
    
    with tab1:
        st.markdown("### Upload Quiz Results")
        st.markdown("Supports CSV files from Quizizz, Google Forms, or any format with student names and scores")
        
        # Upload form
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subject = st.text_input("Subject", placeholder="e.g., Mathematics", key="quiz_subject")
        
        with col2:
            topic = st.text_input("Topic/Quiz Name", placeholder="e.g., Fractions Quiz", key="quiz_topic")
        
        with col3:
            quiz_date = st.date_input("Quiz Date", key="quiz_date")
        
        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=["csv"],
            help="CSV must contain student names and scores/percentages",
            key="quiz_csv_upload"
        )
        
        if uploaded_file and st.button("Process Quiz Results", type="primary", key="process_quiz"):
            with st.spinner("Processing quiz results..."):
                try:
                    # Prepare form data
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    data = {
                        "subject": subject or None,
                        "topic": topic or None,
                        "quiz_date": quiz_date.isoformat() if quiz_date else None
                    }
                    
                    # Upload to API
                    response = requests.post(
                        f"{API_BASE_URL}/api/quiz-analytics/upload",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success(f"✅ Successfully processed {result['records_inserted']} student records!")
                        
                        # Show summary
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Records Processed", result['records_processed'])
                        with col_b:
                            st.metric("Records Inserted", result['records_inserted'])
                        with col_c:
                            st.metric("Warnings", len(result['warnings']))
                        
                        # Show warnings if any
                        if result['warnings']:
                            with st.expander(f"⚠️ Warnings ({len(result['warnings'])})"):
                                for warning in result['warnings']:
                                    st.warning(warning)
                        
                        # Show errors if any
                        if result['errors']:
                            with st.expander(f"❌ Errors ({len(result['errors'])})", expanded=True):
                                for error in result['errors']:
                                    st.error(error)
                    else:
                        st.error(f"Failed to process quiz: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error processing quiz: {str(e)}")
    
    with tab2:
        st.markdown("### Student Performance Trends")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            trend_subject = st.selectbox(
                "Filter by Subject",
                ["All Subjects"] + list(set(["Mathematics", "Science", "English"])),  # Would fetch from DB
                key="trend_subject"
            )
        with col2:
            trend_class = st.selectbox(
                "Filter by Class",
                ["All Classes", "3A", "3B", "4A", "4B"],  # Would fetch from DB
                key="trend_class"
            )
        
        # Fetch data
        params = {}
        if trend_subject != "All Subjects":
            params["subject"] = trend_subject
        if trend_class != "All Classes":
            params["class_code"] = trend_class
        
        trends_data = fetch_api("/api/quiz-analytics/analytics/student-trends", params)
        
        if trends_data and trends_data.get('students'):
            st.markdown(f"**Showing {len(trends_data['students'])} students**")
            
            # Display as table
            students_df = pd.DataFrame(trends_data['students'])
            
            # Format for display
            display_df = students_df[[
                'student_name', 'class_code', 'quiz_count', 
                'average_percentage', 'progress_level', 'trend'
            ]].copy()
            
            display_df.columns = [
                'Student', 'Class', 'Quiz Count',
                'Avg %', 'Progress Level', 'Trend'
            ]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Show individual student details
            st.markdown("---")
            st.markdown("#### Individual Student Details")
            
            selected_student = st.selectbox(
                "Select Student",
                [s['student_name'] for s in trends_data['students']],
                key="selected_trend_student"
            )
            
            if selected_student:
                student_data = next(s for s in trends_data['students'] if s['student_name'] == selected_student)
                
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    st.metric("Average Score", f"{student_data['average_percentage']}%")
                with col_y:
                    st.metric("Quiz Count", student_data['quiz_count'])
                with col_z:
                    trend_icon = "📈" if student_data['trend'] == "improving" else "📉" if student_data['trend'] == "declining" else "➡️"
                    st.metric("Trend", f"{trend_icon} {student_data['trend'].title()}")
                
                # Recent scores chart
                if student_data.get('recent_scores'):
                    recent_df = pd.DataFrame({
                        'Quiz': [f"Quiz {i+1}" for i in range(len(student_data['recent_scores']))],
                        'Score': student_data['recent_scores']
                    })
                    st.line_chart(recent_df.set_index('Quiz'))
        else:
            st.info("No quiz data available. Upload quiz results to see trends.")
    
    with tab3:
        st.markdown("### Progress Level Distribution")
        st.markdown("Students classified by performance: **Exceeding** (85%+), **Meeting** (70-84%), **Working Towards** (<70%)")
        
        # Fetch progress levels
        progress_data = fetch_api("/api/quiz-analytics/analytics/progress-levels")
        
        if progress_data and progress_data.get('total_students', 0) > 0:
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🟢 Exceeding")
                st.metric(
                    "Count",
                    progress_data['exceeding']['count'],
                    delta=f"{progress_data['exceeding']['percentage']}%"
                )
                if progress_data['exceeding']['students']:
                    with st.expander("View Students"):
                        for student in progress_data['exceeding']['students']:
                            st.markdown(f"- {student}")
            
            with col2:
                st.markdown("#### 🟡 Meeting")
                st.metric(
                    "Count",
                    progress_data['meeting']['count'],
                    delta=f"{progress_data['meeting']['percentage']}%"
                )
                if progress_data['meeting']['students']:
                    with st.expander("View Students"):
                        for student in progress_data['meeting']['students']:
                            st.markdown(f"- {student}")
            
            with col3:
                st.markdown("#### 🔴 Working Towards")
                st.metric(
                    "Count",
                    progress_data['working_towards']['count'],
                    delta=f"{progress_data['working_towards']['percentage']}%"
                )
                if progress_data['working_towards']['students']:
                    with st.expander("View Students"):
                        for student in progress_data['working_towards']['students']:
                            st.markdown(f"- {student}")
            
            # Pie chart
            st.markdown("---")
            chart_data = pd.DataFrame({
                'Level': ['Exceeding', 'Meeting', 'Working Towards'],
                'Count': [
                    progress_data['exceeding']['count'],
                    progress_data['meeting']['count'],
                    progress_data['working_towards']['count']
                ]
            })
            st.bar_chart(chart_data.set_index('Level'))
        else:
            st.info("No quiz data available. Upload quiz results to see progress levels.")
    
    with tab4:
        st.markdown("### At-Risk Students")
        st.markdown("Students with low performance or declining trends who may need support")
        
        # Settings
        col1, col2 = st.columns(2)
        with col1:
            threshold = st.slider(
                "Performance Threshold",
                min_value=0,
                max_value=100,
                value=60,
                help="Students below this percentage are flagged",
                key="at_risk_threshold"
            )
        with col2:
            min_quizzes = st.number_input(
                "Minimum Quizzes",
                min_value=1,
                max_value=10,
                value=2,
                help="Minimum quiz attempts to be considered",
                key="at_risk_min_quizzes"
            )
        
        # Fetch at-risk students
        at_risk_data = fetch_api(
            "/api/quiz-analytics/analytics/at-risk",
            {"threshold": threshold, "min_quizzes": min_quizzes}
        )
        
        if at_risk_data:
            st.markdown(f"**{at_risk_data['at_risk_count']} students flagged for support**")
            
            if at_risk_data['students']:
                st.markdown("---")
                
                for student in at_risk_data['students']:
                    with st.expander(
                        f"{'🔴' if student['reason'] == 'declining_performance' else '🟠'} {student['student_name']} ({student['class_code']}) - Avg: {student['average_score']}%",
                        expanded=False
                    ):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Average Score", f"{student['average_score']}%")
                        with col_b:
                            st.metric("Quiz Count", student['quiz_count'])
                        with col_c:
                            reason_label = "Declining" if student['reason'] == "declining_performance" else "Low Performance"
                            st.metric("Risk Reason", reason_label)
                        
                        # Recent scores
                        if student.get('recent_scores'):
                            st.markdown("**Recent Scores:**")
                            scores_str = " → ".join([f"{s:.1f}%" for s in student['recent_scores']])
                            st.markdown(f"`{scores_str}`")
                        
                        # Action buttons
                        col_x, col_y = st.columns(2)
                        with col_x:
                            if st.button("Plan Intervention", key=f"intervene_{student['student_id']}"):
                                st.info("Intervention planning - integrate with existing tools")
                        with col_y:
                            if st.button("Contact Parent", key=f"contact_{student['student_id']}"):
                                st.info("Parent communication - Coming Soon")
            else:
                st.success("✅ No students currently at risk!")
        else:
            st.info("No data available")

def show_project_guardian():
    """Show Project Guardian - Digital Citizenship Breach Triage"""
    st.markdown("## 🛡️ Project Guardian")
    st.markdown("### Digital Citizenship Breach Triage Tool")
    st.markdown("Confidential AI-powered consultation for staff to assess digital citizenship incidents")
    
    st.markdown("---")
    
    # Disclaimer
    st.info(
        "**Disclaimer:** This is a tool to help you make better informed decisions. "
        "If you are still unsure of the outcome, please contact your Head of Year (HOY) or "
        "Designated Safeguarding Lead (DSL). No names should be used in this consultation form. "
        "Reminder: No data will be stored."
    )
    
    # Input form
    with st.form("guardian_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            year_group = st.selectbox(
                "Year Group",
                ["Year 3", "Year 4", "Year 5", "Year 6"],
                key="guardian_year_group"
            )
        
        with col2:
            incident_history = st.radio(
                "Incident History",
                ["First incident", "Repeated offense"],
                key="guardian_history"
            )
        
        description = st.text_area(
            "Describe the Incident",
            placeholder="e.g., 'A student has been receiving unkind messages...' or 'I found a student accessing inappropriate content...'",
            height=150,
            key="guardian_description"
        )
        
        submit = st.form_submit_button("Get AI Assessment", type="primary")
    
    # Process assessment
    if submit:
        if not description.strip():
            st.error("Please enter a description of the incident.")
            return
        
        with st.spinner("Analyzing incident..."):
            # Call backend API
            result = fetch_api(
                "/api/guardian/assess",
                method="POST",
                data={
                    "description": description,
                    "year_group": year_group,
                    "incident_history": incident_history
                }
            )
        
        if result:
            st.markdown("---")
            st.markdown("## 📋 ASSESSMENT COMPLETE")
            
            # Classification styling
            classification = result.get("classification", "MEDIUM")
            if classification == "LOW":
                st.success(f"### 🟢 {classification} - Teacher Level Resolution")
            elif classification == "MEDIUM":
                st.warning(f"### 🟡 {classification} - Head of Year Resolution")
            else:
                st.error(f"### 🔴 {classification} - DSL Level Resolution")
            
            # Reason
            st.markdown("#### Why?")
            st.markdown(result.get("reason", "No reason provided"))
            
            # Next steps
            st.markdown("#### Next Steps")
            for step in result.get("next_steps", []):
                st.markdown(f"- {step}")
            
            # Contact info based on classification
            if classification == "MEDIUM":
                st.markdown("#### Who to Contact")
                st.markdown(f"Inform your Head of Year: **hoy.{year_group.lower().replace(' ', '')}@school.edu**")
            elif classification == "HIGH":
                st.markdown("#### ⚠️ Who to Contact")
                st.error("**You must contact** your Designated Safeguarding Lead (DSL) immediately: **dsl@school.edu**")
            
            # Key resources
            st.markdown("#### Key Resources")
            st.markdown("- [Digital Citizenship Breach Policy](#)")
            st.markdown("- [Log in CPOMS](#)")
            
            # Option to start new consultation
            st.markdown("---")
            if st.button("Start New Consultation", key="guardian_reset"):
                st.rerun()
        else:
            st.error("Failed to get assessment. Please check your connection and try again.")
    
    # Show React app link
    st.markdown("---")
    st.markdown("### 🌐 Standalone Application")
    st.markdown(
        "For a dedicated fullscreen experience, access the [Project Guardian React App](http://localhost:5174) "
        "(requires React dev server running)"
    )

# Main navigation
def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.markdown("# 🏫 PTCC")
    st.sidebar.markdown("Personal Teaching Command Center")
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["Daily Briefing", "Students", "Classroom Tools", "CCA Comments", "ICT Behavior", "Quiz Analytics", "Project Guardian", "Search", "Import", "AI Agents", "Settings"],
        index=0
    )
    
    # Show selected page
    if page == "Daily Briefing":
        show_briefing()
    elif page == "Students":
        show_students()
    elif page == "Classroom Tools":
        show_classroom_tools()
    elif page == "CCA Comments":
        show_cca_comments()
    elif page == "ICT Behavior":
        show_ict_behavior()
    elif page == "Quiz Analytics":
        show_quiz_analytics()
    elif page == "Project Guardian":
        show_project_guardian()
    elif page == "Search":
        show_search()
    elif page == "Import":
        show_import()
    elif page == "AI Agents":
        show_agents()
    elif page == "Settings":
        show_settings()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 PTCC")

if __name__ == "__main__":
    main()
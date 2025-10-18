"""
PTCC - Personal Teaching Command Center
Demo version with authentication and basic features
"""

import streamlit as st
import hashlib

# Demo credentials
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "ptcc2024"

def check_password(username, password):
    """Simple password check"""
    return username == DEMO_USERNAME and password == DEMO_PASSWORD

def login_form():
    """Display login form"""
    st.title("🏫 PTCC Demo Access")
    st.markdown("---")
    
    with st.form("login_form"):
        st.markdown("### Demo Login")
        st.info("**Demo Credentials:** Username: `demo` | Password: `ptcc2024`")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_password(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials. Use demo/ptcc2024")

def main_app():
    """Main PTCC application"""
    st.title("🏫 PTCC - Personal Teaching Command Center")
    
    # Sidebar with logout
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick Navigation")
        page = st.radio("Go to:", ["Dashboard", "Student Search", "Document Upload"])
    
    # Main content based on page selection
    if page == "Dashboard":
        show_dashboard()
    elif page == "Student Search":
        show_student_search()
    elif page == "Document Upload":
        show_document_upload()

def show_dashboard():
    """Dashboard view"""
    st.success("✅ PTCC System Online")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Students", "160", "Demo Data")
    
    with col2:
        st.metric("Documents Processed", "45", "+12 today")
    
    with col3:
        st.metric("Quick Logs", "23", "+5 today")
    
    st.markdown("### Recent Activity")
    st.info("📝 Student incident logged for Year 5A")
    st.info("📊 Weekly behavior report generated")
    st.info("🔍 New support document uploaded")
    
    st.markdown("### System Features")
    st.write("✅ **Authentication** - Working login system")
    st.write("🔄 **Student Database** - 160 demo records ready")
    st.write("🔄 **Document Processing** - Upload and search capability")
    st.write("🔄 **Quick Logging** - Mobile-optimized incident logging")
    st.write("🔄 **AI Analysis** - Student pattern recognition")

def show_student_search():
    """Student search functionality"""
    st.subheader("🔍 Student Search")
    
    search_term = st.text_input("Search students:")
    
    if search_term:
        st.write(f"Searching for: {search_term}")
        
        # Mock search results
        demo_students = [
            {"name": "Alice Johnson", "year": "5A", "support_level": 2},
            {"name": "Bob Smith", "year": "4B", "support_level": 3},
            {"name": "Charlie Brown", "year": "6A", "support_level": 1}
        ]
        
        st.markdown("### Search Results:")
        for student in demo_students:
            if search_term.lower() in student["name"].lower():
                st.write(f"**{student['name']}** - {student['year']} (Support Level: {student['support_level']})")
    
    st.info("💡 **Coming Soon**: Real student database integration with 160+ profiles")

def show_document_upload():
    """Document upload interface"""
    st.subheader("📄 Document Upload")
    
    uploaded_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        st.write(f"File size: {uploaded_file.size} bytes")
        
        if st.button("Process Document"):
            st.info("🔄 Processing document for semantic search...")
            st.success("✅ Document processed! Ready for queries.")
            
            # Mock query interface
            query = st.text_input("Ask a question about this document:")
            if query:
                st.write(f"**Query:** {query}")
                st.write("**Answer:** This is a demo response. Full AI-powered document analysis coming soon!")
    
    st.info("💡 **Coming Soon**: Full document processing with semantic search and AI analysis")

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="PTCC Demo",
        page_icon="🏫",
        layout="wide"
    )
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Show login or main app
    if not st.session_state.authenticated:
        login_form()
    else:
        main_app()

if __name__ == "__main__":
    main()

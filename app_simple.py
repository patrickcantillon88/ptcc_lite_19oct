"""
Simple Streamlit app for testing Render deployment
"""

import streamlit as st
import pandas as pd
import os

def main():
    st.set_page_config(
        page_title="PTCC Demo - Simple Test",
        page_icon="🏫",
        layout="wide"
    )
    
    st.title("🏫 PTCC Demo - Deployment Test")
    
    st.success("✅ Streamlit is working!")
    st.info("✅ Pandas is working!")
    st.warning("✅ FastAPI backend coming soon...")
    
    # Test basic functionality
    st.subheader("Basic Test")
    
    # Simple dataframe
    df = pd.DataFrame({
        'Student': ['Alice', 'Bob', 'Charlie'],
        'Grade': ['A', 'B', 'A'],
        'Subject': ['Math', 'Science', 'English']
    })
    
    st.dataframe(df)
    
    # Environment info
    st.subheader("Environment Info")
    st.write(f"Python version: {os.sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    st.write(f"Pandas version: {pd.__version__}")
    
    st.markdown("---")
    st.markdown("**Next Steps:**")
    st.markdown("1. ✅ Basic deployment working")  
    st.markdown("2. 🔄 Add FastAPI backend")
    st.markdown("3. 🔄 Add authentication")
    st.markdown("4. 🔄 Add full PTCC features")

if __name__ == "__main__":
    main()
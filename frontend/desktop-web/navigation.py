"""
Unified Navigation Component for PTCC Desktop Web

Provides consistent sidebar navigation across all pages without dropdowns.
All navigation is direct links using Streamlit's page switching.
"""

import streamlit as st
from typing import Optional, List, Dict, Any

def render_main_navigation() -> None:
    """
    Render the main navigation sidebar.
    Call this at the top of every page in the pages/ directory.
    """
    with st.sidebar:
        # App title
        st.markdown("### 🏫 PTCC")
        st.markdown("Personal Teaching Command Center")
        st.markdown("---")
        
        # Main navigation sections
        st.markdown("#### 📚 Navigation")
        
        # Dashboard section
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[📊 Dashboard](/)")
        with col2:
            st.markdown("_main_", unsafe_allow_html=True)
        
        # Briefing section
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[📋 Briefing](/Briefing)")
        
        # Search section
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[🔍 Search](/Search)")
        
        # Students section
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[👥 Students](/Students)")
        
        st.markdown("---")
        
        # AI & Tools section
        st.markdown("#### 🤖 AI & Tools")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[🤖 Classroom Copilot](/classroom_copilot)")
        
        st.markdown("---")
        
        # System section
        st.markdown("#### ⚙️ System")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[📋 System Overview](http://localhost:5189)")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("[⚙️ Settings](/Settings)")
        
        st.markdown("---")
        
        # Footer
        st.markdown("#### 📱 Quick Access")
        if st.button("🌐 Open Lesson Console", use_container_width=True):
            import webbrowser
            webbrowser.open("http://localhost:5173")
        
        # Backend status
        st.markdown("---")
        st.markdown("#### 🔌 System Status")
        try:
            import requests
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ Backend: Online")
            else:
                st.error("❌ Backend: Error")
        except:
            st.error("❌ Backend: Offline")


def render_section_navigation(section_name: str, items: List[Dict[str, Any]]) -> None:
    """
    Render a section-specific navigation with subsections.
    Use this when a page needs to switch between different views without dropdowns.
    
    Args:
        section_name: Name of the current section
        items: List of navigation items with {"label": str, "key": str, "icon": str}
    """
    st.markdown("---")
    st.markdown(f"#### {section_name}")
    
    # Create uniform button layout
    for item in items:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{item.get('icon', '📌')} {item['label']}", 
                        key=f"nav_{item['key']}", 
                        use_container_width=True):
                st.session_state.current_view = item['key']
                st.rerun()
    
    st.markdown("---")


def get_page_title(page_name: str) -> tuple:
    """
    Get the title and icon for a page based on its name.
    
    Returns:
        Tuple of (icon, title)
    """
    page_map = {
        "Dashboard": ("📊", "Dashboard"),
        "Briefing": ("📋", "Daily Briefing & AI Assistant"),
        "Search": ("🔍", "Search"),
        "Students": ("👥", "Students"),
        "classroom_copilot": ("🤖", "Classroom Copilot"),
        "Settings": ("⚙️", "Settings"),
    }
    return page_map.get(page_name, ("📄", page_name))


def render_page_header(page_name: str) -> None:
    """
    Render a consistent page header with title and icon.
    
    Args:
        page_name: The name of the current page
    """
    icon, title = get_page_title(page_name)
    st.title(f"{icon} {title}")


def replace_selectbox_with_tabs(options: List[str], key: str) -> str:
    """
    Replace a selectbox dropdown with horizontal tabs/buttons.
    
    Args:
        options: List of options to display as tabs
        key: Session state key for tracking selection
    
    Returns:
        The selected option
    """
    if key not in st.session_state:
        st.session_state[key] = options[0]
    
    cols = st.columns(len(options))
    for i, option in enumerate(options):
        with cols[i]:
            if st.button(option, key=f"{key}_btn_{i}", use_container_width=True,
                        type="primary" if st.session_state[key] == option else "secondary"):
                st.session_state[key] = option
                st.rerun()
    
    return st.session_state[key]


def render_sidebar_filters(filters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Render sidebar filters for search/filtering instead of inline dropdowns.
    
    Args:
        filters: Dictionary of filter configurations
               {"filter_name": {"options": [...], "type": "selectbox|multiselect"}}
    
    Returns:
        Dictionary of selected filter values
    """
    st.sidebar.markdown("### 🔍 Filters")
    
    results = {}
    for filter_name, config in filters.items():
        if config.get("type") == "multiselect":
            results[filter_name] = st.sidebar.multiselect(
                filter_name,
                config.get("options", []),
                key=f"filter_{filter_name}"
            )
        else:  # selectbox
            results[filter_name] = st.sidebar.selectbox(
                filter_name,
                config.get("options", []),
                key=f"filter_{filter_name}"
            )
    
    return results


def render_quick_actions(actions: List[Dict[str, str]]) -> Optional[str]:
    """
    Render quick action buttons in a horizontal layout.
    
    Args:
        actions: List of action configurations
                {"label": str, "key": str, "icon": str}
    
    Returns:
        The key of the clicked action, or None
    """
    st.markdown("### 🚀 Quick Actions")
    
    cols = st.columns(len(actions))
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(
                f"{action.get('icon', '⚡')} {action['label']}",
                key=f"qa_{action['key']}",
                use_container_width=True
            ):
                return action['key']
    
    return None


# Migration helpers for replacing dropdowns

def migrate_selectbox_to_tabs(old_selectbox_key: str, options: List[str]) -> str:
    """Helper to migrate from old selectbox to new tab-based selection."""
    return replace_selectbox_with_tabs(options, old_selectbox_key)


def migrate_sidebar_selectbox_to_filters(filters_config: Dict[str, List[str]]) -> Dict[str, Any]:
    """Helper to migrate inline selectboxes to sidebar filter panel."""
    return render_sidebar_filters({
        name: {"options": opts, "type": "selectbox"}
        for name, opts in filters_config.items()
    })

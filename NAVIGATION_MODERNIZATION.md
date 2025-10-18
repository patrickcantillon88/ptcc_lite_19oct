# PTCC Navigation System Modernization

## Overview

Replace all dropdown menus and selectboxes with a consistent sidebar navigation style across the entire system.

## Key Changes

### 1. Unified Sidebar Navigation (NEW)
**File**: `frontend/desktop-web/navigation.py`

All pages now use the same sidebar with:
- Direct links to main sections (no dropdowns)
- Organized into sections: Navigation, AI & Tools, System
- Backend health status indicator
- Mobile PWA quick access
- Consistent styling with icons

### 2. Implementation Pattern

#### Before (Old Pattern)
```python
# In app.py or individual pages
with st.sidebar:
    page = st.selectbox("Select Page", ["Dashboard", "Search", "Students"])
    if page == "Dashboard":
        show_dashboard()
```

#### After (New Pattern)
```python
# In app.py or any page
from navigation import render_main_navigation, render_page_header

render_main_navigation()  # Renders unified sidebar
render_page_header("Dashboard")  # Sets title
show_dashboard()
```

## Migration Tasks

### Phase 1: Core Navigation Setup
- [x] Create `navigation.py` module
- [ ] Update each page file to use `render_main_navigation()`
- [ ] Replace inline page selectors with tab-based navigation

### Phase 2: Replace Inline Dropdowns
Replace all `st.selectbox()` and `st.radio()` calls with one of:

#### Option A: Horizontal Tabs (for mode selection)
```python
# OLD
mode = st.selectbox("View Mode", ["Summary", "Detailed", "Raw"])

# NEW
from navigation import replace_selectbox_with_tabs
mode = replace_selectbox_with_tabs(["Summary", "Detailed", "Raw"], "view_mode")
```

#### Option B: Sidebar Filters (for filtering)
```python
# OLD
class_filter = st.selectbox("Class", classes)
level_filter = st.multiselect("Support Level", levels)

# NEW
from navigation import render_sidebar_filters
filters = render_sidebar_filters({
    "Class": {"options": classes, "type": "selectbox"},
    "Support Level": {"options": levels, "type": "multiselect"}
})
```

#### Option C: Quick Actions (for common tasks)
```python
# OLD
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Generate Report"):
        generate_report()

# NEW
from navigation import render_quick_actions
action = render_quick_actions([
    {"label": "Generate Report", "key": "gen_report", "icon": "📊"},
    {"label": "Export Data", "key": "export", "icon": "💾"}
])
if action == "gen_report":
    generate_report()
```

## Files to Update

### Phase 2: High Priority (Inline Dropdowns)
1. `frontend/desktop-web/app.py` (line 156-199+)
   - Data source selector → tabs
   - Multiple `st.selectbox()` calls → sidebar filters

2. `frontend/desktop-web/pages/03_🔍_Search.py`
   - Search type selector
   - Filter selections

3. `frontend/desktop-web/pages/04_👥_Students.py`
   - Class selector
   - Sort/filter dropdowns

### Phase 2: Medium Priority
4. `frontend/desktop-web/pages/05_Settings.py`
   - Settings selectors

5. `frontend/desktop-web/pages/01_Briefing.py`
   - Data source toggle

6. `frontend/desktop-web/pages/02_🤖_teacher_assistant.py`
   - Already has inline navigation, can be enhanced

## Benefits

✅ **Consistency**: Same look and feel across all pages
✅ **No Dropdowns**: Cleaner, more direct navigation
✅ **Mobile Friendly**: Sidebar persists without dropdowns
✅ **Accessibility**: Direct links easier to interact with
✅ **Performance**: Less JavaScript overhead from dropdowns
✅ **Maintainability**: Single source of truth for navigation

## Quick Start

### Step 1: Add to Your Page
```python
from frontend.desktop_web.navigation import render_main_navigation, render_page_header

st.set_page_config(page_title="Page Name", page_icon="📌", layout="wide")

render_main_navigation()  # Add sidebar
render_page_header("Page Name")  # Add header
# Rest of your page code
```

### Step 2: Update Dropdowns
Pick the appropriate replacement (tabs, sidebar filters, or quick actions) based on use case.

### Step 3: Test
Navigate between pages and verify sidebar is consistent.

## Architecture

```
navigation.py
├── render_main_navigation()      → Main sidebar with links
├── render_page_header()          → Consistent page titles
├── replace_selectbox_with_tabs() → Horizontal button tabs
├── render_sidebar_filters()      → Advanced filtering
├── render_quick_actions()        → Action buttons
└── Helper functions
    ├── get_page_title()
    ├── render_section_navigation()
    └── migrate_* helpers
```

## Styling

All components use Streamlit's native styling:
- Icons from emoji set
- Color scheme: Primary (buttons) / Secondary (tabs)
- Responsive columns for consistency
- Markdown dividers for sections

## Future Enhancements

- [ ] Dark mode support
- [ ] Collapsible sections in sidebar
- [ ] Breadcrumb navigation
- [ ] Active page highlighting
- [ ] Custom CSS for advanced theming
- [ ] Submenu expansion for nested navigation

## Testing Checklist

- [ ] All pages load with navigation visible
- [ ] Navigation links work correctly
- [ ] Backend status indicator updates
- [ ] Mobile PWA button opens correctly
- [ ] No dropdown menus appear
- [ ] Consistent styling across all pages
- [ ] Filters work correctly
- [ ] Quick actions respond properly
- [ ] Tab selection persists during page session
- [ ] No console errors

## Support

For questions or issues with the new navigation system, refer to:
- `navigation.py` - Full API documentation with docstrings
- Individual page implementations for examples

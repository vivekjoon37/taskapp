import streamlit as st
import requests
import json
import uuid
from datetime import datetime, date, timedelta
from typing import List

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AssignTaskApp",
    page_icon="📋",
    layout="centered",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header */
    .app-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .app-header p {
        color: #888;
        font-size: 0.95rem;
    }

    /* Task card */
    .task-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        background: #fafafa;
        transition: all 0.2s ease;
    }
    .task-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
    .task-card.completed {
        opacity: 0.45;
        background: #f0f0f0;
        text-decoration: line-through;
    }
    .task-card.urgent-soon {
        border-left: 4px solid #f57c00;
        background: #fff8f0;
    }

    /* Urgency badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-low      { background: #e8f5e9; color: #2e7d32; }
    .badge-medium   { background: #fff3e0; color: #e65100; }
    .badge-high     { background: #fce4ec; color: #c62828; }
    .badge-critical { background: #c62828; color: #ffffff; }

    /* Success animation */
    .success-msg {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-radius: 12px;
        margin: 1rem 0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Data Layer (GitHub Gist) ──────────────────────────────────────────────────

def _gist_headers():
    token = st.secrets.get("github_token", "")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def _gist_url():
    gist_id = st.secrets.get("gist_id", "")
    return f"https://api.github.com/gists/{gist_id}"


def load_tasks() -> List[dict]:
    """Load tasks from GitHub Gist."""
    try:
        resp = requests.get(_gist_url(), headers=_gist_headers(), timeout=10)
        if resp.status_code == 200:
            content = resp.json()["files"]["tasks.json"]["content"]
            return json.loads(content)
    except Exception:
        pass
    return []


def save_tasks(tasks: List[dict]):
    """Save tasks to GitHub Gist."""
    try:
        payload = {
            "files": {
                "tasks.json": {
                    "content": json.dumps(tasks, indent=2, default=str)
                }
            }
        }
        requests.patch(_gist_url(), headers=_gist_headers(), json=payload, timeout=10)
    except Exception as e:
        st.error(f"Failed to save tasks: {e}")


# ─── Helpers ───────────────────────────────────────────────────────────────────

def urgency_badge(urgency: str) -> str:
    cls = f"badge-{urgency.lower()}"
    return f'<span class="badge {cls}">{urgency}</span>'


def is_due_soon(by_when_str: str) -> bool:
    """Check if task is due within 2 days."""
    try:
        due = datetime.strptime(by_when_str, "%Y-%m-%d").date()
        return due <= date.today() + timedelta(days=2)
    except (ValueError, TypeError):
        return False


# ─── Sidebar / Auth ───────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📋 AssignTaskApp")
    st.markdown("---")

    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "vivek_logged_in" not in st.session_state:
        st.session_state.vivek_logged_in = False

    email = st.text_input("Your Email", placeholder="name@mathco.com", key="email_input")

    if email:
        if email.endswith("@mathco.com"):
            st.session_state.user_email = email
            st.session_state.authenticated = True
            st.success(f"✅ Welcome!")
        else:
            st.error("Only @mathco.com emails allowed")
            st.session_state.authenticated = False

    if st.session_state.authenticated:
        st.markdown("---")
        st.markdown("### Navigation")
        page = st.radio(
            "Go to",
            ["📝 Assign Task", "📋 My Tasks"],
            label_visibility="collapsed",
        )
    else:
        page = None


# ─── Main Content ──────────────────────────────────────────────────────────────

if not st.session_state.get("authenticated"):
    st.markdown("""
    <div class="app-header">
        <h1>📋 AssignTaskApp</h1>
        <p>Enter your @mathco.com email in the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### 📝 Assign Tasks
        Quickly assign tasks with name, description, urgency, and deadline.
        """)
    with col2:
        st.markdown("""
        #### 📋 View & Manage
        Track progress, complete tasks, and stay on top of deadlines.
        """)
    st.stop()


# ─── Screen 1: Assign Task ────────────────────────────────────────────────────

if page == "📝 Assign Task":
    st.markdown("""
    <div class="app-header">
        <h1>📝 Assign a Task</h1>
        <p>Assign a task to vivek.joon@mathco.com</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("assign_task_form", clear_on_submit=True):
        task_name = st.text_input("Task Name *", placeholder="e.g. Review Q4 Report")
        description = st.text_area("Description", placeholder="Add details about the task...", height=100)
        col1, col2 = st.columns(2)
        with col1:
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
        with col2:
            by_when = st.date_input("By When", min_value=date.today())

        submitted = st.form_submit_button("🚀 Assign Task", use_container_width=True)

        if submitted:
            if not task_name.strip():
                st.error("Task name is required!")
            else:
                tasks = load_tasks()
                new_task = {
                    "id": str(uuid.uuid4())[:8],
                    "task_name": task_name.strip(),
                    "description": description.strip(),
                    "urgency": urgency,
                    "by_when": str(by_when),
                    "assigned_by": st.session_state.user_email,
                    "assigned_to": "vivek.joon@mathco.com",
                    "completed": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                tasks.append(new_task)
                save_tasks(tasks)
                st.markdown("""
                <div class="success-msg">
                    <h3>✅ Task Assigned!</h3>
                    <p>Your task has been sent to vivek.joon@mathco.com</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()


# ─── Screen 2: My Tasks ───────────────────────────────────────────────────────

elif page == "📋 My Tasks":
    # Gatekeeper: only vivek.joon@mathco.com
    if st.session_state.user_email != "vivek.joon@mathco.com":
        st.warning("🔒 This page is only accessible to vivek.joon@mathco.com")
        st.stop()

    # Password gate
    if not st.session_state.get("vivek_logged_in"):
        st.markdown("""
        <div class="app-header">
            <h1>🔐 Authentication</h1>
            <p>Enter your password to access your tasks</p>
        </div>
        """, unsafe_allow_html=True)

        pwd = st.text_input("Password", type="password", key="pwd_input")
        if st.button("Login", use_container_width=True):
            if pwd == st.secrets.get("vivek_password", ""):
                st.session_state.vivek_logged_in = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()

    # ── My Tasks View ──
    st.markdown("""
    <div class="app-header">
        <h1>📋 My Tasks</h1>
        <p>Manage your assigned tasks</p>
    </div>
    """, unsafe_allow_html=True)

    tasks = load_tasks()

    # ── Add New Task ──
    with st.expander("➕ Add a new task"):
        with st.form("add_task_form", clear_on_submit=True):
            new_name = st.text_input("Task Name *", placeholder="e.g. Prepare slides")
            new_desc = st.text_area("Description", placeholder="Details...", height=80)
            c1, c2 = st.columns(2)
            with c1:
                new_urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"], key="add_urgency")
            with c2:
                new_by_when = st.date_input("By When", min_value=date.today(), key="add_date")
            if st.form_submit_button("➕ Add Task", use_container_width=True):
                if new_name.strip():
                    tasks.append({
                        "id": str(uuid.uuid4())[:8],
                        "task_name": new_name.strip(),
                        "description": new_desc.strip(),
                        "urgency": new_urgency,
                        "by_when": str(new_by_when),
                        "assigned_by": "vivek.joon@mathco.com",
                        "assigned_to": "vivek.joon@mathco.com",
                        "completed": False,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
                    save_tasks(tasks)
                    st.rerun()
                else:
                    st.error("Task name is required!")

    # ── Summary Stats ──
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("completed"))
    pending = total - done
    due_soon = sum(1 for t in tasks if not t.get("completed") and is_due_soon(t.get("by_when", "")))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Pending", pending)
    c3.metric("Completed", done)
    c4.metric("⚠️ Due Soon", due_soon)

    st.markdown("---")

    if not tasks:
        st.info("No tasks yet. Add one above or have someone assign one to you!")
        st.stop()

    # ── Task List ──
    for i, task in enumerate(tasks):
        task_completed = task.get("completed", False)
        due_soon_flag = not task_completed and is_due_soon(task.get("by_when", ""))

        # Card styling
        card_class = "task-card"
        if task_completed:
            card_class += " completed"
        elif due_soon_flag:
            card_class += " urgent-soon"

        with st.container():
            cols = st.columns([0.5, 5, 1.5])

            # Checkbox
            with cols[0]:
                checked = st.checkbox(
                    "Done",
                    value=task_completed,
                    key=f"check_{task['id']}",
                    label_visibility="collapsed",
                )
                if checked != task_completed:
                    tasks[i]["completed"] = checked
                    save_tasks(tasks)
                    st.rerun()

            # Task info
            with cols[1]:
                badge = urgency_badge(task.get("urgency", "Low"))
                strike_start = "<s>" if task_completed else ""
                strike_end = "</s>" if task_completed else ""
                due_icon = "🟠 " if due_soon_flag else ""
                opacity = "opacity: 0.45;" if task_completed else ""

                st.markdown(
                    f'<div style="{opacity}">'
                    f'{strike_start}<strong>{task["task_name"]}</strong>{strike_end} '
                    f'{badge}<br/>'
                    f'<small style="color:#888;">'
                    f'{due_icon}Due: {task.get("by_when", "N/A")} · '
                    f'From: {task.get("assigned_by", "Unknown")}'
                    f'</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Edit button
            with cols[2]:
                if st.button("✏️ Edit", key=f"edit_{task['id']}"):
                    st.session_state[f"editing_{task['id']}"] = True

        # ── Edit Form ──
        if st.session_state.get(f"editing_{task['id']}"):
            with st.form(f"edit_form_{task['id']}"):
                st.markdown(f"**Editing:** {task['task_name']}")
                ed_name = st.text_input("Task Name", value=task["task_name"], key=f"en_{task['id']}")
                ed_desc = st.text_area("Description", value=task.get("description", ""), key=f"ed_{task['id']}", height=80)
                ec1, ec2 = st.columns(2)
                with ec1:
                    urgency_options = ["Low", "Medium", "High", "Critical"]
                    current_idx = urgency_options.index(task.get("urgency", "Low")) if task.get("urgency") in urgency_options else 0
                    ed_urgency = st.selectbox("Urgency", urgency_options, index=current_idx, key=f"eu_{task['id']}")
                with ec2:
                    try:
                        current_date = datetime.strptime(task.get("by_when", ""), "%Y-%m-%d").date()
                    except ValueError:
                        current_date = date.today()
                    ed_date = st.date_input("By When", value=current_date, key=f"edt_{task['id']}")

                sc1, sc2 = st.columns(2)
                with sc1:
                    save_edit = st.form_submit_button("💾 Save", use_container_width=True)
                with sc2:
                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)

                if save_edit:
                    tasks[i]["task_name"] = ed_name.strip()
                    tasks[i]["description"] = ed_desc.strip()
                    tasks[i]["urgency"] = ed_urgency
                    tasks[i]["by_when"] = str(ed_date)
                    save_tasks(tasks)
                    st.session_state.pop(f"editing_{task['id']}", None)
                    st.rerun()
                if cancel_edit:
                    st.session_state.pop(f"editing_{task['id']}", None)
                    st.rerun()

        if not task_completed and due_soon_flag:
            st.caption("🟠 This task is due within 2 days!")

        st.markdown("<hr style='margin: 0.5rem 0; border-color: #eee;'>", unsafe_allow_html=True)

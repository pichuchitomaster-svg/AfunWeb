import streamlit as st
import pandas as pd
import numpy as np
import json
import random
import string
import re
import math
import colorsys
from datetime import datetime, date, timedelta
from pathlib import Path

# ============================================================
# NEXUS OS — A multipurpose personal web portal built in Streamlit
# ============================================================
st.set_page_config(
    page_title="NEXUS OS — Personal Command Center",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("nexus_data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "workspace.json"

DEFAULTS = {
    "tasks": [],
    "notes": [],
    "bookmarks": [],
    "habits": [],
    "journal": [],
    "theme": "Midnight",
    "accent": "#8B5CF6",
    "username": "Explorer",
    "focus_minutes": 25,
    "completed_focus": 0,
    "launch_count": 1,
    "scratchpad": "",
    "saved_palettes": [],
    "saved_conversions": [],
}

def load_data():
    try:
        if DATA_FILE.exists():
            raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return {**DEFAULTS, **raw}
    except Exception:
        pass
    return DEFAULTS.copy()

def save_data():
    try:
        DATA_FILE.write_text(
            json.dumps({k: st.session_state[k] for k in DEFAULTS}, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8"
        )
    except Exception:
        st.warning("Couldn't save local workspace data. Check folder permissions.")

if "booted" not in st.session_state:
    stored = load_data()
    for key, value in stored.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.booted = True

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------------------- STYLE -----------------------------
THEMES = {
    "Midnight": {"bg": "#090B14", "panel": "#121627", "panel2": "#181E32", "text": "#F4F6FF", "muted": "#9AA4C3"},
    "Graphite": {"bg": "#111315", "panel": "#1B1E22", "panel2": "#252A30", "text": "#F4F4F5", "muted": "#A1A1AA"},
    "Ocean": {"bg": "#06151D", "panel": "#0C2532", "panel2": "#123444", "text": "#E8FAFF", "muted": "#8DB7C8"},
    "Plum": {"bg": "#170D1D", "panel": "#281532", "panel2": "#382044", "text": "#FFF3FF", "muted": "#C1A2C8"},
    "Paper": {"bg": "#F3F5F9", "panel": "#FFFFFF", "panel2": "#E8ECF4", "text": "#182033", "muted": "#596579"},
}
theme = THEMES.get(st.session_state.theme, THEMES["Midnight"])
accent = st.session_state.accent

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {{
 --n-bg:{theme['bg']}; --n-panel:{theme['panel']}; --n-panel2:{theme['panel2']};
 --n-text:{theme['text']}; --n-muted:{theme['muted']}; --n-accent:{accent};
}}
.stApp {{ background:var(--n-bg); color:var(--n-text); font-family:'Manrope',sans-serif; }}
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stSidebar"] {{ background:var(--n-panel); border-right:1px solid color-mix(in srgb, var(--n-accent) 25%, transparent); }}
.block-container {{ max-width:1500px; padding-top:1.7rem; padding-bottom:4rem; }}
h1,h2,h3,h4 {{ letter-spacing:-.035em; color:var(--n-text); }}
p, label, li, span {{ color:inherit; }}
a {{ color:var(--n-accent) !important; }}
div.stButton > button, div.stDownloadButton > button {{
 background:var(--n-panel2); color:var(--n-text); border:1px solid color-mix(in srgb,var(--n-accent) 45%, transparent);
 border-radius:12px; font-weight:700; transition:all .18s ease; min-height:2.6rem;
}}
div.stButton > button:hover, div.stDownloadButton > button:hover {{
 background:var(--n-accent); color:white; border-color:var(--n-accent); transform:translateY(-1px);
}}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input, div[data-testid="stDateInput"] input {{
 background:var(--n-panel); color:var(--n-text); border-radius:10px; border-color:color-mix(in srgb,var(--n-accent) 30%, transparent);
}}
div[data-baseweb="select"] > div {{ background:var(--n-panel); border-color:color-mix(in srgb,var(--n-accent) 30%, transparent); border-radius:10px; }}
div[data-testid="stMetric"] {{ background:var(--n-panel); border:1px solid color-mix(in srgb,var(--n-accent) 25%, transparent); padding:1rem 1.1rem; border-radius:16px; }}
div[data-testid="stMetricLabel"] {{ color:var(--n-muted); }}
div[data-testid="stMetricValue"] {{ color:var(--n-text); font-weight:800; }}
hr {{ border-color:color-mix(in srgb,var(--n-accent) 24%, transparent); }}
.nexus-hero {{
 background:radial-gradient(circle at 85% 15%, color-mix(in srgb,var(--n-accent) 30%, transparent), transparent 32%),
 linear-gradient(135deg,var(--n-panel),var(--n-panel2)); border:1px solid color-mix(in srgb,var(--n-accent) 45%, transparent);
 padding:2rem; border-radius:24px; margin-bottom:1.2rem; position:relative; overflow:hidden;
}}
.nexus-kicker {{ font-family:'DM Mono',monospace; color:var(--n-accent); letter-spacing:.16em; font-size:.75rem; text-transform:uppercase; }}
.nexus-title {{ font-size:clamp(2.2rem,5vw,4.5rem); line-height:1.02; font-weight:800; margin:.55rem 0; }}
.nexus-sub {{ color:var(--n-muted); max-width:720px; font-size:1.02rem; }}
.nexus-card {{ background:var(--n-panel); border:1px solid color-mix(in srgb,var(--n-accent) 22%, transparent); border-radius:18px; padding:1.1rem 1.2rem; min-height:110px; }}
.nexus-card h3 {{ margin:.2rem 0 .55rem 0; font-size:1.05rem; }}
.nexus-muted {{ color:var(--n-muted); font-size:.9rem; }}
.nexus-chip {{ display:inline-block; background:color-mix(in srgb,var(--n-accent) 18%, transparent); color:var(--n-text); padding:.28rem .62rem; border-radius:99px; font-size:.75rem; margin-right:.3rem; }}
.nexus-big {{ font-size:2rem; font-weight:800; }}
.nexus-line {{ height:4px; background:var(--n-panel2); border-radius:9px; overflow:hidden; }}
.nexus-line span {{ display:block; height:100%; background:var(--n-accent); }}
code {{ color:var(--n-accent) !important; }}
[data-testid="stDataFrame"] {{ border:1px solid color-mix(in srgb,var(--n-accent) 25%, transparent); border-radius:14px; overflow:hidden; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------- UTILITIES -----------------------------
def persist():
    save_data()

def add_points_placeholder():
    return None

def safe_filename(text):
    text = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip()).strip("-")
    return text[:60] or "nexus-export"

def section_header(kicker, title, description=None):
    st.markdown(f'<div class="nexus-kicker">{kicker}</div><h1 style="margin:.3rem 0 .2rem">{title}</h1>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="nexus-muted" style="margin-bottom:1.2rem">{description}</div>', unsafe_allow_html=True)

def card(title, body, icon="◈", tag=None):
    tag_html = f'<span class="nexus-chip">{tag}</span>' if tag else ""
    st.markdown(f'<div class="nexus-card"><div class="nexus-kicker">{icon} &nbsp; {tag_html}</div><h3>{title}</h3><div class="nexus-muted">{body}</div></div>', unsafe_allow_html=True)

def empty_state(title, detail):
    st.markdown(f'<div class="nexus-card"><h3>{title}</h3><div class="nexus-muted">{detail}</div></div>', unsafe_allow_html=True)

def persist_and_rerun():
    persist()
    st.rerun()

def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def luminance(hex_color):
    rgb = [v / 255 for v in hex_to_rgb(hex_color)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    return .2126*rgb[0] + .7152*rgb[1] + .0722*rgb[2]

def contrast_ratio(a, b):
    l1, l2 = sorted([luminance(a), luminance(b)], reverse=True)
    return (l1 + .05) / (l2 + .05)

def normalize_task(task):
    task.setdefault("done", False)
    task.setdefault("priority", "Normal")
    task.setdefault("category", "Personal")
    task.setdefault("due", str(date.today()))
    task.setdefault("created", datetime.now().isoformat(timespec="minutes"))
    return task

# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="padding:.4rem .2rem 1.2rem">
      <div style="font-size:2rem;font-weight:800;letter-spacing:-.08em">◈ NEXUS</div>
      <div class="nexus-kicker">PERSONAL COMMAND CENTER</div>
    </div>
    """, unsafe_allow_html=True)
    pages = [
        "Overview", "Task Manager", "Notes & Journal", "Habit Tracker", "Focus Studio",
        "Data Lab", "Calculator Suite", "Creative Studio", "Knowledge Hub",
        "Text Workshop", "Utility Deck", "Settings & Backup"
    ]
    page = st.radio("NAVIGATION", pages, label_visibility="collapsed")
    st.divider()
    st.markdown(f"**Welcome, {st.session_state.username}**")
    st.caption(f"Workspace • {date.today().strftime('%A, %d %B %Y')}")
    done_count = sum(1 for t in st.session_state.tasks if t.get("done"))
    total_count = len(st.session_state.tasks)
    st.progress(done_count / max(total_count, 1), text=f"Tasks complete: {done_count}/{total_count}")
    st.markdown('<div class="nexus-muted">LOCAL WORKSPACE • AUTOSAVE</div>', unsafe_allow_html=True)

# ----------------------------- OVERVIEW -----------------------------
if page == "Overview":
    now = datetime.now()
    st.markdown(f"""
    <div class="nexus-hero">
      <div class="nexus-kicker">SYSTEM ONLINE / PERSONAL SPACE</div>
      <div class="nexus-title">Make room for<br><span style="color:{accent}">what matters.</span></div>
      <div class="nexus-sub">Welcome back, {st.session_state.username}. Your tools, thoughts, projects, and ideas live here.</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OPEN TASKS", sum(not t.get("done", False) for t in st.session_state.tasks))
    c2.metric("NOTES SAVED", len(st.session_state.notes))
    c3.metric("BOOKMARKS", len(st.session_state.bookmarks))
    c4.metric("FOCUS SESSIONS", st.session_state.completed_focus)
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("⚡ Quick launch")
        quick = st.columns(2)
        quick_pages = [("＋ New task", "Task Manager"), ("✎ Capture an idea", "Notes & Journal"),
                       ("◷ Start a focus session", "Focus Studio"), ("▦ Explore data", "Data Lab")]
        for i, (label, dest) in enumerate(quick_pages):
            with quick[i % 2]:
                if st.button(label, key=f"quick_{i}", use_container_width=True):
                    st.session_state.quick_destination = dest
                    st.rerun()
        st.subheader("☀️ Today's briefing")
        today = str(date.today())
        due_today = [t for t in st.session_state.tasks if t.get("due") == today and not t.get("done")]
        if due_today:
            for t in due_today[:5]:
                st.markdown(f"- **{t['title']}** · {t.get('priority','Normal')} priority")
        else:
            st.info("No unfinished tasks due today. Add something small and meaningful.")
    with right:
        st.subheader("📌 Recent notes")
        if st.session_state.notes:
            for note in sorted(st.session_state.notes, key=lambda n:n.get("updated",""), reverse=True)[:4]:
                st.markdown(f'<div class="nexus-card" style="min-height:auto;margin-bottom:.6rem"><b>{note["title"]}</b><div class="nexus-muted">{note.get("updated","")[:16]} · {len(note.get("body",""))} characters</div></div>', unsafe_allow_html=True)
        else:
            empty_state("Your ideas go here", "Create your first note in Notes & Journal.")
        st.subheader("🌦️ A tiny prompt")
        prompts = [
            "What would make today feel like a win?",
            "What could you simplify instead of perfecting?",
            "What idea have you been postponing?",
            "What did you learn recently that surprised you?",
            "What can you finish in fifteen minutes?"
        ]
        st.markdown(f'<div class="nexus-card"><div class="nexus-muted">DAILY PROMPT</div><h3>{random.choice(prompts)}</h3></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("Your workspace at a glance")
    stats = pd.DataFrame({
        "Area": ["Tasks", "Notes", "Bookmarks", "Journal entries", "Saved palettes"],
        "Items": [len(st.session_state.tasks), len(st.session_state.notes), len(st.session_state.bookmarks),
                  len(st.session_state.journal), len(st.session_state.saved_palettes)]
    })
    st.bar_chart(stats.set_index("Area"), height=230)

# ----------------------------- TASK MANAGER -----------------------------
elif page == "Task Manager":
    section_header("ORGANIZE / EXECUTE", "Task Manager", "Turn a long list into a clear next step. Changes save to your local workspace.")
    with st.expander("＋ Create a task", expanded=not bool(st.session_state.tasks)):
        with st.form("new_task_form", clear_on_submit=True):
            title = st.text_input("Task title", placeholder="e.g. Finish the science project")
            details = st.text_area("Details (optional)", placeholder="What does done look like?")
            col1, col2, col3 = st.columns(3)
            priority = col1.selectbox("Priority", ["Low", "Normal", "High", "Urgent"], index=1)
            category = col2.selectbox("Category", ["Personal", "School", "Work", "Creative", "Health", "Other"])
            due = col3.date_input("Due date", value=date.today())
            submitted = st.form_submit_button("Add task", use_container_width=True)
            if submitted:
                if title.strip():
                    st.session_state.tasks.append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "title": title.strip(), "details": details.strip(), "priority": priority,
                        "category": category, "due": str(due), "done": False,
                        "created": datetime.now().isoformat(timespec="minutes")
                    })
                    persist_and_rerun()
                else:
                    st.error("Give the task a title first.")
    tasks = [normalize_task(t) for t in st.session_state.tasks]
    f1, f2, f3 = st.columns([1.4, 1, 1])
    query = f1.text_input("Search tasks", placeholder="Search title or details")
    status_filter = f2.selectbox("Status", ["All", "Open", "Completed"])
    priority_filter = f3.selectbox("Priority", ["All", "Low", "Normal", "High", "Urgent"])
    filtered = tasks
    if query:
        filtered = [t for t in filtered if query.lower() in (t["title"] + " " + t.get("details", "")).lower()]
    if status_filter == "Open":
        filtered = [t for t in filtered if not t["done"]]
    elif status_filter == "Completed":
        filtered = [t for t in filtered if t["done"]]
    if priority_filter != "All":
        filtered = [t for t in filtered if t["priority"] == priority_filter]
    open_tasks = sum(not t["done"] for t in tasks)
    completed_tasks = sum(t["done"] for t in tasks)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total", len(tasks)); m2.metric("Open", open_tasks); m3.metric("Completed", completed_tasks)
    st.progress(completed_tasks / max(len(tasks), 1), text="Overall completion")
    if not filtered:
        empty_state("Nothing to show", "Add a task or change your filters.")
    for task in sorted(filtered, key=lambda t: (t["done"], {"Urgent":0,"High":1,"Normal":2,"Low":3}.get(t["priority"],2), t["due"])):
        with st.container(border=True):
            cols = st.columns([.12, 2.2, .7, .75, .55])
            checked = cols[0].checkbox("Done", value=task["done"], key=f"task_done_{task['id']}", label_visibility="collapsed")
            title_label = f"~~{task['title']}~~" if checked else task["title"]
            cols[1].markdown(f"**{title_label}**")
            cols[1].caption(task.get("details", "") or f"{task['category']} · Due {task['due']}")
            cols[2].markdown(f"`{task['priority']}`")
            cols[3].caption(f"Due {task['due']}")
            if cols[4].button("Delete", key=f"del_task_{task['id']}"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                persist_and_rerun()
            if checked != task["done"]:
                task["done"] = checked
                persist_and_rerun()
    if tasks:
        st.download_button("Export tasks as CSV", csv_bytes(pd.DataFrame(tasks)), "nexus_tasks.csv", "text/csv")

# ----------------------------- NOTES & JOURNAL -----------------------------
elif page == "Notes & Journal":
    section_header("CAPTURE / REFLECT", "Notes & Journal", "A searchable notebook for rough ideas, useful snippets, and daily reflections.")
    tab1, tab2, tab3 = st.tabs(["Notes", "Daily journal", "Scratchpad"])
    with tab1:
        with st.form("note_form", clear_on_submit=True):
            note_title = st.text_input("Title", placeholder="A thought worth keeping")
            note_body = st.text_area("Write your note", height=160, placeholder="Start anywhere…")
            note_tags = st.text_input("Tags (comma-separated)", placeholder="ideas, school, project")
            if st.form_submit_button("Save note"):
                if note_title.strip() or note_body.strip():
                    st.session_state.notes.append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "title": note_title.strip() or "Untitled note", "body": note_body.strip(),
                        "tags": [x.strip() for x in note_tags.split(",") if x.strip()],
                        "updated": datetime.now().isoformat(timespec="minutes")
                    })
                    persist_and_rerun()
        search_note = st.text_input("Search notes", key="note_search", placeholder="Find words or tags")
        notes = st.session_state.notes
        if search_note:
            notes = [n for n in notes if search_note.lower() in (n["title"] + " " + n.get("body","") + " " + " ".join(n.get("tags",[]))).lower()]
        if not notes:
            empty_state("A blank page is a beginning", "Save a note above to start your notebook.")
        for note in reversed(notes):
            with st.expander(f"✎ {note['title']}  ·  {note.get('updated','')[:10]}"):
                st.write(note.get("body", ""))
                if note.get("tags"):
                    st.caption("Tags: " + " · ".join(note["tags"]))
                c1, c2 = st.columns([1, 5])
                if c1.button("Delete note", key=f"delete_note_{note['id']}"):
                    st.session_state.notes = [n for n in st.session_state.notes if n["id"] != note["id"]]
                    persist_and_rerun()
                c2.download_button("Download note", f"# {note['title']}\n\n{note.get('body','')}", f"{safe_filename(note['title'])}.md", "text/markdown", key=f"download_note_{note['id']}")
    with tab2:
        st.subheader("Daily reflection")
        with st.form("journal_form", clear_on_submit=True):
            journal_date = st.date_input("Date", value=date.today())
            mood = st.select_slider("How did the day feel?", options=["Rough", "Low-key", "Okay", "Good", "Great"], value="Okay")
            win = st.text_area("One thing that went well", placeholder="A tiny win counts.")
            improve = st.text_area("One thing to try tomorrow", placeholder="Keep it kind and specific.")
            if st.form_submit_button("Save reflection"):
                st.session_state.journal.append({
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "date": str(journal_date),
                    "mood": mood, "win": win.strip(), "improve": improve.strip()
                })
                persist_and_rerun()
        if st.session_state.journal:
            jdf = pd.DataFrame(st.session_state.journal).sort_values("date", ascending=False)
            st.dataframe(jdf[["date", "mood", "win", "improve"]], use_container_width=True, hide_index=True)
            st.download_button("Export journal", csv_bytes(jdf), "nexus_journal.csv", "text/csv")
        else:
            empty_state("Your reflections will appear here", "Try a quick check-in at the end of the day.")
    with tab3:
        st.subheader("Quick scratchpad")
        st.caption("Autosaves when you press Save scratchpad.")
        st.session_state.scratchpad = st.text_area("Temporary thoughts", value=st.session_state.scratchpad, height=260, label_visibility="collapsed")
        if st.button("Save scratchpad"):
            persist()
            st.success("Scratchpad saved.")

# ----------------------------- HABIT TRACKER -----------------------------
elif page == "Habit Tracker":
    section_header("CONSISTENCY / SMALL WINS", "Habit Tracker", "Track the repeatable actions that help your days feel more intentional.")
    today_key = str(date.today())
    with st.expander("＋ Add a habit", expanded=not bool(st.session_state.habits)):
        with st.form("habit_add_form", clear_on_submit=True):
            habit_name = st.text_input("Habit name", placeholder="e.g. Read for 10 minutes")
            habit_category = st.selectbox("Area", ["Learning", "Wellbeing", "Creative", "Home", "Other"])
            habit_goal = st.selectbox("Target frequency", ["Daily", "Weekdays", "A few times a week"])
            habit_note = st.text_input("Tiny reminder (optional)", placeholder="Make it easy to begin")
            if st.form_submit_button("Create habit"):
                if habit_name.strip():
                    st.session_state.habits.append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "name": habit_name.strip(), "category": habit_category,
                        "goal": habit_goal, "reminder": habit_note.strip(),
                        "checks": {}, "created": today_key
                    })
                    persist_and_rerun()
                else:
                    st.error("Give your habit a name first.")

    habits = st.session_state.habits
    checked_today = sum(1 for h in habits if h.get("checks", {}).get(today_key, False))
    h1, h2, h3 = st.columns(3)
    h1.metric("Habits in your list", len(habits))
    h2.metric("Completed today", checked_today)
    h3.metric("Today's completion", f"{checked_today / max(1, len(habits)):.0%}")
    st.progress(checked_today / max(1, len(habits)), text="Today's progress")
    if not habits:
        empty_state("Start with one small habit", "Choose something realistic enough that you can repeat it on an ordinary day.")
    for habit in habits:
        checks = habit.setdefault("checks", {})
        with st.container(border=True):
            col_check, col_info, col_streak, col_delete = st.columns([.25, 2.2, .8, .55])
            is_done = col_check.checkbox("Complete", value=bool(checks.get(today_key, False)), key=f"habit_check_{habit['id']}", label_visibility="collapsed")
            if is_done != bool(checks.get(today_key, False)):
                checks[today_key] = is_done
                persist_and_rerun()
            col_info.markdown(f"**{habit['name']}**")
            col_info.caption(f"{habit.get('category','Other')} · {habit.get('goal','Daily')}" + (f" · {habit.get('reminder')}" if habit.get('reminder') else ""))
            # Consecutive-day streak is counted backward from today.
            streak = 0
            cursor = date.today()
            while checks.get(str(cursor), False):
                streak += 1
                cursor -= timedelta(days=1)
            col_streak.metric("Current streak", f"{streak} day" if streak == 1 else f"{streak} days")
            if col_delete.button("Delete", key=f"habit_delete_{habit['id']}"):
                st.session_state.habits = [h for h in st.session_state.habits if h["id"] != habit["id"]]
                persist_and_rerun()

    if habits:
        st.divider()
        st.subheader("Last 14 days")
        days = [date.today() - timedelta(days=i) for i in range(13, -1, -1)]
        history_rows = []
        for habit in habits:
            row = {"Habit": habit["name"]}
            for day in days:
                row[day.strftime("%d %b")] = "✓" if habit.get("checks", {}).get(str(day), False) else "·"
            history_rows.append(row)
        st.dataframe(pd.DataFrame(history_rows), use_container_width=True, hide_index=True)
        all_checks = sum(sum(1 for val in h.get("checks", {}).values() if val) for h in habits)
        possible = len(habits) * 14
        st.caption(f"Total check-ins recorded: {all_checks}. A blank day is information, not failure—just begin again when you're ready.")
        habit_export = [{"name":h["name"], "category":h.get("category"), "goal":h.get("goal"), "checks":h.get("checks", {})} for h in habits]
        st.download_button("Export habit history", json.dumps(habit_export, indent=2), "nexus_habits.json", "application/json")

# ----------------------------- FOCUS STUDIO -----------------------------
elif page == "Focus Studio":
    section_header("ATTENTION / MOMENTUM", "Focus Studio", "Make a little protected space for one thing at a time.")
    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="nexus-card"><div class="nexus-kicker">FOCUS MODE</div><h2>One thing. For a while.</h2><div class="nexus-muted">Choose a session length, decide what matters, and begin.</div></div>', unsafe_allow_html=True)
        focus_task = st.text_input("What are you focusing on?", placeholder="e.g. Read 10 pages")
        minutes = st.select_slider("Session length", options=[5, 10, 15, 20, 25, 30, 45, 60, 90], value=st.session_state.focus_minutes)
        st.session_state.focus_minutes = minutes
        st.metric("Planned focus time", f"{minutes} minutes")
        st.caption("This page doesn't run a background timer. Use the session card as a commitment and mark it complete when you're done.")
        if st.button("✓ Mark session complete", use_container_width=True):
            st.session_state.completed_focus += 1
            persist()
            st.success(f"Nice work. Session #{st.session_state.completed_focus} logged.")
        if st.button("Reset session count"):
            st.session_state.completed_focus = 0
            persist_and_rerun()
    with right:
        st.subheader("Session ritual")
        ritual = [
            ("01", "Clear the runway", "Close unrelated tabs and put your phone aside."),
            ("02", "Pick one outcome", "Make the finish line small and visible."),
            ("03", "Work gently", "When your mind wanders, return to the next action."),
            ("04", "Close the loop", "Write down where to resume next time.")
        ]
        for n, title, body in ritual:
            st.markdown(f'<div class="nexus-card" style="margin-bottom:.6rem;min-height:auto"><span class="nexus-kicker">{n}</span><h3>{title}</h3><div class="nexus-muted">{body}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("Focus history")
    st.metric("Completed sessions", st.session_state.completed_focus)
    st.metric("Approximate focused minutes", st.session_state.completed_focus * st.session_state.focus_minutes)
    st.info("Tip: a 10-minute start is often easier than waiting for a perfect hour.")

# ----------------------------- DATA LAB -----------------------------
elif page == "Data Lab":
    section_header("EXPLORE / UNDERSTAND", "Data Lab", "Upload a CSV, inspect the data, explore distributions, and export a cleaned version.")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    sample = st.checkbox("Use sample dataset instead", value=uploaded is None)
    df = None
    if uploaded is not None and not sample:
        try:
            df = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")
    elif sample:
        rng = np.random.default_rng(7)
        df = pd.DataFrame({
            "day": pd.date_range(end=pd.Timestamp.today().normalize(), periods=60),
            "visitors": rng.integers(80, 260, 60),
            "conversions": rng.integers(5, 45, 60),
            "satisfaction": np.round(rng.normal(4.1, .45, 60).clip(1, 5), 2),
            "channel": rng.choice(["Search", "Social", "Direct", "Referral"], 60)
        })
    if df is not None:
        st.subheader("Dataset overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{df.shape[0]:,}")
        c2.metric("Columns", f"{df.shape[1]:,}")
        c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
        with st.expander("Data preview", expanded=True):
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)
        numeric = df.select_dtypes(include=np.number).columns.tolist()
        categorical = df.select_dtypes(exclude=np.number).columns.tolist()
        tab1, tab2, tab3 = st.tabs(["Statistics", "Charts", "Clean & export"])
        with tab1:
            if numeric:
                st.dataframe(df[numeric].describe().T, use_container_width=True)
                corr = df[numeric].corr()
                if len(numeric) > 1:
                    st.subheader("Correlation matrix")
                    st.dataframe(corr.style.format("{:.2f}"), use_container_width=True)
            else:
                st.info("No numeric columns found for statistical summaries.")
            st.subheader("Column quality")
            quality = pd.DataFrame({
                "Column": df.columns,
                "Type": [str(df[c].dtype) for c in df.columns],
                "Missing": [int(df[c].isna().sum()) for c in df.columns],
                "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns]
            })
            st.dataframe(quality, use_container_width=True, hide_index=True)
        with tab2:
            if numeric:
                xcol = st.selectbox("Horizontal axis", df.columns.tolist(), index=0)
                ycol = st.selectbox("Numeric value", numeric, index=0)
                chart_type = st.selectbox("Chart type", ["Line", "Bar", "Area", "Histogram"])
                chart_df = df[[xcol, ycol]].dropna()
                if chart_type == "Histogram":
                    st.bar_chart(chart_df[ycol].value_counts().sort_index())
                else:
                    chart_df = chart_df.set_index(xcol)
                    if chart_type == "Line":
                        st.line_chart(chart_df)
                    elif chart_type == "Bar":
                        st.bar_chart(chart_df)
                    else:
                        st.area_chart(chart_df)
            if categorical:
                catcol = st.selectbox("Categorical breakdown", categorical)
                st.bar_chart(df[catcol].fillna("Missing").value_counts().head(20))
        with tab3:
            st.caption("Choose simple cleanup operations, then download the result.")
            drop_duplicates = st.checkbox("Remove duplicate rows", value=True)
            drop_empty = st.checkbox("Drop rows that are entirely empty", value=True)
            fill_missing = st.selectbox("Missing-value handling", ["Leave as-is", "Fill numeric with median / text with mode", "Drop rows with any missing values"])
            cleaned = df.copy()
            if drop_duplicates:
                cleaned = cleaned.drop_duplicates()
            if drop_empty:
                cleaned = cleaned.dropna(how="all")
            if fill_missing.startswith("Fill"):
                for col in cleaned.columns:
                    if pd.api.types.is_numeric_dtype(cleaned[col]):
                        if cleaned[col].notna().any():
                            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
                    elif cleaned[col].notna().any():
                        cleaned[col] = cleaned[col].fillna(cleaned[col].mode().iloc[0])
            elif fill_missing.startswith("Drop"):
                cleaned = cleaned.dropna()
            st.write(f"Rows before: **{len(df)}** · Rows after: **{len(cleaned)}**")
            st.dataframe(cleaned.head(100), use_container_width=True, hide_index=True)
            st.download_button("Download cleaned CSV", csv_bytes(cleaned), "nexus_cleaned_data.csv", "text/csv")
    else:
        empty_state("Ready for your data", "Upload a CSV or enable the sample dataset.")

# ----------------------------- CALCULATOR SUITE -----------------------------
elif page == "Calculator Suite":
    section_header("CALCULATE / CONVERT", "Calculator Suite", "Practical number tools, with clear results and no mystery.")
    tabs = st.tabs(["Quick math", "Percentages", "Unit converter", "Scientific"])
    with tabs[0]:
        st.subheader("Expression calculator")
        expr = st.text_input("Expression", placeholder="e.g. (125 * 1.19) / 3")
        st.caption("Supports basic arithmetic, parentheses, powers, and a small set of math functions.")
        allowed_names = {k: getattr(math, k) for k in ["sqrt", "sin", "cos", "tan", "log", "log10", "ceil", "floor", "fabs", "pi", "e"]}
        allowed_names.update({"abs": abs, "round": round})
        if st.button("Calculate", key="quick_calc"):
            try:
                if not re.fullmatch(r"[0-9+\-*/().,% a-zA-Z_]+", expr):
                    raise ValueError("Use only numbers, arithmetic symbols, and supported math names.")
                safe_expr = expr.replace("^", "**").replace("%", "/100")
                result = eval(safe_expr, {"__builtins__": {}}, allowed_names)
                st.success(f"Result: {result}")
            except Exception as exc:
                st.error(f"Couldn't calculate that expression: {exc}")
    with tabs[1]:
        st.subheader("Percentage tools")
        mode = st.selectbox("I want to…", ["Find X% of a number", "Find what percent X is of Y", "Increase/decrease a number"])
        a, b = st.columns(2)
        if mode == "Find X% of a number":
            pct = a.number_input("Percentage (%)", value=15.0)
            val = b.number_input("Number", value=240.0)
            st.metric("Result", f"{val * pct / 100:,.4f}")
        elif mode == "Find what percent X is of Y":
            x = a.number_input("X", value=30.0)
            y = b.number_input("Y", value=120.0)
            st.metric("Result", "Undefined" if y == 0 else f"{x / y * 100:,.2f}%")
        else:
            val = a.number_input("Starting number", value=100.0)
            pct = b.number_input("Change (%) — use negative to decrease", value=12.0)
            st.metric("New value", f"{val * (1 + pct / 100):,.4f}")
            st.metric("Absolute change", f"{val * pct / 100:+,.4f}")
    with tabs[2]:
        st.subheader("Unit converter")
        unit_sets = {
            "Length": {"Millimeters": .001, "Centimeters": .01, "Meters": 1, "Kilometers": 1000, "Inches": .0254, "Feet": .3048, "Yards": .9144, "Miles": 1609.344},
            "Mass": {"Milligrams": .000001, "Grams": .001, "Kilograms": 1, "Ounces": .0283495, "Pounds": .453592},
            "Time": {"Seconds": 1, "Minutes": 60, "Hours": 3600, "Days": 86400},
            "Data": {"Bytes": 1, "Kilobytes": 1000, "Megabytes": 1_000_000, "Gigabytes": 1_000_000_000, "Kibibytes": 1024, "Mebibytes": 1024**2, "Gibibytes": 1024**3},
            "Speed": {"Meters/second": 1, "Kilometers/hour": 1/3.6, "Miles/hour": .44704},
        }
        category = st.selectbox("Category", list(unit_sets))
        units = list(unit_sets[category])
        c1, c2, c3 = st.columns([1, 1, .8])
        amount = c1.number_input("Value", value=1.0)
        from_unit = c2.selectbox("From", units, index=0)
        to_unit = c3.selectbox("To", units, index=min(1, len(units)-1))
        result = amount * unit_sets[category][from_unit] / unit_sets[category][to_unit]
        st.markdown(f'<div class="nexus-card"><div class="nexus-kicker">CONVERSION RESULT</div><div class="nexus-big">{result:,.8g}</div><div class="nexus-muted">{amount:g} {from_unit} = {result:,.8g} {to_unit}</div></div>', unsafe_allow_html=True)
    with tabs[3]:
        st.subheader("Scientific calculator")
        num = st.number_input("Number", value=9.0, key="scientific_number")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Square root", f"{math.sqrt(num):.6g}" if num >= 0 else "Not real")
            st.metric("Square", f"{num**2:.6g}")
        with col2:
            st.metric("Cube", f"{num**3:.6g}")
            st.metric("Absolute value", f"{abs(num):.6g}")
        with col3:
            st.metric("Log₁₀", f"{math.log10(num):.6g}" if num > 0 else "Undefined")
            st.metric("Reciprocal", f"{1/num:.6g}" if num != 0 else "Undefined")

# ----------------------------- CREATIVE STUDIO -----------------------------
elif page == "Creative Studio":
    section_header("MAKE / EXPERIMENT", "Creative Studio", "Generate palettes, test contrast, build gradients, and collect inspiration.")
    tabs = st.tabs(["Color lab", "Palette generator", "Gradient builder", "Idea spark"])
    with tabs[0]:
        st.subheader("Color inspector")
        chosen = st.color_picker("Choose a color", st.session_state.accent)
        st.session_state.accent = chosen
        r, g, b = hex_to_rgb(chosen)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("HEX", chosen.upper())
        c2.metric("RGB", f"{r}, {g}, {b}")
        c3.metric("HUE", f"{h*360:.1f}°")
        c4.metric("SATURATION", f"{s*100:.1f}%")
        st.markdown(f'<div style="height:100px;border-radius:16px;background:{chosen};border:1px solid #ffffff22"></div>', unsafe_allow_html=True)
        st.subheader("Contrast check")
        background = st.color_picker("Background color", "#FFFFFF", key="contrast_bg")
        ratio = contrast_ratio(chosen, background)
        st.metric("Contrast ratio", f"{ratio:.2f}:1")
        if ratio >= 7:
            st.success("Excellent contrast for normal text (AAA guideline).")
        elif ratio >= 4.5:
            st.success("Good contrast for normal text (AA guideline).")
        elif ratio >= 3:
            st.warning("May work for large text, but not normal text.")
        else:
            st.error("Low contrast. Try a lighter or darker color.")
        if st.button("Save this color to palettes"):
            st.session_state.saved_palettes.append({"name": "Picked color", "colors": [chosen]})
            persist()
            st.success("Color saved.")
    with tabs[1]:
        st.subheader("Palette generator")
        base_color = st.color_picker("Base color", "#8B5CF6", key="palette_base")
        scheme = st.selectbox("Harmony", ["Complementary", "Analogous", "Triadic", "Monochrome"])
        rr, gg, bb = [v/255 for v in hex_to_rgb(base_color)]
        hh, ss, vv = colorsys.rgb_to_hsv(rr, gg, bb)
        if scheme == "Complementary":
            hues = [hh, (hh+.5)%1]
        elif scheme == "Analogous":
            hues = [(hh-.08)%1, hh, (hh+.08)%1, (hh+.16)%1]
        elif scheme == "Triadic":
            hues = [hh, (hh+1/3)%1, (hh+2/3)%1]
        else:
            hues = [hh]*5
        colors = []
        for i, hue in enumerate(hues):
            sat = max(.25, min(1, ss * (1 if scheme != "Monochrome" else .8 - i*.12)))
            val = max(.25, min(1, vv * (1 if scheme != "Monochrome" else .45 + i*.13)))
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            colors.append("#%02X%02X%02X" % tuple(round(c*255) for c in rgb))
        cols = st.columns(len(colors))
        for i, color in enumerate(colors):
            with cols[i]:
                st.markdown(f'<div style="height:120px;background:{color};border-radius:12px;border:1px solid #ffffff22"></div><p style="text-align:center;font-family:monospace">{color}</p>', unsafe_allow_html=True)
                if st.button("Copy/save", key=f"save_palette_{i}"):
                    st.session_state.saved_palettes.append({"name": f"{scheme} palette", "colors": colors})
                    persist()
                    st.success("Palette saved.")
        st.download_button("Download palette JSON", json.dumps({"scheme":scheme,"colors":colors}, indent=2), "nexus_palette.json", "application/json")
    with tabs[2]:
        st.subheader("CSS gradient builder")
        gc1, gc2 = st.columns(2)
        color1 = gc1.color_picker("Start color", "#7C3AED")
        color2 = gc2.color_picker("End color", "#06B6D4")
        angle = st.slider("Angle", 0, 360, 135)
        gradient = f"linear-gradient({angle}deg, {color1}, {color2})"
        st.markdown(f'<div style="height:180px;border-radius:18px;background:{gradient};border:1px solid #ffffff22"></div>', unsafe_allow_html=True)
        css = f"background: {gradient};"
        st.code(css, language="css")
        st.download_button("Download CSS snippet", f".my-gradient {{\n  {css}\n}}", "nexus_gradient.css", "text/css")
    with tabs[3]:
        st.subheader("Idea spark")
        prompts = [
            "Design a tiny tool that saves someone five minutes every day.",
            "Invent a fictional museum for objects from the future.",
            "Create a personal dashboard for a character in a sci-fi story.",
            "Explain a complicated idea using only everyday objects.",
            "Build a website that feels like a place, not a page.",
            "Make a useful app for a problem people usually ignore.",
            "Imagine a new kind of notebook for people who think visually.",
            "Create a color palette inspired by a weather forecast.",
            "Turn one boring daily routine into a satisfying ritual.",
            "Design a public space for people who love quiet."
        ]
        if "idea_spark" not in st.session_state:
            st.session_state.idea_spark = random.choice(prompts)
        st.markdown(f'<div class="nexus-card"><div class="nexus-kicker">YOUR PROMPT</div><div style="font-size:1.5rem;font-weight:700;margin:.7rem 0">{st.session_state.idea_spark}</div></div>', unsafe_allow_html=True)
        if st.button("Generate another idea"):
            st.session_state.idea_spark = random.choice(prompts)
            st.rerun()
        if st.button("Save idea as a note"):
            st.session_state.notes.append({"id":datetime.now().strftime("%Y%m%d%H%M%S%f"),"title":"Idea spark","body":st.session_state.idea_spark,"tags":["inspiration"],"updated":datetime.now().isoformat(timespec="minutes")})
            persist_and_rerun()
    if st.session_state.saved_palettes:
        with st.expander("Saved palettes"):
            for i, pal in enumerate(st.session_state.saved_palettes):
                st.write(f"**{pal['name']}** — " + ", ".join(pal["colors"]))
                if st.button("Delete palette", key=f"delete_pal_{i}"):
                    st.session_state.saved_palettes.pop(i)
                    persist_and_rerun()

# ----------------------------- KNOWLEDGE HUB -----------------------------
elif page == "Knowledge Hub":
    section_header("COLLECT / CONNECT", "Knowledge Hub", "Keep useful links and build a personal library of things worth revisiting.")
    with st.form("bookmark_form", clear_on_submit=True):
        c1, c2 = st.columns([1.3, 1])
        title = c1.text_input("Resource name", placeholder="e.g. Python documentation")
        url = c2.text_input("URL", placeholder="https://...")
        description = st.text_area("Why is this useful?", height=80)
        category = st.selectbox("Collection", ["Learning", "Reference", "Inspiration", "Tools", "Reading", "Other"])
        if st.form_submit_button("Save resource"):
            if title.strip() and url.strip():
                if not re.match(r"^https?://", url.strip()):
                    url = "https://" + url.strip()
                st.session_state.bookmarks.append({"id":datetime.now().strftime("%Y%m%d%H%M%S%f"),"title":title.strip(),"url":url.strip(),"description":description.strip(),"category":category,"added":str(date.today())})
                persist_and_rerun()
            else:
                st.error("Add a name and URL.")
    q = st.text_input("Search library", placeholder="Search titles, notes, categories")
    cats = ["All"] + sorted({b.get("category","Other") for b in st.session_state.bookmarks})
    chosen_cat = st.selectbox("Filter collection", cats)
    bookmarks = st.session_state.bookmarks
    if q:
        bookmarks = [b for b in bookmarks if q.lower() in (b["title"] + " " + b.get("description","") + " " + b["url"]).lower()]
    if chosen_cat != "All":
        bookmarks = [b for b in bookmarks if b.get("category") == chosen_cat]
    if not bookmarks:
        empty_state("Your library is waiting", "Save a useful website above. You can filter and search it later.")
    for bm in bookmarks:
        with st.container(border=True):
            a, b = st.columns([4, 1])
            a.markdown(f"### [{bm['title']}]({bm['url']})")
            a.caption(f"{bm.get('category','Other')} · Added {bm.get('added','')}")
            if bm.get("description"):
                a.write(bm["description"])
            if b.button("Delete", key=f"del_bm_{bm['id']}"):
                st.session_state.bookmarks = [x for x in st.session_state.bookmarks if x["id"] != bm["id"]]
                persist_and_rerun()
    if st.session_state.bookmarks:
        st.download_button("Export library JSON", json.dumps(st.session_state.bookmarks, indent=2), "nexus_bookmarks.json", "application/json")

# ----------------------------- TEXT WORKSHOP -----------------------------
elif page == "Text Workshop":
    section_header("WRITE / TRANSFORM", "Text Workshop", "A practical toolkit for editing, inspecting, and transforming text locally.")
    tabs = st.tabs(["Text inspector", "Case converter", "Find & replace", "Slug & list tools"])
    with tabs[0]:
        text_input = st.text_area("Paste or write text", height=220, placeholder="Your text goes here…")
        words = re.findall(r"\b[\w'-]+\b", text_input)
        sentences = [s for s in re.split(r"[.!?]+", text_input) if s.strip()]
        paragraphs = [p for p in re.split(r"\n\s*\n", text_input) if p.strip()]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Characters", len(text_input))
        c2.metric("Words", len(words))
        c3.metric("Sentences", len(sentences))
        c4.metric("Paragraphs", len(paragraphs))
        if text_input:
            st.metric("Estimated reading time", f"{max(1, math.ceil(len(words)/220))} min")
            st.download_button("Download text", text_input, "nexus_text.txt", "text/plain")
    with tabs[1]:
        source = st.text_area("Text to convert", key="case_source", height=150)
        mode = st.selectbox("Convert to", ["UPPERCASE", "lowercase", "Title Case", "Sentence case", "Alternating cAsE"])
        if mode == "UPPERCASE":
            converted = source.upper()
        elif mode == "lowercase":
            converted = source.lower()
        elif mode == "Title Case":
            converted = source.title()
        elif mode == "Sentence case":
            converted = source[:1].upper() + source[1:].lower()
        else:
            converted = "".join(ch.upper() if i % 2 else ch.lower() for i, ch in enumerate(source))
        st.text_area("Result", value=converted, height=150)
        st.download_button("Download converted text", converted, "nexus_converted.txt", "text/plain")
    with tabs[2]:
        source = st.text_area("Original text", key="replace_source", height=160)
        old = st.text_input("Find", key="replace_old")
        new = st.text_input("Replace with", key="replace_new")
        replace_all = st.checkbox("Replace all occurrences", value=True)
        if old:
            result = source.replace(old, new) if replace_all else source.replace(old, new, 1)
        else:
            result = source
        st.text_area("Preview", value=result, height=160)
        st.download_button("Download result", result, "nexus_replaced.txt", "text/plain")
    with tabs[3]:
        phrase = st.text_input("Text for URL slug", placeholder="My New Project: Version 2")
        slug = re.sub(r"[^a-z0-9]+", "-", phrase.lower()).strip("-")
        st.code(slug or "your-slug")
        items_text = st.text_area("List items (one per line)", placeholder="first item\nsecond item\nthird item")
        items = [x.strip() for x in items_text.splitlines() if x.strip()]
        sort_items = st.checkbox("Sort alphabetically")
        unique_items = st.checkbox("Remove duplicates")
        if unique_items:
            items = list(dict.fromkeys(items))
        if sort_items:
            items = sorted(items, key=str.lower)
        st.code("\n".join(f"{i+1}. {item}" for i, item in enumerate(items)) or "Your formatted list appears here.")
        st.download_button("Download list", "\n".join(items), "nexus_list.txt", "text/plain")

# ----------------------------- UTILITY DECK -----------------------------
elif page == "Utility Deck":
    section_header("SMALL TOOLS / BIG LEVERAGE", "Utility Deck", "A collection of practical utilities for everyday decisions, dates, structured text, and quick planning.")
    utility_tabs = st.tabs(["Decision picker", "Date calculator", "List shuffler", "JSON formatter", "Regex tester", "Markdown preview"])

    with utility_tabs[0]:
        st.subheader("Decision picker")
        st.write("Give every option a fair chance when you're stuck between choices.")
        options_raw = st.text_area("Enter one option per line", placeholder="Make a playlist\nGo for a walk\nRead a chapter", height=130, key="decision_options")
        options = [line.strip() for line in options_raw.splitlines() if line.strip()]
        remove_duplicates = st.checkbox("Ignore duplicate options", value=True, key="decision_unique")
        if remove_duplicates:
            options = list(dict.fromkeys(options))
        if options:
            st.caption(f"{len(options)} option(s) ready")
        if st.button("🎲 Pick for me", key="decision_pick", use_container_width=True):
            if options:
                st.session_state.decision_result = random.choice(options)
            else:
                st.session_state.decision_result = "Add at least one option first."
        if st.session_state.get("decision_result"):
            st.markdown(f'<div class="nexus-card"><div class="nexus-kicker">THE PICK</div><div class="nexus-big">{st.session_state.decision_result}</div></div>', unsafe_allow_html=True)
        if st.button("Clear result", key="decision_clear"):
            st.session_state.decision_result = ""
            st.rerun()

    with utility_tabs[1]:
        st.subheader("Date calculator")
        date_mode = st.selectbox("Calculate", ["Days between dates", "Add days to a date", "Subtract days from a date"])
        if date_mode == "Days between dates":
            d1, d2 = st.columns(2)
            start = d1.date_input("Start date", value=date.today(), key="date_start")
            end = d2.date_input("End date", value=date.today() + timedelta(days=14), key="date_end")
            delta = (end - start).days
            st.metric("Difference", f"{abs(delta)} days")
            st.caption("The result is signed below: positive means the end date is later.")
            st.write(f"Signed difference: **{delta:+d} days**")
        else:
            base_date = st.date_input("Base date", value=date.today(), key="date_base")
            day_count = st.number_input("Number of days", min_value=0, max_value=100000, value=30, step=1, key="date_days")
            output_date = base_date + timedelta(days=int(day_count) * (1 if date_mode == "Add days to a date" else -1))
            st.markdown(f'<div class="nexus-card"><div class="nexus-kicker">RESULTING DATE</div><div class="nexus-big">{output_date.strftime("%A, %d %B %Y")}</div><div class="nexus-muted">{output_date.isoformat()}</div></div>', unsafe_allow_html=True)
        st.divider()
        st.subheader("Useful date facts")
        today = date.today()
        fact1, fact2, fact3 = st.columns(3)
        fact1.metric("Day of year", today.timetuple().tm_yday)
        fact2.metric("ISO week", today.isocalendar().week)
        fact3.metric("Leap year", "Yes" if (today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0)) else "No")

    with utility_tabs[2]:
        st.subheader("List shuffler and organizer")
        list_input = st.text_area("Paste a list, one item per line", height=160, key="shuffle_input", placeholder="Alpha\nBravo\nCharlie\nDelta")
        list_items = [item.strip() for item in list_input.splitlines() if item.strip()]
        options_row = st.columns(3)
        unique_only = options_row[0].checkbox("Remove duplicates", key="shuffle_unique")
        alphabetize = options_row[1].checkbox("Sort alphabetically", key="shuffle_sort")
        reverse_list = options_row[2].checkbox("Reverse order", key="shuffle_reverse")
        if unique_only:
            list_items = list(dict.fromkeys(list_items))
        if alphabetize:
            list_items = sorted(list_items, key=str.casefold)
        if reverse_list:
            list_items = list(reversed(list_items))
        st.caption(f"Current list: {len(list_items)} items")
        if st.button("Shuffle list", key="shuffle_go"):
            random.shuffle(list_items)
            st.session_state.shuffled_result = list_items
        if st.session_state.get("shuffled_result") is not None:
            result_items = st.session_state.shuffled_result
            st.code("\n".join(f"{i + 1}. {item}" for i, item in enumerate(result_items)) or "No items")
            st.download_button("Download shuffled list", "\n".join(result_items), "nexus_shuffled_list.txt", "text/plain")
        elif list_items:
            st.code("\n".join(f"{i + 1}. {item}" for i, item in enumerate(list_items)))
        if st.button("Clear shuffled result", key="shuffle_clear"):
            st.session_state.shuffled_result = None
            st.rerun()

    with utility_tabs[3]:
        st.subheader("JSON formatter and validator")
        json_source = st.text_area("Paste JSON", height=200, key="json_source", placeholder='{"project": "NEXUS", "active": true, "items": [1, 2, 3]}')
        json_indent = st.selectbox("Indentation", [2, 4, 8], index=0, format_func=lambda x: f"{x} spaces")
        if st.button("Validate and format JSON", key="json_format"):
            try:
                parsed = json.loads(json_source)
                st.session_state.formatted_json = json.dumps(parsed, ensure_ascii=False, indent=json_indent, sort_keys=False)
                st.session_state.json_error = ""
            except json.JSONDecodeError as exc:
                st.session_state.formatted_json = ""
                st.session_state.json_error = f"Line {exc.lineno}, column {exc.colno}: {exc.msg}"
        if st.session_state.get("json_error"):
            st.error(st.session_state.json_error)
        if st.session_state.get("formatted_json"):
            st.success("Valid JSON")
            st.code(st.session_state.formatted_json, language="json")
            st.download_button("Download formatted JSON", st.session_state.formatted_json, "formatted.json", "application/json")

    with utility_tabs[4]:
        st.subheader("Regular expression tester")
        st.write("Test a pattern against sample text. This tool shows matching spans and matched values.")
        pattern = st.text_input("Regex pattern", value=r"\b\w+\b", key="regex_pattern")
        regex_text = st.text_area("Sample text", value="NEXUS makes small tools feel connected. Version 2 is ready!", height=130, key="regex_text")
        regex_flags = st.multiselect("Flags", ["Ignore case", "Multiline", "Dot matches newline"], key="regex_flags")
        flag_value = 0
        if "Ignore case" in regex_flags:
            flag_value |= re.IGNORECASE
        if "Multiline" in regex_flags:
            flag_value |= re.MULTILINE
        if "Dot matches newline" in regex_flags:
            flag_value |= re.DOTALL
        if st.button("Run regex", key="regex_run"):
            try:
                compiled = re.compile(pattern, flag_value)
                matches = list(compiled.finditer(regex_text))
                st.session_state.regex_result = [{"match": m.group(0), "start": m.start(), "end": m.end(), "groups": list(m.groups())} for m in matches]
                st.session_state.regex_error = ""
            except re.error as exc:
                st.session_state.regex_result = []
                st.session_state.regex_error = str(exc)
        if st.session_state.get("regex_error"):
            st.error(st.session_state.regex_error)
        elif st.session_state.get("regex_result") is not None:
            result = st.session_state.regex_result
            st.metric("Matches found", len(result))
            if result:
                st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)
            elif st.session_state.get("regex_result") == []:
                st.info("No matches found for this pattern.")

    with utility_tabs[5]:
        st.subheader("Markdown preview")
        md_source = st.text_area("Write Markdown", value="# A little plan\n\n- First step\n- Second step\n\n**Keep it simple.**", height=220, key="markdown_source")
        preview_col, source_col = st.columns(2)
        with preview_col:
            st.markdown("#### Preview")
            st.markdown(md_source)
        with source_col:
            st.markdown("#### Source")
            st.code(md_source, language="markdown")
        st.download_button("Download Markdown", md_source, "nexus_document.md", "text/markdown")

# ----------------------------- SETTINGS & BACKUP -----------------------------
elif page == "Settings & Backup":
    section_header("CONFIGURE / PROTECT", "Settings & Backup", "Make NEXUS feel like yours, and keep an export of your workspace.")
    with st.form("settings_form"):
        username = st.text_input("Display name", value=st.session_state.username)
        theme_name = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))
        accent_color = st.color_picker("Accent color", st.session_state.accent)
        if st.form_submit_button("Apply settings"):
            st.session_state.username = username.strip() or "Explorer"
            st.session_state.theme = theme_name
            st.session_state.accent = accent_color
            persist()
            st.success("Settings saved. Refreshing the visual theme…")
            st.rerun()
    st.divider()
    st.subheader("Workspace backup")
    export_obj = {key: st.session_state[key] for key in DEFAULTS}
    st.download_button("⬇ Export full workspace backup", json.dumps(export_obj, ensure_ascii=False, indent=2, default=str), "nexus_workspace_backup.json", "application/json", use_container_width=True)
    imported = st.file_uploader("Restore from a NEXUS JSON backup", type=["json"])
    if imported is not None:
        if st.button("Restore backup", type="primary"):
            try:
                backup = json.load(imported)
                for key in DEFAULTS:
                    if key in backup:
                        st.session_state[key] = backup[key]
                persist()
                st.success("Backup restored.")
                st.rerun()
            except Exception as exc:
                st.error(f"That backup couldn't be read: {exc}")
    st.divider()
    st.subheader("Storage status")
    status = {
        "Storage mode": "Local JSON file",
        "File path": str(DATA_FILE),
        "Tasks": len(st.session_state.tasks),
        "Notes": len(st.session_state.notes),
        "Bookmarks": len(st.session_state.bookmarks),
        "Journal entries": len(st.session_state.journal),
    }
    st.dataframe(pd.DataFrame(list(status.items()), columns=["Setting", "Value"]), use_container_width=True, hide_index=True)
    st.warning("Local file storage is suitable for a personal prototype. On a hosted Streamlit app, the filesystem may reset during redeploys or restarts. Download backups regularly; use a database for durable multi-user storage.")
    if st.button("Reset workspace data", type="secondary"):
        st.session_state.confirm_reset = True
    if st.session_state.get("confirm_reset"):
        st.error("This will remove your saved tasks, notes, bookmarks, journal, and settings from the local workspace.")
        confirm = st.checkbox("I understand and want to reset the workspace")
        if st.button("Confirm permanent reset", disabled=not confirm):
            for key, value in DEFAULTS.items():
                st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value
            st.session_state.confirm_reset = False
            persist_and_rerun()

# ----------------------------- FOOTER -----------------------------
st.divider()
st.markdown(
    f'<div style="display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;color:{theme["muted"]};font-size:.8rem">'
    f'<span>◈ NEXUS OS · PERSONAL COMMAND CENTER</span>'
    f'<span>Built with Python + Streamlit · {datetime.now().strftime("%Y")}</span>'
    f'<span>Workspace changes save locally</span></div>',
    unsafe_allow_html=True
)

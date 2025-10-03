import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_calendar import calendar
from collections import Counter

st.set_page_config(page_title="Leave Management System", layout="wide")

# ====== Custom Theme (white + sky blue background + blue sidebar with fixed inputs) ======
page_bg = """
<style>
    body {
        background: linear-gradient(to bottom right, #87CEFA, #ffffff);
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background: linear-gradient(to bottom right, #87CEFA, #ffffff);
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #1e3c72, #2a5298);
        color: white;
    }
    /* Sidebar labels */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label {
        color: white !important;
        font-weight: bold;
    }
    /* Sidebar inputs (selectbox, text input, radio) */
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stSelectbox div[role="button"],
    section[data-testid="stSidebar"] .stRadio div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 5px;
        padding: 4px;
    }
    /* Dropdown listbox */
    section[data-testid="stSidebar"] .stSelectbox div[role="listbox"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ====== Demo public holidays (South Africa 2025 sample) ======
SA_PUBLIC_HOLIDAYS = [
    date(2025,1,1), date(2025,3,21), date(2025,4,18), date(2025,4,21),
    date(2025,4,27), date(2025,5,1), date(2025,6,16), date(2025,8,9),
    date(2025,9,24), date(2025,12,16), date(2025,12,25), date(2025,12,26)
]

# ====== Fake database ======
if "leave_requests" not in st.session_state:
    st.session_state.leave_requests = pd.DataFrame(columns=[
        "ID", "Employee", "Team", "Leave Type", "Start", "End", "Days",
        "Sick Note", "Status"
    ])

if "balances" not in st.session_state:
    st.session_state.balances = {
        "Amy Analyst": {"annual": 21, "sick": 30, "team": "Functional Office"},
        "Ben BA": {"annual": 21, "sick": 30, "team": "Integration Office"},
        "Cindy Cyber": {"annual": 21, "sick": 30, "team": "Cybersecurity Office"},
        "Adam Admin": {"annual": 21, "sick": 30, "team": "Admin Office"}
    }

# ====== Helpers ======
def working_days(start, end):
    return sum(1 for i in range((end - start).days + 1)
               if (start + timedelta(i)).weekday() < 5)

def team_events(team, person=None):
    """Return calendar events for team + personal leave highlighted."""
    events = []
    reqs = st.session_state.leave_requests
    team_reqs = reqs[reqs["Team"] == team]
    for _, r in team_reqs.iterrows():
        color = "#008080"  # teal for team leave
        if person and r["Employee"].lower() == person.lower():
            color = "#1E90FF"  # blue for personal leave
        events.append({
            "title": f"{r['Employee']} ({r['Leave Type']})",
            "start": str(r["Start"]),
            "end": str(r["End"]),
            "color": color
        })
    for h in SA_PUBLIC_HOLIDAYS:
        events.append({
            "title": "Public Holiday",
            "start": str(h),
            "end": str(h),
            "color": "#FFD700"  # gold for holidays
        })
    return events

# ====== Sidebar ======
role = st.sidebar.radio("Login As:", ["Employee", "Manager", "HR", "Payroll"])
team = st.sidebar.selectbox("Select Team", ["Functional Office", "Integration Office", "Cybersecurity Office", "Admin Office"])
employee = st.sidebar.text_input("Enter Your Name (e.g., Amy Analyst)")
st.sidebar.write(f"👤 Role: **{role}**, 🏢 Team: **{team}**")

# ====== Tabs ======
tabs = st.tabs(["Apply for Leave", "Leave Balance", "Leave History", "Team Availability"])

# ---------------- Apply for Leave ----------------
with tabs[0]:
    st.header("Apply for Leave")
    if role in ["Employee", "Manager"] and employee:
        leave_type = st.selectbox("Leave Type", ["ANNUAL", "SICK", "FAMILY", "MATERNITY", "PATERNITY", "UNPAID"])
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today())
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        days = working_days(start_date, end_date)
        balance = st.session_state.balances.get(employee, {}).get(
            leave_type.lower() if leave_type in ["ANNUAL","SICK"] else "annual", 0
        )
        st.info(f"📊 Current balance for {leave_type}: {balance} days")
        sick_note_file = None
        if leave_type == "SICK" and days >= 3:
            st.warning("⚠️ Sick leave ≥ 3 days requires a doctor's note.")
            sick_note_file = st.file_uploader("Upload Sick Note", type=["pdf", "jpg", "png"])
        if st.button("Submit Request"):
            if days > balance:
                st.error("❌ Request exceeds your leave balance.")
            elif leave_type == "SICK" and days >= 3 and not sick_note_file:
                st.error("❌ Doctor's note required.")
            else:
                req_id = len(st.session_state.leave_requests) + 1
                new_row = {
                    "ID": req_id,
                    "Employee": employee,
                    "Team": team,
                    "Leave Type": leave_type,
                    "Start": start_date,
                    "End": end_date,
                    "Days": days,
                    "Sick Note": "Yes" if sick_note_file else "No",
                    "Status": "Pending Manager"
                }
                st.session_state.leave_requests = pd.concat(
                    [st.session_state.leave_requests, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                if employee in st.session_state.balances:
                    st.session_state.balances[employee][leave_type.lower() if leave_type in ["ANNUAL","SICK"] else "annual"] -= days
                st.success(f"✅ Request #{req_id} submitted!")
    else:
        st.info("Only Employees or Managers with a valid name can submit leave requests.")

# ---------------- Leave Balance ----------------
with tabs[1]:
    st.header("Leave Balance")
    if role in ["Employee", "Manager"] and employee in st.session_state.balances:
        personal_balance = st.session_state.balances[employee]
        st.subheader(f"{employee}")
        st.write(f"🌴 Annual Leave: {personal_balance['annual']} days remaining")
        st.write(f"🤒 Sick Leave (36-month cycle): {personal_balance['sick']} days remaining")
    elif role == "HR":
        for emp, bal in st.session_state.balances.items():
            st.subheader(emp)
            st.write(f"🌴 Annual Leave: {bal['annual']} days remaining")
            st.write(f"🤒 Sick Leave: {bal['sick']} days remaining")

# ---------------- Leave History ----------------
with tabs[2]:
    st.header("Leave History")
    if role in ["Employee", "Manager"] and employee:
        my_history = st.session_state.leave_requests[st.session_state.leave_requests["Employee"].str.lower() == employee.lower()]
        st.dataframe(my_history)
    elif role == "HR":
        st.dataframe(st.session_state.leave_requests)

# ---------------- Team Availability ----------------
with tabs[3]:
    st.header(f"Team Availability — {team}")
    events = team_events(team, employee if employee else None)
    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "height": "700px"
    }
    calendar(events=events, options=calendar_options)

    # AI Insights
    st.subheader("🤖 AI Availability Insights")
    if events:
        leave_days = [e["start"] for e in events if e["title"] != "Public Holiday"]
        counts = Counter(leave_days)
        busy_days = [d for d, c in counts.items() if c >= 2]
        if busy_days:
            st.warning(f"⚠️ High leave load on: {', '.join(busy_days)}")
            for bd in busy_days:
                bd_date = date.fromisoformat(bd)
                suggestion = bd_date + timedelta(days=7)
                st.info(f"💡 Consider {suggestion} instead of {bd_date}.")
        overlap_holidays = [h for h in SA_PUBLIC_HOLIDAYS if str(h) in leave_days]
        if overlap_holidays:
            st.info(f"📅 Leave overlaps with holidays: {', '.join(str(h) for h in overlap_holidays)}")
    else:
        st.info("No leave events yet. All dates available.")
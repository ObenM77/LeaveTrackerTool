import streamlit as st 
import pandas as pd

# --- Custom Victorian / Elegant CSS ---
st.markdown("""
    <style>
    /* General App Styling */
    .stApp {
        font-family: 'Playfair Display', 'Cormorant Garamond', serif;
        color: #2c2c2c;
    }

    /* Headings */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        letter-spacing: 1px;
        color: #1a1a1a;
    }

    /* Dashboard Background */
    .dashboard {
        background: linear-gradient(to bottom right, #87ceeb, #e0f7fa);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.2);
    }

    /* White Card Style for other pages */
    .white-bg {
        background: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 1px 1px 6px rgba(0,0,0,0.1);
    }

    /* Animated Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4682b4, #87ceeb);
        color: white;
        border-radius: 10px;
        border: none;
        font-size: 16px;
        font-weight: bold;
        padding: 0.6em 1.2em;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }

    div.stButton > button:hover {
        transform: scale(1.08);
        background: linear-gradient(135deg, #5dade2, #3498db);
        box-shadow: 4px 4px 12px rgba(0,0,0,0.4);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fbff;
        border-right: 2px solid #cfd8dc;
    }
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
st.image(r"C:\Users\nomfi\OneDrive\Desktop\Kion\Functional\vacation work\python\calculators\kion logo.jfif", 
         width=160)

# --- Initialize session state ---
if "leave_balance" not in st.session_state:
    st.session_state.leave_balance = {
        "Annual Leave": 21,
        "Sick Leave": 10,
        "Study Leave": 14,
        "Family Responsility Leave": 7,
        "Maternity Leave": 120
    }

if "leave_requests" not in st.session_state:
    st.session_state.leave_requests = pd.DataFrame(columns=["Type", "Start Date", "End Date", "Days", "Status"])


# --- Sidebar Navigation ---
st.sidebar.title("📌 Kion Leave Tracker Tool")
menu = st.sidebar.radio("Menu", ["Dashboard", "Request Leave", "Leave History"])


# --- Dashboard ---
if menu == "Dashboard":
    st.markdown('<div class="dashboard">', unsafe_allow_html=True)
    st.title("📊 Leave Dashboard")

    st.subheader("Your Leave Balances")
    col1, col2 = st.columns(2)
    for i, (leave_type, balance) in enumerate(st.session_state.leave_balance.items()):
        with (col1 if i % 2 == 0 else col2):
            st.metric(label=leave_type, value=f"{balance} days")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Request Leave ---
elif menu == "Request Leave":
    st.markdown('<div class="white-bg">', unsafe_allow_html=True)
    st.title("📝 Request Leave")

    leave_type = st.selectbox("Select Leave Type", list(st.session_state.leave_balance.keys()))
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if start_date > end_date:
        st.error("⚠️ End date cannot be before start date")
    else:
        days_requested = (end_date - start_date).days + 1

        st.write(f"📅 Days Requested: {days_requested}")

        if st.button("Submit Request"):
            if days_requested <= st.session_state.leave_balance[leave_type]:
                st.session_state.leave_balance[leave_type] -= days_requested
                new_request = pd.DataFrame({
                    "Type": [leave_type],
                    "Start Date": [start_date],
                    "End Date": [end_date],
                    "Days": [days_requested],
                    "Status": ["Approved ✅"]
                })
                st.session_state.leave_requests = pd.concat([st.session_state.leave_requests, new_request], ignore_index=True)
                st.success("✅ Leave request submitted and approved!")
            else:
                st.error("❌ Not enough leave days available!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Leave History ---
elif menu == "Leave History":
    st.markdown('<div class="white-bg">', unsafe_allow_html=True)
    st.title("📅 Leave History")

    if st.session_state.leave_requests.empty:
        st.info("No leave requests yet.")
    else:
        st.dataframe(st.session_state.leave_requests, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


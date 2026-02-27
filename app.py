import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from utils import generate_ai_insight, generate_pdf

st.set_page_config(page_title="Premium AI Dashboard", layout="wide")

# -------- Background --------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, lightgreen, skyblue);
}
</style>
""", unsafe_allow_html=True)

# -------- User File Setup --------
USER_FILE = "users_data.csv"

if not os.path.exists(USER_FILE):
    df = pd.DataFrame(columns=["username", "password"])
    df.to_csv(USER_FILE, index=False)

# -------- Session States --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# -------- Login Page --------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = pd.read_csv(USER_FILE)

        if ((users["username"] == username) &
            (users["password"] == password)).any():

            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

    if st.button("Create New Account"):
        st.session_state.page = "register"
        st.rerun()

# -------- Register Page --------
def register_page():
    st.title("📝 Register")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Register"):
        users = pd.read_csv(USER_FILE)

        if new_user in users["username"].values:
            st.error("Username already exists")
        else:
            new_data = pd.DataFrame([[new_user, new_pass]],
                                    columns=["username", "password"])
            new_data.to_csv(USER_FILE, mode="a", header=False, index=False)
            st.success("Registration Successful! Please Login.")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# -------- Page Control --------
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        register_page()
    st.stop()

# =========================================================
# ================= DASHBOARD STARTS ======================
# =========================================================

st.title("🚀 Premium AI Business Dashboard")

uploaded_file = st.file_uploader("Upload Excel/CSV File", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
else:
    st.warning("Upload a CSV file to continue.")
    st.stop()

required_cols = ["Date", "Region", "Category", "Sales", "Expense"]
if not all(col in data.columns for col in required_cols):
    st.error("CSV must contain: Date, Region, Category, Sales, Expense")
    st.stop()

data["Date"] = pd.to_datetime(data["Date"])
data["Profit"] = data["Sales"] - data["Expense"]
data["Month"] = data["Date"].dt.to_period("M").astype(str)

# -------- Filters --------
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Region",
    data["Region"].unique(),
    default=data["Region"].unique()
)

category = st.sidebar.multiselect(
    "Category",
    data["Category"].unique(),
    default=data["Category"].unique()
)

filtered = data[
    (data["Region"].isin(region)) &
    (data["Category"].isin(category))
]

# -------- KPI --------
total_sales = filtered["Sales"].sum()
total_expense = filtered["Expense"].sum()
total_profit = filtered["Profit"].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"₹{total_sales:,.0f}")
col2.metric("Total Expense", f"₹{total_expense:,.0f}")
col3.metric("Total Profit", f"₹{total_profit:,.0f}")
col4.metric("Profit Margin", f"{profit_margin:.2f}%")

st.divider()

# -------- Charts --------
st.subheader("Sales by Region")
st.bar_chart(filtered.groupby("Region")["Sales"].sum())

st.subheader("Sales by Category")
st.bar_chart(filtered.groupby("Category")["Sales"].sum())

st.subheader("Monthly Trend")
st.line_chart(filtered.groupby("Month")["Sales"].sum())

# -------- Forecast --------
st.subheader("📈 Sales Forecast")

monthly = filtered.groupby("Month")["Sales"].sum().reset_index()
monthly["Index"] = np.arange(len(monthly))

if len(monthly) > 2:
    model = LinearRegression()
    model.fit(monthly[["Index"]], monthly["Sales"])

    future_index = np.arange(len(monthly), len(monthly) + 3).reshape(-1, 1)
    forecast = model.predict(future_index)

    forecast_df = pd.DataFrame({
        "Index": future_index.flatten(),
        "Forecast": forecast
    })

    st.line_chart(monthly.set_index("Index")["Sales"])
    st.line_chart(forecast_df.set_index("Index")["Forecast"])

# -------- AI Insight --------
top_region = filtered.groupby("Region")["Sales"].sum().idxmax()
insight = generate_ai_insight(total_sales, profit_margin, top_region)

st.subheader("🤖 AI Insight")
st.success(insight)

# -------- Export --------
st.subheader("⬇ Export Data")

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_data.csv")

# -------- PDF --------
if st.button("Generate PDF Report"):
    file = generate_pdf(filtered)
    with open(file, "rb") as f:
        st.download_button("Download PDF", f, file_name="report.pdf")

st.caption("Premium AI Dashboard | Streamlit Enterprise Version")
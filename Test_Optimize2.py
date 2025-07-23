import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
import requests
import io
import time
from scipy.optimize import linprog
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary


# Set Streamlit to wide layout
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .appview-container .main {
        max-width: 1100px !important; /* Adjust width as needed */
        margin: auto;
    }
    .block-container {
        max-width: 1100px !important; /* Adjust width as needed */
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to set black background with black font for login inputs
def set_black_background():
    bg_style = """
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    .stTextInput input, .stTextArea textarea {
        color: black;
        background-color: white;
    }
    .stButton>button {
        color: black;
    }
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)

# List of valid usernames and passwords
valid_users = {
    "mbcs": "1234",
    "mbcs1": "5678",
    "admin": "adminpass"  # Add more users if needed
}

# If user is NOT logged in, show login page with black background
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    set_black_background()  # Set black background
    
    # Logo image (Google Drive direct link)
    # logo_url = "https://i.postimg.cc/x1JFDk6P/Nest.webp"
    logo_url = "https://i.postimg.cc/85nTdNSr/Nest-Logo2.jpg"
    st.markdown(f"<div style='text-align: center;'><img src='{logo_url}' width='200'></div>", unsafe_allow_html=True)

    # Title with larger and bold text
    st.markdown("<h1 style='text-align: center; color: white;'>🔒 WELCOME TO NEST OPTIMIZED TOOL</h1>", unsafe_allow_html=True)

    # Bold and white color for the input labels
    st.markdown("<h3 style='color: white; font-weight: bold;'>Username</h3>", unsafe_allow_html=True)
    username = st.text_input("", key="username")
    
    st.markdown("<h3 style='color: white; font-weight: bold;'>Password</h3>", unsafe_allow_html=True)
    password = st.text_input("", type="password", key="password")

    # Login button
    if st.button("Login"):
        if username in valid_users and password == valid_users[username]:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Incorrect username or password. Please try again.")
    
    st.stop()  # Stop execution if not logged in

#function to add logo
def show_logo(centered=True, width=200):
    logo_url = "https://i.postimg.cc/85nTdNSr/Nest-Logo2.jpg"
    if centered:
        st.markdown(f"<div style='text-align: center;'><img src='{logo_url}' width='{width}'></div>", unsafe_allow_html=True)
    else:
        st.image(logo_url, width=width)

# After login, show main content
show_logo(centered=True, width=150)
st.write("🎉 Welcome! You are now logged in.")

# ---------- SESSION STATE FOR DATA SHARING ----------
if 'inputs' not in st.session_state:
    st.session_state.inputs = {
        'VIP': 0,
        'Mega': 0,
        'Macro': 0,
        'Mid': 0,
        'Micro': 0,
        'Nano': 0
    }

if 'page' not in st.session_state:
    st.session_state.page = 'Simulation Budget'  # Default page

# ---------- FUNCTION TO CHANGE PAGE ----------
def change_page(page_name):
    st.session_state.page = page_name

st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
        border-radius: 8px;
        background-color: #000000;
        color: white;
        border: none;
        transition: background-color 0.3s, color 0.3s;
        white-space: nowrap;  /* Prevents wrapping */
    }

    .stButton>button:hover {
        background-color: #333333;
        color: #ffffff;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- TOP NAVIGATION BUTTONS ----------
st.markdown("### 📁 Welcome To MBCS Optimize Tool")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Equal column widths

with col1:
    if st.button("📂 Simulation Budget"):
        change_page("Simulation Budget")

with col2:
    if st.button("💰 Influencer Performance"):
        change_page("Influencer Performance")

with col3:
    if st.button("📋 Optimized Budget"):
        change_page("Optimized Budget")

with col4:
    if st.button("🤖 GEN AI"):
        change_page("GEN AI")

with col5:
    if st.button("📊 Dashboard"):
        change_page("Dashboard")

# ---------- FUNCTION: Load Weights from Google Sheet CSV ----------
@st.cache_data
def load_weights(csv_url):
    df = pd.read_csv(csv_url)
    return df

# Load weights from the published Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/1CG19lrXCDYLeyPihaq4xwuPSw86oQUNB/export?format=csv"
weights_df = load_weights(csv_url)

# ---------- PAGE 1: Initialize session state ----------
if 'page' not in st.session_state:
    st.session_state.page = "Simulation Budget"
if 'inputs' not in st.session_state:
    st.session_state.inputs = {'VIP': 0, 'Mega': 0, 'Macro':0,'Mid': 0, 'Micro': 0, 'Nano': 0}
if 'category' not in st.session_state:
    st.session_state.category = weights_df['Category'].unique()[0]  # default first category

# ---------- PAGE 1: INPUT DATA ----------
if st.session_state.page == "Simulation Budget":
    st.title("📊 Simulation Budget")

    # Safe initialization of category in session state
    available_categories = sorted(weights_df['Category'].unique())
    if 'category' not in st.session_state or st.session_state.category not in available_categories:
        st.session_state.category = available_categories[0]  # default to first valid category

    # Category dropdown
    category = st.selectbox("Select Category:", available_categories, index=available_categories.index(st.session_state.category))
    st.session_state.category = category

    # Get input values from session state
    vip = st.session_state.inputs['VIP']
    mega = st.session_state.inputs['Mega']
    macro = st.session_state.inputs['Macro']
    mid = st.session_state.inputs['Mid']
    micro = st.session_state.inputs['Micro']
    nano = st.session_state.inputs['Nano']

    # Get weights from dataframe
    def get_weights(kpi):
        filtered = weights_df[(weights_df['Category'] == category) & (weights_df['KPI'] == kpi)]
        return {row['Tier']: row['Weights'] for _, row in filtered.iterrows()}

    impression_weights = get_weights("Impression")
    view_weights = get_weights("View")
    engagement_weights = get_weights("Engagement")

    # Total budget
    total_sum = vip + mega + macro + mid + micro + nano

    # KPI calculations
    total_impressions = sum(st.session_state.inputs[k] * impression_weights.get(k, 0) for k in st.session_state.inputs)
    total_views = sum(st.session_state.inputs[k] * view_weights.get(k, 0) for k in st.session_state.inputs)
    total_engagement = sum(st.session_state.inputs[k] * engagement_weights.get(k, 0) for k in st.session_state.inputs)

    # Display summary metrics
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-around; padding: 15px; background-color: #f0f2f6; 
                    color: black; border-radius: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); text-align: center;">
            <div>
                <h4>📢 Total Impressions</h4>
                <h2 style="color:#2196F3;">{total_impressions:,.0f}</h2>
            </div>
            <div>
                <h4>👀 Total Views</h4>
                <h2 style="color:#FF9800;">{total_views:,.0f}</h2>
            </div>
            <div>
                <h4>💬 Total Engagement</h4>
                <h2 style="color:#E91E63;">{total_engagement:,.0f}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)

    # Layout with input fields
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Enter Data")
        new_values = {}
        for category_tier in ['VIP', 'Mega', 'Macro', 'Mid', 'Micro', 'Nano']:
            cols = st.columns([3, 1])
            new_values[category_tier] = cols[0].number_input(
                f"{category_tier}", min_value=0, value=st.session_state.inputs[category_tier], key=category_tier
            )
            percentage = (new_values[category_tier] / total_sum * 100) if total_sum > 0 else 0
            cols[1].markdown(f"""
                <div style='text-align:center; margin-bottom:5px; font-size:14px; color:#555;'>%</div>
                <div style='display:flex; align-items:center; justify-content:center; height:40px; 
                            width:100%; border-radius:5px; border:1px solid #ddd; padding:5px; text-align:center; line-height: 35px;'>
                    {percentage:.2f}%
                </div>
            """, unsafe_allow_html=True)

        # Update session state if user input changes
        if new_values != st.session_state.inputs:
            st.session_state.inputs = new_values
            st.rerun()

    with col2:
        st.subheader("💰 Total Budget")
        st.markdown(
            f"""
            <div style="background-color:#f0f2f6;padding:20px;border-radius:10px;text-align:center;
                        box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                <h3>💰 Budget</h3>
                <h1 style="color:#4CAF50;">{total_sum}</h1>
            </div>
            """, unsafe_allow_html=True
        )

# ---------- PAGE 2: Influencer Performance ----------

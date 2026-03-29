import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- CONFIGURATION ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("Secrets missing! Please check Streamlit Advanced Settings.")
    st.stop()

# Gemini AI Setup - Using the most compatible model name
genai.configure(api_key=GEMINI_API_KEY)
# 'gemini-1.0-pro' purane API versions ke saath sabse best chalta hai
model = genai.GenerativeModel('gemini-1.0-pro')

def save_to_sheets(input_query, ai_response):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        row = [str(datetime.now()), str(input_query)[:500], "AI Analysis", str(ai_response)[:2000]]
        sheet.append_row(row)
        return True
    except: return False

# --- UI ---
st.set_page_config(page_title="Bruncash YouTube AI", page_icon="🚀")
st.title("🚀 Bruncash YouTube AI Genius")

user_input = st.text_area("YouTube Link ya Sawal dalo:", placeholder="Ask anything...")

if st.button("Generate Strategy"):
    if user_input:
        with st.spinner("AI processing..."):
            try:
                # Stable generation call
                response = model.generate_content(f"Hinglish mein detail mein jawab do: {user_input}")
                result = response.text
                
                st.markdown("### 💡 AI Strategy Insights")
                st.write(result)
                
                if save_to_sheets(user_input, result):
                    st.success("Data saved to Google Sheet! ✅")
            except Exception as e:
                # Agar abhi bhi error aaye, toh ye dikhayega
                st.error(f"System Error: {e}")
    else:
        st.warning("Please enter something!")user_input = st.text_area("YouTube Link ya Sawal dalo:", placeholder="Ask anything about YouTube...")

if st.button("Generate Strategy"):
    if user_input:
        with st.spinner("AI Brainstorming..."):
            try:
                # Direct AI Response for everything
                prompt = f"Tum ek YouTube Expert Guru ho. Hinglish mein detail mein jawab do: {user_input}. Agar channel ka pucha hai toh details do, agar topic rank pucha hai toh strategy batao."
                response = model.generate_content(prompt)
                result = response.text
                
                st.markdown("### 💡 AI Strategy Insights")
                st.write(result)
                
                if save_to_sheets(user_input, result):
                    st.success("Saved to YT_History! ✅")
            except Exception as e:
                st.error(f"Error: {e}")

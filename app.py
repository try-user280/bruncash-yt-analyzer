import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP & SECRETS ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("❌ Secrets Missing: Streamlit Advanced Settings mein keys check karein!")
    st.stop()

# Model setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. GOOGLE SHEETS SAVING ---
def save_to_sheets(query, response_text):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        row = [str(datetime.now()), str(query)[:500], "Bruncash 2025 Master Analysis", str(response_text)[:2500]]
        sheet.append_row(row)
        return True
    except:
        return False

# --- 3. UI DASHBOARD ---
st.set_page_config(page_title="Bruncash 2025 AI Master", page_icon="🔥", layout="wide")
st.title("💎 Bruncash 2025 YouTube AI Master")
st.markdown("Video Link dalo ya YouTube ka koi bhi sawal pucho. Ye All-in-One AI sabka jawab dega!")

# Box for user to type (Ab ye upar hai taaki error na aaye)
user_input = st.text_area("Yahan Paste Karein (Link, Channel Name, ya Sawal):", 
                          placeholder="Example: https://youtube.com/shorts/... ya 'Aajjubhai ke subs?'", 
                          height=150)

# Main Button
if st.button("🚀 Analyze & Generate Strategy"):
    
    # Check if box is empty
    if not user_input.strip():
        st.warning("⚠️ Bhai, pehle upar box mein kuch likho ya link dalo!")
    else:
        with st.spinner("⏳ AI Brainstorming kar raha hai..."):
            try:
                # Regular Expression to check if it's a YouTube Link
                v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", user_input)
                
                if v_id_match:
                    # --- VIDEO ANALYSIS MODE ---
                    v_id = v_id_match.group(1)
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        title = item['snippet']['title']
                        views = item['statistics'].get('viewCount', '0')
                        
                        prompt = f"Tum ek YouTube SEO Expert ho. Is video ka post-mortem karo: Title: {title}, Views: {views}. Hinglish mein report do: 1. Viral Factor, 2. SEO Score, 3. 5 Viral Titles, 4. 20 Rankable Tags."
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video Analysis: {title}")
                    else:
                        st.error("Video data nahi mila! Shayad link galat hai.")
                        st.stop()
                else:
                    # --- GENERAL AI MODE (Aajjubhai, Trending, etc.) ---
                    prompt = f"Tum ek YouTube Strategy Guru ho. User ka sawal hai: '{user_input}'. Isko detail mein Hinglish mein samjhao. Agar channel (jaise Aajjubhai) ke bare mein pucha hai toh unki details aur growth batao. Agar topics pucha hai toh best niches batao."
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy & Insights")

                # Print Result
                st.markdown(result)
                
                # Save to Sheets
                if save_to_sheets(user_input, result):
                    st.success("✅ Analysis successfully saved to 'YT_History' Sheet!")
                    
            except Exception as e:
                st.error(f"❌ System Error: {e}")                        2. **SEO Score**: 100 mein se kitna hai?
                        3. **5 Viral Titles**: High CTR wale options.
                        4. **20 Rankable Tags**: Jo search mein kaam aayein.
                        5. **Retention Strategy**: Log is video ko end tak kyun dekhein?
                        """
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video Analysis: {title}")
                    else:
                        st.error("Video data nahi mila! Shayad link galat hai.")
                        st.stop()
                else:
                    # --- MODE 2: General YouTube Consulting ---
                    prompt = f"""
                    Tum ek YouTube Strategy Guru ho. User ka sawal hai: '{user_input}'
                    Isko bahut details mein Hinglish mein samjhao. 
                    - Agar kisi channel ke bare mein pucha hai (jaise Aajjubhai, MrBeast), toh unka content style aur subscriber growth batao.
                    - Agar trending topics pucha hai, toh current year ke top niches aur keyword strategy do.
                    - Jawab point-by-point hona chahiye aur atleast 400-500 words ka detail report do.
                    - Beginner se lekar Pro level tak ki tips shamil karo.
                    """
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy & Insights")

                # Results Display
                st.markdown(result)
                
                # Auto-save to Google Sheets
                if save_to_sheets(user_input, result):
                    st.success("✅ Analysis successfully saved to 'YT_History' Sheet!")
                
            except Exception as e:
                st.error(f"❌ System Error: {e}")
    else:
        st.warning("⚠️ Bhai, kuch toh likho ya link dalo!")

# Sidebar Info
st.sidebar.markdown("### 🛠️ Tool Capabilities")
st.sidebar.write("- Video SEO Audit")
st.sidebar.write("- Channel Strategy")
st.sidebar.write("- Trending Topic Finder")
st.sidebar.write("- Unlimited Questions")
st.sidebar.info("Developed by Brun [Jamshedpur] 🚀")
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

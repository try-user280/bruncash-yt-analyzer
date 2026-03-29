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
    st.error("Secrets not found! Advanced Settings check karein.")
    st.stop()

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def save_to_sheets(input_query, ai_response):
    """Sari activity YT_History mein save hogi"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        
        row = [str(datetime.now()), input_query[:500], "Advanced AI Analysis", "System", ai_response[:2000]]
        sheet.append_row(row)
        return True
    except: return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bruncash YouTube Genius", page_icon="🔥", layout="wide")

# Custom CSS for better look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #FF0000; color: white; }
    </style>
    """, unsafe_allow_status_with_html=True)

st.title("🚀 Bruncash YouTube AI Genius")
st.markdown("YouTube ke bare mein kuch bhi puche - Video Link, Channel Analysis, ya Trending Topics!")

# User Input
user_input = st.text_area("YouTube Link dalo ya apna sawal likho (e.g. 'Best gaming topics right now'):", placeholder="Paste link or ask anything...")

if st.button("Generate Advanced Insights"):
    if user_input:
        # Check if input is a YouTube Link
        v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", user_input)
        
        with st.spinner("AI Brainstorming kar raha hai..."):
            try:
                if v_id_match:
                    # MODE 1: Video Link Analysis
                    v_id = v_id_match.group(1)
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        title = item['snippet']['title']
                        views = item['statistics'].get('viewCount', '0')
                        
                        prompt = f"""
                        Analyze this YouTube Video: {title}. Views: {views}.
                        Provide a MASTER SEO Report in Hinglish:
                        1. Why it's successful?
                        2. 5 Viral Title Variations.
                        3. 20 High-Ranking Tags.
                        4. Secret SEO Score (0-100).
                        5. Competition level for this topic.
                        """
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video: {title}")
                    else:
                        st.error("Video details not found.")
                        st.stop()
                else:
                    # MODE 2: General YouTube Question / Channel Analysis
                    prompt = f"""
                    Tum ek YouTube Strategy Guru ho. User ne ye pucha hai: '{user_input}'
                    Isko detail mein Hinglish mein samjhao. 
                    - Agar kisi bade channel ke bare mein pucha hai toh uski growth strategy batao.
                    - Agar trending topic pucha hai toh aaj ke top 5 niches aur keyword ideas do.
                    - Agar general sawal hai toh YouTube algorithm ke hisab se best advice do.
                    - Jawab points mein aur professional hona chahiye.
                    """
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy Insights")

                # Display Result
                st.markdown(result)
                
                # Save to Sheets
                if save_to_sheets(user_input, result):
                    st.success("Analysis saved to YT_History! ✅")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Pehle kuch likho toh sahi!")

st.sidebar.markdown("### 🛠️ Tool Capabilities")
st.sidebar.info("""
- ✅ Video SEO Audit
- ✅ Channel Growth Strategy
- ✅ Trending Topic Finder
- ✅ Unlimited Questions
- ✅ Auto-save to Sheets
""")

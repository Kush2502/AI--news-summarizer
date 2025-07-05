import streamlit as st
from newspaper import Article
from transformers import pipeline
import feedparser
import requests
import re

# Email validation
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

# Page config
st.set_page_config(page_title="AI-Powered News Summarizer", layout="wide")

# CSS Design
st.markdown("""
    <style>
    body {
        background-color: #121212;
        font-family: 'Roboto', sans-serif;
        color: #f1f1f1;
        margin: 0;
        padding: 0;
        background-image: linear-gradient(to right, #1e3c72, #2a5298), url('https://cdn.pixabay.com/photo/2015/09/18/19/01/architecture-940325_960_720.jpg');
        background-size: cover;
        background-position: center;
    }
    .main {
        padding: 50px;
        width: 90%;
        max-width: 1000px;
        margin: auto;
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 16px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 20px;
        font-family: 'Pacifico', cursive;
    }
    .subtitle {
        font-size: 1.7rem;
        color: #d3d3d3;
        text-align: center;
        margin-bottom: 40px;
    }
    .stTextInput, .stButton, .stTabs {
        width: 100%;
        max-width: 700px;
        padding: 20px;
        margin: 15px 0;
        background-color: #2b2b2b;
        color: #d3d3d3;
        border-radius: 12px;
        border: none;
        font-size: 1.1rem;
        transition: background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stTextInput:focus, .stButton:hover, .stTabs [data-baseweb="tab"]:hover {
        background-color: #4f4f4f;
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
    }
    .stButton button {
        background-color: #5C6BC0;
        color: #ffffff;
        padding: 14px 24px;
        border-radius: 16px;
        border: none;
        cursor: pointer;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    .stButton button:active {
        background-color: #3f51b5;
        transform: scale(0.98);
    }
    .result-box {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 16px;
        margin-top: 20px;
        font-size: 1.1rem;
        color: #ffffff;
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    .result-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.6);
    }
    .card {
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.7);
    }
    .card-title {
        font-size: 1.3rem;
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .card-description {
        font-size: 1.1rem;
        color: #d3d3d3;
    }
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
    </style>
""", unsafe_allow_html=True)

# Summarization model
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
summarizer = load_summarizer()

# Fix: Resolve redirected Google News URLs before using newspaper3k
def extract_article_content(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        final_url = response.url
        article = Article(final_url)
        article.download()
        article.parse()
        if article.text and len(article.text.split()) > 50:
            return article.text
    except Exception as e:
        print(f"[ERROR] {e}")
    return None

# Session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'is_registering' not in st.session_state:
    st.session_state.is_registering = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Login / Register UI
if not st.session_state.logged_in:
    st.markdown("<h1 class='title'>💻AI-Powered News📰Summarizer</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='subtitle'>🔐Login or Register to Continue🔑</h2>", unsafe_allow_html=True)

    if st.session_state.is_registering:
        st.subheader("Create Account🔑")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register🔒"):
            if not reg_email or not reg_password:
                st.error("Email and password cannot be empty.")
            elif not is_valid_email(reg_email):
                st.error("Please enter a valid email address.")
            elif reg_email in st.session_state.users:
                st.error("User already exists. Try logging in.")
            else:
                st.session_state.users[reg_email] = reg_password
                st.success("Registration successful! Please log in.")
                st.session_state.is_registering = False
                st.rerun()
        if st.button("Go to Login"):
            st.session_state.is_registering = False
            st.rerun()
        st.stop()
    else:
        st.subheader("🔑Login to Your Account💻")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login🔑"):
            if not is_valid_email(login_email):
                st.error("Please enter a valid email address.")
            elif login_email in st.session_state.users and st.session_state.users[login_email] == login_password:
                st.session_state.logged_in = True
                st.session_state.current_user = login_email
                st.success("Logged in successfully!🚀")
                st.rerun()
            else:
                st.error("Invalid email or password. Please try again.")
        if st.button("Go to Register🔓"):
            st.session_state.is_registering = True
            st.rerun()
        st.stop()

# Main app (after login)
st.markdown(f"<h2 class='subtitle'> 👋Welcome To The AI-News Summarizer, {st.session_state.current_user}! 🚀</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔎Topic", "🌐Summarize by URL"])

# Topic-based summarization
with tab1:
    topic = st.text_input("🔍Enter a topic (e.g., 'Tech News', 'Cricket', 'Rohit Sharma'):")
    if st.button("Search Articles📖"):
        if topic:
            st.info("Searching for articles...🌍")
            query = topic.replace(" ", "+")
            rss_url = f"https://news.google.com/rss/search?q={query}+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
            feed = feedparser.parse(rss_url)

            if feed.entries:
                st.subheader("Related Articles📑:")
                for entry in feed.entries[:10]:
                    title = entry.title
                    link = entry.link
                    st.markdown(f"""
                        <div class='card'>
                            <h4 class='card-title'>🔗 <a href="{link}" target="_blank" style="color: #5C6BC0;">{title}</a></h4>
                            <p class='card-description'>{entry.summary}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No articles found. Try a different topic 🔄.")
        else:
            st.error("Please enter a topic to search.✍")

# URL summarization
with tab2:
    url = st.text_input("🌐Enter article URL here:")
    if st.button("Summarize📑"):
        if url:
            st.info("Extracting content... Please Hold On...⏳")
            with st.spinner("Processing...⏳"):
                article_text = extract_article_content(url)
                if article_text:
                    summary = summarizer(article_text, max_length=300, min_length=120, do_sample=False)
                    st.subheader("Article Summary📖:")
                    st.markdown(f"{summary[0]['summary_text']}")
                else:
                    st.error("Unable to extract or summarize the article. Please check the URL and try again.")
        else:
            st.error("Please enter a valid URL...🌐")

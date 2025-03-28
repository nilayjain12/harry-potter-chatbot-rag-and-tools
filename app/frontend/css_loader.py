from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSS_DARK_PATH = BASE_DIR / "app" / "frontend" / "css" / "style_dark.css"
CSS_LIGHT_PATH = BASE_DIR / "app" / "frontend" / "css" / "style_light.css"
CSS_CHAT_PATH = BASE_DIR / "app" / "frontend" / "css" / "chat_style.css"

def load_css():
    css_path_light = CSS_LIGHT_PATH
    with open(css_path_light) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    css_path_chat = CSS_CHAT_PATH
    with open(css_path_chat) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
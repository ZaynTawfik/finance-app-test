import os
import streamlit as st

def load_env():
    os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]

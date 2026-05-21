"""Streamlit Cloud entry point - adds project root to path."""
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load secrets
import streamlit as st
if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
if hasattr(st, 'secrets') and 'LANGCHAIN_API_KEY' in st.secrets:
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_API_KEY'] = st.secrets['LANGCHAIN_API_KEY']
    os.environ['LANGCHAIN_PROJECT'] = st.secrets.get('LANGCHAIN_PROJECT', 'ai-governance-helper')

# Now import and run the actual app
from src.ui.app import main
main()
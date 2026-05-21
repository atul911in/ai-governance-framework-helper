"""Streamlit Cloud entry point - sets env vars BEFORE any LangChain imports."""
import sys
import os
from pathlib import Path

# Add project root to Python path FIRST
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Set environment variables BEFORE importing anything from langchain/langgraph
# This is critical - LangSmith tracing must be configured before module load
os.environ.setdefault('LANGCHAIN_TRACING_V2', 'false')

try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        if 'OPENAI_API_KEY' in st.secrets:
            os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
        if 'LANGCHAIN_API_KEY' in st.secrets:
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
            os.environ['LANGCHAIN_API_KEY'] = st.secrets['LANGCHAIN_API_KEY']
            os.environ['LANGCHAIN_PROJECT'] = st.secrets.get('LANGCHAIN_PROJECT', 'ai-governance-helper')
            os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
except Exception:
    pass

# NOW import and run the app (LangChain will pick up the env vars)
from src.ui.app import main
main()
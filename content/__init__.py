import streamlit as st
import pandas as pd
import pickle, os, logging
import httpx

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SERVER_HOST = st.secrets["API_HOST"]
SERVER_ACCESS_KEY = st.secrets["API_ACCESS_KEY"]
SERVER_ACCESS_TOKEN = st.secrets["API_ACCESS_TOKEN"]

MODEL_PATH = st.secrets["MODEL_PATH"]
PRED_LOGS_FOLDER = st.secrets["PRED_LOGS_FOLDER"]

make_req = lambda s: f"{SERVER_HOST}/{s}"
import httpx
import pandas as pd
from PIL import Image 
import streamlit as st
import pickle, os, logging

if st.secrets["ENV"] == "LOCAL":
    SERVER_HOST = st.secrets["API_HOST"]
    SERVER_ACCESS_KEY = st.secrets["API_ACCESS_KEY"]
    SERVER_ACCESS_TOKEN = st.secrets["API_ACCESS_TOKEN"]
    MODEL_PATH = st.secrets["MODEL_PATH"]
    PRED_LOGS_FOLDER = st.secrets["PRED_LOGS_FOLDER"]
else:
    SERVER_HOST = os.getenv("API_HOST", "")
    SERVER_ACCESS_KEY = os.getenv("API_ACCESS_KEY", "")
    SERVER_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")
    MODEL_PATH = os.getenv("MODEL_PATH")
    PRED_LOGS_FOLDER = os.getenv("PRED_LOGS_FOLDER")


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def ping_server():
    try:
        response = httpx.get(f"{SERVER_HOST}/", timeout=5)
        if response.status_code == 200:
            return "ok"
        else:
            return "ko"
    except httpx.RequestError as e:
        logger.error(f"Server ping failed: {e}")
        return "ko"

st.session_state["server_state"] = ping_server()  # default server state

make_req = lambda s: f"{SERVER_HOST}/{s}"
make_route = make_req

def make_route_with_token(s):
    return f"{make_req(s)}?access_key={SERVER_ACCESS_KEY}&access_token={SERVER_ACCESS_TOKEN}"

def load_image(image_path):
    """
    Load an image from the given path.
    """
    if os.path.exists(image_path):
        return Image.open(image_path)
    else:
        logger.error(f"Image not found at {image_path}")
        return None
    
def load_logo():
    """
    Load the logo image.
    """
    logo_path = "content/img/logo.ico"
    return load_image(logo_path) or "🤖"
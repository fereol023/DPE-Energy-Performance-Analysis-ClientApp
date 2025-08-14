import requests
import pandas as pd
import streamlit as st
import pickle, os, logging, uuid

from PIL import Image 

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("VOLT-DPE-DATAVIZ-APP")


try:
    if st.secrets["ENV"] == "LOCAL":
        SERVER_URL = st.secrets["API_HOST"]
        SERVER_ACCESS_KEY = st.secrets["API_ACCESS_KEY"]
        SERVER_ACCESS_TOKEN = st.secrets["API_ACCESS_TOKEN"]
        MODEL_PATH = st.secrets["MODEL_PATH"]
        PRED_LOGS_FOLDER = st.secrets["PRED_LOGS_FOLDER"]
    else:
        SERVER_URL = os.getenv("API_HOST", "")
        SERVER_ACCESS_KEY = os.getenv("API_ACCESS_KEY", "")
        SERVER_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")
        MODEL_PATH = os.getenv("MODEL_PATH")
        PRED_LOGS_FOLDER = os.getenv("PRED_LOGS_FOLDER")
except:
        logger.info("Using environment variables")
        SERVER_URL = os.getenv("API_HOST", "")
        SERVER_ACCESS_KEY = os.getenv("API_ACCESS_KEY", "")
        SERVER_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")
        MODEL_PATH = os.getenv("MODEL_PATH")
        PRED_LOGS_FOLDER = os.getenv("PRED_LOGS_FOLDER")



def ping_server():
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            return "ok", response.json()
        else:
            return "ko", response.json()
    except Exception as e:
        logger.error(f"Server ping failed: {e}")
        return "ko", e

st.session_state["server_state"] = ping_server()  # default server state


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

def make_get_request(route):
    try:
        access_token = st.session_state['access_token']
    except:
        access_token = ""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{SERVER_URL}/{route}"
    logger.info(f"calling route : {url}")
    try:
        return requests.get(url, headers=headers)
    except Exception as e:
        s = f"😔 Smthg happened wrong for query : {url} : {e}"
        logger.info(s)

def make_post_request(route, payload):
    try:
        access_token = st.session_state['access_token']
    except:
        access_token = ""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{SERVER_URL}/{route}"
    logger.info(f"calling route : {url}")
    try:
        return requests.post(url, headers=headers, json=payload)
    except Exception as e:
        s = f"😔 Smthg happened wrong for query : {url} : {e}"
        logger.info(s)

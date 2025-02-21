import streamlit as st
import pickle, requests, os
import pandas as pd

st.title('Hello page')

API_URL = os.getenv("API_URL", "http://localhost:8000/") # env variable
API_PWD = os.getenv("API_TOKEN", "pwd") # env variable

r = requests.get(API_URL, timeout=30).json()
r = requests.get(f"{API_URL}/read/db/testcollection", timeout=30).json()

# st.text(r)
st.table(pd.DataFrame(r.get('res', {}).get('data', {})))
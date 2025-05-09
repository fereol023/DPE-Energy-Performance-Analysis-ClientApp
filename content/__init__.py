import streamlit as st
import pickle, requests, os
import pandas as pd


SERVER_HOST = st.secrets["API_HOST"]
SERVER_ACCESS_KEY = st.secrets["API_ACCESS_KEY"]
SERVER_ACCESS_TOKEN = st.secrets["API_ACCESS_TOKEN"]

make_req = lambda s: f"{SERVER_HOST}/{s}"
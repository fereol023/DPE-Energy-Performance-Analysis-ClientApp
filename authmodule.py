import os
import logging
import requests
import streamlit as st

logger = logging.getLogger("VOLT-DPE-DATAVIZ-APP")
try:
    if st.secrets["ENV"] == "LOCAL":
        API_BASE_URL = st.secrets["SERVER_API_URL"]
        # SERVER_ACCESS_TOKEN = st.secrets["API_ACCESS_TOKEN"]
    else:
        API_BASE_URL = os.getenv("SERVER_API_URL")
except:
        logger.info("Using environment variables")
        API_BASE_URL = os.getenv("SERVER_API_URL")

def check_is_connected():
    return 'access_token' in st.session_state 

def check_is_connected_as_admin():
    try:
        return st.session_state['user_role'] == 'admin'
    except:
        return False

def request_otp(email, context, debug=False):
    response = requests.post(f"{API_BASE_URL}/send-otp", json={"email": email})
    if response.status_code == 200:
        if debug: 
            context.success(f"OTP envoyé par email ! : {response.json().get('message', '')}")
        else:
            context.success(f"OTP envoyé par email ! Ce code est valable 5 min.")
    else:
        context.error(f"Erreur : {response.json().get('detail', 'Erreur inconnue')}")

def verify_otp(email, otp, context):
    response = requests.post(f"{API_BASE_URL}/login-with-otp", json={"email": email, "otp": otp})
    if response.status_code == 200:
        context.success(f"Connexion réussie en tant que {response.json().get('role', '')} ! ")
        #  {'access_token': 'xxxxx', 'token_type': 'bearer', 'role': 'admin/reader'}
        # Ici tu peux stocker le cookie/token dans une session ou gérer la suite
        st.session_state['access_token'] = response.json().get('access_token')
        st.session_state['user_role'] = response.json().get('role')
        return True
    else:
        context.error(f"Échec de la connexion, OTP incorrect. : {response.status_code} : {response.json()}")
        return False

def make_connexion_page():
    _, c, __ = st.columns([1, 2, 1])
    c.title("Connexion")

    email = c.text_input("Adresse email")
    if c.button("Demander un code OTP"):
        if email:
            request_otp(email, c)
        else:
            c.warning("Veuillez saisir une adresse email valide.")

    otp = c.text_input("Code OTP (5 chiffres)", max_chars=5)
    if c.button("Se connecter"):
        if email and otp:
            verify_otp(email, otp, c)
        else:
            c.warning("Veuillez saisir votre email et le code OTP.")

if __name__ == "__main__":
    make_connexion_page()

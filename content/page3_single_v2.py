from content import *
from uuid import uuid4
from typing import Union
from datetime import datetime
import os
import io
import logging
import pandas as pd
from datetime import datetime
import boto3

@st.cache_data
def get_kwh_price():
    """
    Prix du kWh en euros.
    Source : api serveur 
    """
    res = make_get_request("price_kwh")
    if res.status_code == 200:
        return res.json()
    else:
        return {
            "prix_kwh_base": 0.2,  # default backup value
            "source": "Backup value"
        }


@st.cache_data
def search_adress(inp_addr: str)->list:
    """
    Call API endpoint to get adresses closer to input adress.
    """
    res = make_get_request(f"db/reader/adresses/searchadress/{inp_addr}")
    if res.status_code == 200:
        data = res.json()
        if data.get('data'):
            return data.get('data')
        else:
            return []
    else:
        logger.error(f"Failed to fetch adresses: {res.text}")
        st.error("Failed to fetch adresses")
    return []


@st.cache_data
def search_avg_inputs_from_address(inp_addr: str)->dict:
    """
    Call API endpoint to get example of inputs values to set
    as default values in form - to prepare model input.
    # TODO: for now, just take one example from the database
    """
    res = make_get_request(f"db/reader/logements/getbyadress/{inp_addr}")
    if res.status_code == 200:
        data = res.json()
        if data.get('data'):
            # si plusieurs logements on prend juste le premier
            return data.get('data') if isinstance(data.get('data'), dict) else data.get('data')[0]
        else:
            logger.warning("No data found for the given address.")
            st.warning("No data found for the given address.")
    else:
        logger.error(f"Failed to fetch address data: {res.text}")
        st.error("Failed to fetch address data")
    return {}


def get_dpe_conso_range(inp):
    mapping = {
        "A": "inférieure à 70 kWh/m2/an",	
        "B": "entre 71 et 110 kWh/m2/an",	
        "C": "entre 111 et 180 kWh/m2/an",	
        "D": "entre 181 et 250 kWh/m2/an",	
        "E": "entre 251 et 330 kWh/m2/an",	
        "F": "entre 331 et 420 kWh/m2/an",	
        "G": "supérieure à 421 kWh/m2.an"
    }
    return mapping.get(inp, 'NC')


def get_dpe_label(dpe_value_idx: int):
    """
    Pour obtenir la liste des dpe restants. 
    """
    mapping = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G'}
    return mapping.get(dpe_value_idx, "NC")


def make_form_from_config(model_features_config, example_inputs={}):
    """
    Generate input form based on model features configuration.
    """
    FLOAT_COLS, CATEG_COLS = [], []
    for feature, config in model_features_config.items():
        if 'float' in config.get('dtype'):
            FLOAT_COLS.append(feature)
        elif 'int' in config.get('dtype'):
            CATEG_COLS.append(feature)
        else:
            pass

    input_values = {}
    col11, col12 = st.columns(2)
    _milieu = len(FLOAT_COLS)//2
    for feature in FLOAT_COLS[:_milieu]:
        # default is min+max//2
        feature_config = model_features_config.get(feature)
        label = feature_config.get('desc', '')
        _default = float(example_inputs.get(feature, None) or feature_config.get('def', 0))
        input_values[feature] = col11.slider(
            f"{label}",
            min_value=float(feature_config.get('min', 0)),
            max_value=float(feature_config.get('max', 100)),
            value=_default
        )
    for feature in FLOAT_COLS[_milieu:]:
        # default is min+max//2
        feature_config = model_features_config.get(feature)
        label = feature_config.get('desc', '')
        _default = float(example_inputs.get(feature, None) or feature_config.get('def', 0))
        input_values[feature] = col12.slider(
            f"{label}",
            min_value=float(feature_config.get('min', 0)),
            max_value=float(feature_config.get('max', 100)),
            value=_default
        )
        
    col21, col22 = st.columns(2)
    _milieu = len(CATEG_COLS)//2
    for feature in CATEG_COLS[:_milieu]:
        feature_config = model_features_config.get(feature)
        label = feature_config.get('desc', '')
        v = col21.selectbox(
            f"{label}", 
            options=feature_config['mapping'], 
            index=feature_config['mapping'].get(example_inputs.get(feature, None), 0)
            )
        input_values[feature] = feature_config.get('mapping').get(v)
    for feature in CATEG_COLS[_milieu:]:
        feature_config = model_features_config.get(feature)
        label = feature_config.get('desc', '')
        v = col22.selectbox(
            f"{label}", 
            options=feature_config['mapping'], 
            index=feature_config['mapping'].get(example_inputs.get(feature, None), 0)
            )
        input_values[feature] = feature_config.get('mapping').get(v)
    # update inputs
    st.session_state['inputs'] = input_values


def make_input_df(inputs: dict) -> pd.DataFrame:
    """
    Convert inputs dict to DataFrame.
    """
    inputs_model = []
    for dpe in range(1, 8): # iterates from 1 to 7 actually
        inputs['etiquette_dpe_ademe'] = dpe
        inputs_model.append(inputs.copy())
    input_model_df = pd.DataFrame(inputs_model)
    input_model_df.sort_index(axis=1, inplace=True)
    return input_model_df


def get_predictions_from_server(input_as_df, model_version="v1") -> list:
    try:
        res = make_get_request(f"model/{model_version}/config")
        model_required_cols = res.json()
        input_as_df = input_as_df[model_required_cols.keys()]
        payload = input_as_df.to_dict(orient="records")
        res = make_post_request(f"model/{model_version}/predict", payload=payload) # true requires url to be https
        logger.info("Prediction ok !")
        #st.write(f'predictions : {res.status_code}')
        #st.write(res.json())
        l = logging.getLogger("VOLT-DPE-DATAVIZ-APP")
        l.info(f"Prediction output : {res.json()}")
        return res.json().get('predictions', [])
    except Exception as e:
        logger.warning(f"Prediction ko - {e}")
        return


def format_prediction_result(res_df: pd.DataFrame) -> pd.DataFrame:
    """Format the prediction result DataFrame."""

    def highlight_row(s):
        input_dpe_value = st.session_state['input_dpe_as_int']
        if input_dpe_value:
            if s['Etiquette DPE'] == get_dpe_label(input_dpe_value):
                return ['background-color: #2ECC71'] * len(s)
            else:
                return [''] * len(s)

    def format_euro(val):
        try:
            return f"{val:,.2f} €"
        except Exception:
            raise

    rev_dpe_enc = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G"}

    PRIX_KWH_EUROS = get_kwh_price().get("prix_kwh_base")    
    logger.info(f"Prix du kWh : {PRIX_KWH_EUROS} euros")

    res_df['Conso kwh/m2/an'] = round(res_df['conso_kwh_m2'], 3)
    res_df['Conso kwh/an'] = round(res_df['Conso kwh/m2/an'] * res_df['surface_habitable_logement_ademe'], 3)
    res_df['Etiquette DPE'] = res_df['etiquette_dpe_ademe'].apply(lambda r: rev_dpe_enc.get(r))
    res_df['Montant (euros/an)'] = round(res_df['Conso kwh/an'] * PRIX_KWH_EUROS, 2)
    res_df['Economies (euros/an) vs classe DPE précédente'] = round(res_df['Montant (euros/an)'].shift(-1) - res_df['Montant (euros/an)'], 2)
    res_df = res_df.sort_values(by=['Etiquette DPE'], ascending=False)
    res_df['Economies cumulées (euros/an)'] = res_df['Economies (euros/an) vs classe DPE précédente'].cumsum()
    res_df = res_df.sort_values(by=['Etiquette DPE'], ascending=True)
    res_cols = [
        "Etiquette DPE",
        "Conso kwh/m2/an",
        "Conso kwh/an",
        "Montant (euros/an)",
        "Economies (euros/an) vs classe DPE précédente",
        "Economies cumulées (euros/an)"
    ]
    res_df = res_df[res_cols].rename(
        columns={
            "surface_habitable_logement_ademe": "Surface du logement",
            })
    styled_df = res_df.style.apply(highlight_row, axis=1)
    styled_df = styled_df.format({
        "Economies (euros/an) vs classe DPE précédente": format_euro,
        "Economies cumulées (euros/an)": format_euro,
        "Montant (euros/an)": format_euro,
        "Conso kwh/an": lambda v: f"{v:,.2f}",
        "Conso kwh/m2/an": lambda v: f"{v:,.2f}",
    })
    st.markdown("**Détails prédictions**")
    st.write("- *Montant euros/an = prix du kwh (euros/an) x consommation kwh/an*")
    st.write("- *Economie euros/an = Economie réalisée en changeant vers :orange[la classe DPE au dessus]*")
    st.write("- *Economie cumulée euros/an = Economie réalisée en changeant de :orange[plusieurs classes DPE] au dessus*")
    return styled_df # res_df


def log_prediction_results(
        res: pd.DataFrame,
        folder: str = None,
        save_inputs: bool = False) -> None:
    """
    Log prediction results as JSON to S3 (via boto3).
    """
    logger = logging.getLogger("VOLT-DPE-DATAVIZ-APP")

    def generate_id() -> str:
        """Generate a unique prediction ID."""
        return str(uuid4())
    if save_inputs:
        try:
            s3_client = boto3.client(
                "s3",
                endpoint_url=os.getenv("S3_URL"), # optional for aws (needed if using MinIO-compatible S3)
                aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            )
        except Exception as e:
            logger.critical(f"Could not connect to filestorage : {e}")
            return
        PRED_LOGS_BUCKET = os.getenv("S3_BUCKET_NAME")
        if folder is None:
            folder = PRED_LOGS_BUCKET
        pred_id = generate_id()
        object_name = f"model/pred-logs/{pred_id}.json"
        # JSON in memory
        json_buffer = io.BytesIO()
        res.assign(
            id=res.index,
            prediction_id=pred_id,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ).to_json(
            json_buffer,
            orient="records",
            date_format="iso",
            force_ascii=False,
            indent=4
        )
        # Reset buffer pointer
        json_buffer.seek(0)
        try:
            # Upload with boto3
            s3_client.upload_fileobj(
                Fileobj=json_buffer,
                Bucket=PRED_LOGS_BUCKET,
                Key=object_name,
                ExtraArgs={"ContentType": "application/json"}
            )
            logger.info(f"Results saved to S3 at s3://{PRED_LOGS_BUCKET}/{object_name}")
        except Exception as e:
            logger.error(f"Failed to upload prediction results: {e}")


def main(obj_model, model_config, save_inputs=False):

    inp_addr = st.text_input(
        "Recherchez votre addresse : *exple. rue lord byron cannes*",
        )
    if inp_addr:
        results = search_adress(inp_addr)

        st.write(
            "*Pour avoir les données automatiquement remplies, choisir dans cette liste le meilleur match avec votre saisie...*"
            )
        choosed_address = st.selectbox(
            "Choisir adresse..", 
            results
            ) or {}
        
        st.session_state['inputs'] = search_avg_inputs_from_address(
            choosed_address.get('adresse', 'abcde') # fetch on non existing town
            )
        # display form
        st.markdown("----------------")
        make_form_from_config(
            model_config, 
            example_inputs={}
            )
        st.markdown("----------------")
        
        if st.button("Estimez avec ces informations"):
            inputs_dict_form = st.session_state.get("inputs", False)
            st.session_state['input_dpe_as_int'] = inputs_dict_form.get('etiquette_dpe_ademe')
            st.session_state['input_dpe_as_label'] = get_dpe_label(inputs_dict_form.get('etiquette_dpe_ademe'))
            if not inputs_dict_form:
                st.error("No inputs")
            else:
                inputs_as_df = make_input_df(inputs_dict_form)
                # inputs_as_df['conso_kwh_m2'] = obj_model.predict(inputs_as_df)
                inputs_as_df['conso_kwh_m2'] = get_predictions_from_server(inputs_as_df, model_version="v1")
                output = format_prediction_result(inputs_as_df).data
                log_prediction_results(inputs_as_df, save_inputs=save_inputs)
                st.success(f"""
                    **Résultats :**\n
                    "➡️ Etiquette DPE" : ***{st.session_state['input_dpe_as_label']}***\n
                    "📊 Consommation estimée sur la base du DPE (min-max)" : ***{get_dpe_conso_range(st.session_state['input_dpe_as_label'])}***\n
                    "✅ Consommation kwh/an estimée": ***{round(output.query(f" `Etiquette DPE` == '{st.session_state['input_dpe_as_label']}' ")['Conso kwh/an'].iloc[0], 2)}***\n
                    "✅ Consommation kwh/m2/an estimée": ***{round(output.query(f" `Etiquette DPE` == '{st.session_state['input_dpe_as_label']}' ")['Conso kwh/m2/an'].iloc[0], 2)}***,\n
                    "💶 Consommation euros/an estimée": ***{round(output.query(f" `Etiquette DPE` == '{st.session_state['input_dpe_as_label']}' ")['Montant (euros/an)'].iloc[0], 3)}***,\n
                    """)
                st.markdown("ℹ️ Informations sur la tarification appliquée")
                st.write(get_kwh_price())
                st.write("")
                st.dataframe(format_prediction_result(inputs_as_df), hide_index=True)

        if st.button("Log out - Reset all"): st.session_state.clear()
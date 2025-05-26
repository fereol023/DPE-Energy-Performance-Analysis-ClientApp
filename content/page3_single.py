from content import *
from uuid import uuid4
from typing import Union
from datetime import datetime


@st.cache_data
def get_kwh_price():
    """
    Prix du kWh en euros.
    Source : api serveur 
    """
    route = make_req("price_kwh")
    logger.info(f"Calling route : {route}")
    res = httpx.get(route)
    if res.status_code == 200:
        return res.json()
    else:
        return {
            "prix_kwh_base": 0.216,  # default backup value
            "source": "Backup value"
        }


@st.cache_data
def search_adress(inp_addr: str)->list:
    """
    Call API endpoint to get adresses closer to input adress.
    """
    #make_req()
    return []


@st.cache_data
def search_avg_inputs_from_address(inp_addr: str)->dict:
    """
    Call API endpoint to get example of inputs values to set
    as default values in form - to prepare model input.
    """
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


def get_dpe_label(dpe_value_idx):
    """
    Pour obtenir la liste des dpe restants. 
    Prédire les économies réalisées en changeant de classe DPE
    """
    mapping = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G'}
    return mapping.get(dpe_value_idx, "NC")


def make_form_from_config(model_features_config):
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
        config = model_features_config.get(feature)
        label = config.get('desc', '')
        _default = float(config.get('def', 0))
        input_values[feature] = col11.slider(
            f"{label}",
            min_value=float(config.get('min', 0)),
            max_value=float(config.get('max', 100)),
            value=_default
        )
    for feature in FLOAT_COLS[_milieu:]:
        # default is min+max//2
        config = model_features_config.get(feature)
        label = config.get('desc', '')
        _default = float(config.get('def', 0))
        input_values[feature] = col12.slider(
            f"{label}",
            min_value=float(config.get('min', 0)),
            max_value=float(config.get('max', 100)),
            value=_default
        )
        
    col21, col22 = st.columns(2)
    _milieu = len(CATEG_COLS)//2
    for feature in CATEG_COLS[:_milieu]:
        config = model_features_config.get(feature)
        label = config.get('desc', '')
        v = col21.selectbox(f"{label}", options=config['mapping'], index=0)
        input_values[feature] = config.get('mapping').get(v)
    for feature in CATEG_COLS[_milieu:]:
        config = model_features_config.get(feature)
        label = config.get('desc', '')
        v = col22.selectbox(f"{label}", options=config['mapping'], index=0)
        input_values[feature] = config.get('mapping').get(v)

    # update inputs
    st.session_state['inputs'] = input_values


def make_input_df(inputs: dict) -> pd.DataFrame:
    """
    Convert inputs dict to DataFrame.
    """
    inputs_model = []
    for dpe in range(1, 8):
        inputs['etiquette_dpe_ademe'] = dpe
        inputs_model.append(inputs.copy())
    
    input_model_df = pd.DataFrame(inputs_model)
    input_model_df.sort_index(axis=1, inplace=True)
    return input_model_df


def generate_id():
    """
    Generate a unique identifier for the prediction.
    """
    return str(uuid4())


def format_prediction_result(res_df: pd.DataFrame) -> str:
    """
    Format the prediction result DataFrame.
    """

    def highlight_row(s):
        input_dpe_value = st.session_state.get('inputs', {}).get('etiquette_dpe_ademe', 1)
        if s['Etiquette DPE'] == get_dpe_label(input_dpe_value):
            return ['background-color: #ffe082'] * len(s)
        else:
            return [''] * len(s)

    def format_euro(val):
        try:
            return f"{val:,.2f} €"
        except Exception:
            return val

    rev_dpe_enc = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G"}

    PRIX_KWH_EUROS = get_kwh_price().get("prix_kwh_base")
    logger.info(f"Prix du kWh : {PRIX_KWH_EUROS} euros")

    res_df['Conso kwh/m2/an'] = round(res_df['conso_kwh_m2'], 3)
    res_df['Conso kwh/an'] = round(res_df['Conso kwh/m2/an'] * res_df['surface_habitable_logement_ademe'], 3)
    res_df['Etiquette DPE'] = res_df['etiquette_dpe_ademe'].apply(lambda r: rev_dpe_enc.get(r))
    res_df['Montant (euros/an)'] = round(res_df['Conso kwh/an'] * PRIX_KWH_EUROS, 2)
    res_df['Economies (euros/an)'] = round(res_df['Montant (euros/an)'].shift(-1) - res_df['Montant (euros/an)'], 2)
    res_df = res_df.sort_values(by=['Etiquette DPE'], ascending=False)
    res_df['Economies cumulées (euros/an)'] = res_df['Economies (euros/an)'].cumsum()
    res_df = res_df.sort_values(by=['Etiquette DPE'], ascending=True)

    res_cols = [
        "Etiquette DPE",
        "Conso kwh/m2/an",
        "Conso kwh/an",
        "Montant (euros/an)",
        "Economies (euros/an)",
        "Economies cumulées (euros/an)"
    ]
    res_df = res_df[res_cols].rename(
        columns={
            "surface_habitable_logement_ademe": "Surface du logement",
            })

    styled_df = res_df.style.apply(highlight_row, axis=1)
    styled_df = styled_df.format({
        "Economies (euros/an)": format_euro,
        "Economies cumulées (euros/an)": format_euro,
        "Montant (euros/an)": format_euro,
        "Conso kwh/an": lambda v: f"{v:,.2f}",
        "Conso kwh/m2/an": lambda v: f"{v:,.2f}",
    })

    st.markdown("**Détails prédictions**")
    st.write("- *Montant euros/an = prix du kwh (euros/an) x consommation kwh/an*")
    st.write("- *Economie euros/an = Economie réalisée en changeant vers :orange[la classe DPE au dessus]*")
    st.write("- *Economie cumulée euros/an = Economie réalisée en changeant de :orange[plusieurs classes DPE] au dessus*")

    # st.dataframe(
    #     styled_df,
    #     hide_index=True
    # )

    return res_df


def log_prediction_results(
        res: pd.DataFrame, 
        folder = None, 
        save_inputs = False) -> None:
    """
    Log prediction results to a file or database.
    """
    if save_inputs:
        if folder is None:
            folder = PRED_LOGS_FOLDER

        pred_id = generate_id()
        filepath = os.path.join(folder, f"{pred_id}.json")
        res.assign(
            id=res.index,
            prediction_id=pred_id,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ).to_json(
            open(filepath, 'w'), 
            orient='records',
            date_format='iso', 
            force_ascii=False, 
            indent=4
        )
        logger.info(f"Results saved to {filepath}")


def main(obj_model, model_config, save_inputs=False):

    # _, c1, __ = st.columns([1, 2, 1])
    inp_addr = st.text_input("Input address")
    if inp_addr:
        results = search_adress(inp_addr)

        st.write(
            "Choose between the following best matches with your input"
            )
        choosed_address = st.selectbox(
            "Choisir adresse..", 
            results
            )
        st.session_state['inputs'] = search_avg_inputs_from_address(
            choosed_address
            )
        # display form
        st.markdown("----------------")
        make_form_from_config(model_config)
        st.markdown("----------------")
        
        if st.button("Predict on this"):
            inputs_as_df = st.session_state.get("inputs", False)
            if not inputs_as_df:
                st.error("No inputs")
            else:
                st.write("Running prediction")
                inputs_as_df = make_input_df(inputs_as_df)
                inputs_as_df['conso_kwh_m2'] = obj_model.predict(inputs_as_df)

                log_prediction_results(inputs_as_df, save_inputs=save_inputs)
                st.dataframe(format_prediction_result(inputs_as_df), hide_index=True)

        if st.button("Reset all"): st.session_state.clear()

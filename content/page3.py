import authmodule
from content import *
import content.page3_batch as demo_batch
import content.page3_single_v2 as demo_single


class ModesDemo(enumerate):
    single = "Estimation pour un seul logement"
    multiple = "Estimations multiples (plus d'un logement)"

# @st.cache_data
def load_model_config(version="v0"):
    try:
        res = make_get_request(f"model/{version}/config")
        if res.status_code==200: 
            model_config = res.json()
            logger.info("Config du modèle bien loadé !")
        else:
            logger.critical(f"Erreur chargement config model : {res.json()}")
            model_config = {}
        return model_config
    except Exception as e:
        logger.warning(f"Error loading model - {e}")
        return {}

def main(*args, **kwargs):

    serveur_state = st.session_state.get('server_state')
    if serveur_state == 'ko':
        st.error(f"Le serveur n'est pas démarré. Veuillez démarrer le serveur pour continuer. Details : {st.session_state["server_state_details"]}")
        # return

    obj_model, config_model = None, load_model_config(version="v1")

    _, c1, __ = st.columns([1, 1.5, 1])
    mode_choosed = c1.segmented_control(
        label="*Mode*",
        options=["Estimation pour un seul logement", "Estimations multiples (plus d'un logement)"],
        selection_mode="single",
        default="Estimation pour un seul logement"
    )
    # consentemment
    not_consent = c1.toggle(
        "*Vous refusez la sauvegarde de vos données pour améliorer le modèle.*"
        )
    if st.toggle("Voir les métadonnées du modèle"):
        st.markdown("---")
        st.markdown(f"""
                    👉 **Nom du modèle :** *{config_model.get("model_name", "rf-proxy2-oise-60-v1-202507")}*\n
                    👉 **Version :** *{config_model.get("model_version", "v1")}*\n
                    👉 **Type de modèle :** *{config_model.get("model_type", "RandomForestRegressor")}*\n
                    👉 **Description :** *Modèle de régression pour estimer la consommation électrique annuelle (kwh) d'un logement en fonction de ses caractéristiques et du DPE.*\n
                    👉 **Données entrainement :** *Enedis Ademe 2023 extrait en Juillet 2025 (département 60 - Oise).*\n
                    👉 **Méthode de calcul matrice de gains** : *Pour un même set de caractéristiques, on calcule la différence de consommation entre la classe DPE actuelle et la classe DPE visée. On multiplie cette différence par le prix du kWh pour obtenir le gain annuel en euros.*\n
                    👉 **Configuration brute :** {config_model}
                    """)
        st.markdown("---")

    st.sidebar.selectbox("Modèle de prédiction", ["rf-proxy2-oise-60-v1-202507"], index=0, key="model_name")
    if mode_choosed == ModesDemo.single:
        c1.write("*Avec ce mode- :orange[estimez vos économies pour un logement après changement de classe DPE]*")
        demo_single.main(obj_model, config_model, (not not_consent))
    else:
        c1.write("Not available")
        demo_batch.main(config_model)
    st.feedback("faces")
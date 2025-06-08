from content import *
import content.page3_batch as demo_batch
import content.page3_single as demo_single


class ModesDemo(enumerate):
    single = "une prédiction"
    multiple = "prédictions multiples"

@st.cache_resource # model, db connection, atg you cant store in db
def load_model(default:bool, path=None, type=None):
    try:
        if default:
            path, type = MODEL_PATH, "pkl"

        if type=="pkl":
            _ = pickle.load(open(path, 'rb'))
            logger.info("Modele bien loadé !")
            return _
    except Exception as e:
        logger.warning(f"Error loading model - {e}")
        return

@st.cache_data
def load_model_config(version="v0"):
    try:
        _ = make_req(f"model/{version}/config")
        logger.info(f"Calling route : {_}")
        model_config = httpx.get(_).json()
        logger.info("Config du modèle bien loadé !")
        return model_config
    except Exception as e:
        logger.warning(f"Error loading model - {e}")
        return

def main(*args, **kwargs):
    # model loading
    obj_model, config_model = load_model(default=True), load_model_config()
    # consentemment
    not_consent = st.toggle(
        "*Vous refusez la sauvegarde de vos données pour améliorer le modèle.*"
        )

    _, c1, __ = st.columns([1, 3, 1])
    mode_choosed = st.segmented_control(
        label="*Mode*",
        options=["une prédiction", "prédictions multiples"],
        selection_mode="single",
        default="une prédiction"
    )

    if mode_choosed == ModesDemo.single:
        c1.write("*With single mode - :orange[estimate savings on only one flat]*")
        demo_single.main(obj_model, config_model, (not not_consent))
    else:
        c1.write("Not available")
        demo_batch.main()

    st.feedback("faces")
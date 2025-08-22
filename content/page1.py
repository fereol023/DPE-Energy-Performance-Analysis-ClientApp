import authmodule
from content import *


def main(*args, **kwargs):
    
    serveur_state = st.session_state.get('server_state')
    if serveur_state == 'ko':
        st.error(f"Le serveur n'est pas démarré. Veuillez démarrer le serveur pour continuer. Details : {st.session_state["server_state_details"]}")
        return
    
    ville = kwargs.get("selected_ville", "")
    st.markdown("""
        <style>
        h1 {
            font-size: 3rem !important; /* titre principal */
        }
        h2 {
            font-size: 2rem !important; /* header */
        }
        h3 {
            font-size: 1.5rem !important; /* subheader */
        }
        p {
            font-size: 1.2rem !important; /* texte normal */
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Diagnostics de performance énergétique " + ville)
    
    st.subheader("Contexte du projet")
    st.markdown(f"""
Le changement climatique et la hausse des prix de l’énergie poussent à la sobriété énergétique.
Objectif politique : la neutralité carbone à l'horizon 2050, diminuer les GES des bâtiments d’ici 2030. La rénovation énergétique est un levier économique clé car les bâtiments
sont responsables d'une part importante des émissions de GES.
""")
    st.subheader("Problématique et solutions apportées par cet outil")
    st.markdown(f"""
**Problématique :**
- Les estimations conventionnelles fournies dans les DPE reflètent-elles bien la réalité mesurée des consommations électriques ? 
- Et quelle est la variabilité restante due à l’hétérogénéité des modes de vie et taux d’occupation ?
- Combien gagne t-on chaque année à changer de classe DPE ?

**L'outil présent :**
- permet d'étudier l’impact des caractéristiques du bâtiment ou des équipements (mode de chauffage, isolation, année de construction, etc.) sur la consommation électrique réelle
- permet de modéliser la consommation électrique en fonction de la classe DPE, des habitudes de consommation et des caractéristiques des bâtiments, puis comparer avec la consommation réelle et analyser la part du delta expliquée par le DPE et celle expliquée par les habitudes
- permet de se prononcer sur la conformité ou non des estimations de consommation présentées dans les DPE par rapport aux données réelles (consommation théorique vs consommation réelle)
- permet de quantifier les gains potentiels liés à une amélioration de la performance énergétique d’un logement via une amélioration de la classe DPE (impact sur la consommation et éventuellement sur le prix, toutes choses égales par ailleurs)
- permet de discuter l’impact des habitudes individuelles de consommation sur ces résultats, usage par usage : chauffage, eau chaude sanitaire, refroidissement, éclairage, autres
""")

    if not authmodule.check_is_connected():
        authmodule.make_connexion_page()
    else:
        if authmodule.check_is_connected_as_admin(): 
            st.markdown("#### Panel admin ⚙️")
            if st.button("Init DB (placeholder)"):
                st.success("calling route /user-admin")
                st.markdown(make_get_request(f"/user-admin").json())
                #st.markdown(make_get_request(f"/db").json())
            if st.button("Connect to prefect UI"):
                SERVER_URL = os.getenv("SERVER_API_URL", "")
                if not SERVER_URL:
                    st.error("Uh oh error")
                else:
                    url = f"{SERVER_URL}/prefect-server/dashboard"
                    st.success(f"route : {url}")
            if st.button("Deploy ETL flow"):
                SERVER_URL = os.getenv("SERVER_API_URL", "")
                if not SERVER_URL:
                    st.error("Uh oh error")
                else:
                    url = f"{SERVER_URL}/etl/start-deployment"
                    st.success(f"route: {url}")
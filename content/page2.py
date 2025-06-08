from content import *
import plotly.express as px

#@st.cache_data
def get_data_logement_table(city_name="All", arrondissement_name="All", year_range=None):
    """
    Call API endpoint to get all adresses by city and arrondissement.
    """
    # route = make_route_with_token(f"db/reader/adresses/getbycityandarrondissement/{city_name}/{arrondissement_name}")
    if city_name == "All":
        route = make_route("db/reader/logements/getall")
    else:
        route = make_route(f"db/reader/logements/getallbycity/{city_name}")
    logger.info(f"Calling route : {route}")
    res = httpx.get(route)
    if res.status_code == 200:
        return res.json()
    else:
        return {"data": [], "error": "Failed to fetch adresses"}

def get_data_adresse_table(city_name="All", arrondissement_name="All"):
    """
    Call API endpoint to get all adresses by city and arrondissement.
    """
    if city_name == "All":
        route = make_route("db/reader/adresses/all/allcoords")
    else:
        route = make_route(f"db/reader/adresses/{city_name}/allcoords")
    logger.info(f"Calling route : {route}")
    res = httpx.get(route)
    if res.status_code == 200:
        return res.json()
    else:
        return {"data": [], "error": "Failed to fetch adresses"}

def main(*args, **kwargs):
    
    st.markdown("#### Exploratory Data Analysis (EDA) and Key Performance Indicators (KPI)")
    serveur_state = st.session_state.get('server_state')
    if serveur_state == 'ko':
        st.error("Le serveur n'est pas démarré. Veuillez démarrer le serveur pour continuer.")
        return
    st.markdown("""
Cette page permet d'explorer les données et de visualiser les 
indicateurs clés de performance (KPI) liés aux diagnostics de performance énergétique (DPE).
                """)

    # data retrieval
    selected_city = kwargs.get('selected_city', "All")
    selected_arrondissement = kwargs.get('selected_arrondissement', "All")

    data_logement = pd.DataFrame(get_data_logement_table(selected_city, selected_arrondissement).get('data', []))
    if not data_logement.empty:
        # cast
        if 'cout_chauffage_ademe' not in data_logement.columns:
            st.error("La colonne 'cout_chauffage_ademe' n'est pas présente dans les données.")
            return
        if 'consommation_annuelle_totale_de_l_adresse_mwh_enedis' not in data_logement.columns:
            st.error("La colonne 'consommation_annuelle_totale_de_l_adresse_mwh_enedis' n'est pas présente dans les données.")
            return
        if 'surface_habitable_logement_ademe' not in data_logement.columns:
            st.error("La colonne 'surface_habitable_m2_ademe' n'est pas présente dans les données.")
            return
    
        data_logement['cout_chauffage_ademe'] = (
            data_logement['cout_chauffage_ademe'].astype(float)
        )
        data_logement['consommation_annuelle_totale_de_l_adresse_mwh_enedis'] = (
            data_logement['consommation_annuelle_totale_de_l_adresse_mwh_enedis'].astype(float)
        )
        data_logement['surface_habitable_logement_ademe'] = (
            data_logement['surface_habitable_logement_ademe'].astype(float)
        )

        # calculate consumption per m²
        data_logement['consommation_kwh_m2_ademe'] = round(
            data_logement['consommation_annuelle_totale_de_l_adresse_mwh_enedis'] * 1000 / 
            data_logement['surface_habitable_logement_ademe'], 3
        )
    data_coord_adresse = pd.DataFrame(get_data_adresse_table(selected_city, selected_arrondissement)\
        .get('data', [{'latitude': 46.603354, 'longitude': 1.888334}]))
    ## visu
    if st.toggle("Afficher les données", value=False):
        st.dataframe(data_logement.head(), use_container_width=True)
        st.dataframe(data_coord_adresse.head(), use_container_width=True)

    c01, c02 = st.columns([2, 1])
    
    # minimap using longitude and latitude
    c01.markdown("#### Carte")

    if not data_coord_adresse.empty:
        c01.map(data_coord_adresse[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'}))
    else:
        # else center map on France with a default zoom to see full country
        france_center = {'latitude': 46, 'longitude': 1.8}  
        c01.map(pd.DataFrame([france_center]))
    
    c02.markdown("#### Adresses exploitables")
    data_coord_adresse = data_coord_adresse\
        .drop(labels=['latitude', 'longitude'], axis=1)\
        .groupby('Ville')\
        .agg({'nombre_logements': 'sum'})\
        .reset_index()\
        .rename(columns={'nombre_logements': 'Nombre de logements trouvés'})
    c02.dataframe(data_coord_adresse, use_container_width=True, hide_index=True)


    # filter type batiment ademe
    st.markdown("----")
    if st.toggle("Filtrer tous les graphiques sur appartements et maisons", value=True):
        if 'type_batiment_ademe' not in data_logement.columns:
            st.warning(
                "Impossible de filtrer par bâtiment car : "\
                "*colonne 'type_batiment_ademe' n'est pas présente dans les données.*"
                )
            return
        data_logement = data_logement[data_logement['type_batiment_ademe'].isin(['maison', 'appartement'])]

    # 1 logements par dpe
    c11, c12 = st.columns([1, 1])
    # c11.markdown("#### Nombre de logements par DPE")
    if not data_logement.empty:
        _columns = ['etiquette_dpe_ademe']
        if any(col not in data_logement.columns for col in _columns):
            st.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
            return
        _data_graph = data_logement.groupby('etiquette_dpe_ademe').size().reset_index(name='Count')
        fig = px.bar(_data_graph, x='etiquette_dpe_ademe', y='Count', title="Nombre de logements par DPE")
        c11.plotly_chart(fig)
    else:
        c11.markdown("No data available for DPE counts.")

    # 2 logements par ges
    # c12.markdown("#### Nombre de logements par GES")
    if not data_logement.empty:
        _columns = ['etiquette_ges_ademe']
        if any(col not in data_logement.columns for col in _columns):
            st.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
            return
        _data_graph = data_logement.groupby('etiquette_ges_ademe').size().reset_index(name='Count')
        fig = px.bar(_data_graph, x='etiquette_ges_ademe', y='Count', title="Nombre de logements par GES")
        c12.plotly_chart(fig)
    else:
        c12.markdown("No data available for DPE counts.")

    # add hue (color) by DPE label
    add_hue = st.toggle("Ajouter une couleur par DPE (hue)", value=False)
    c11, c12 = st.columns([1, 1])

    # 3 nb logements par type de chauffage
    if not data_logement.empty:
        _columns = ['type_energie_principale_chauffage_ademe']
        if add_hue:
            _columns.append('etiquette_dpe_ademe')
        if any(col not in data_logement.columns for col in _columns):
            c11.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
            return
        if add_hue:
            _data_graph = data_logement.groupby(['type_energie_principale_chauffage_ademe', 'etiquette_dpe_ademe']).size().reset_index(name='Count')
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='Count', color='etiquette_dpe_ademe', barmode='group', title="Nombre de logements par type de chauffage (par DPE)")
        else:
            _data_graph = data_logement.groupby('type_energie_principale_chauffage_ademe').size().reset_index(name='Count')
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='Count', title="Nombre de logements par type de chauffage")
        c11.plotly_chart(fig)
    else:
        c11.markdown("No data available for heating type counts.")

    # 4 cout moyen chauffage par type de chauffage
    if not data_logement.empty:
        _columns = ['type_energie_principale_chauffage_ademe', 'cout_chauffage_ademe']
        if add_hue:
            _columns.append('etiquette_dpe_ademe')
        if any(col not in data_logement.columns for col in _columns):
            c12.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
            return
        if add_hue:
            _data_graph = data_logement.groupby(['type_energie_principale_chauffage_ademe', 'etiquette_dpe_ademe'])['cout_chauffage_ademe'].mean().reset_index()
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='cout_chauffage_ademe', color='etiquette_dpe_ademe', barmode='group', title="Coût moyen de chauffage par type de chauffage (par DPE)")
        else:
            _data_graph = data_logement.groupby('type_energie_principale_chauffage_ademe')['cout_chauffage_ademe'].mean().reset_index()
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='cout_chauffage_ademe', title="Coût moyen de chauffage par type de chauffage")
        c12.plotly_chart(fig)
    else:
        c12.markdown("No data available for heating cost averages.")

    # 5 consommation moyenne/m2 par type de chauffage
    if not data_logement.empty:
        _columns = ['type_energie_principale_chauffage_ademe', 'consommation_kwh_m2_ademe']
        if add_hue:
            _columns.append('etiquette_dpe_ademe')
        if any(col not in data_logement.columns for col in _columns):
            c11.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
            return
        if add_hue:
            _data_graph = data_logement.groupby(['type_energie_principale_chauffage_ademe', 'etiquette_dpe_ademe'])['consommation_kwh_m2_ademe'].mean().reset_index()
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='consommation_kwh_m2_ademe', color='etiquette_dpe_ademe', barmode='group', title="Consommation moyenne par m² par type de chauffage (par DPE)")
        else:
            _data_graph = data_logement.groupby('type_energie_principale_chauffage_ademe')['consommation_kwh_m2_ademe'].mean().reset_index()
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='consommation_kwh_m2_ademe', title="Consommation moyenne par m² par type de chauffage")
        c11.plotly_chart(fig)
    else:
        c11.markdown("No data available for average consumption per m² by heating type.")

    # 6 consommation moyenne/m2 par dpe
    # if not data_logement.empty:
    #     _columns = ['etiquette_dpe_ademe', 'consommation_kwh_m2_ademe']
    #     if any(col not in data_logement.columns for col in _columns):
    #         c12.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
    #         return
    #     _data_graph = data_logement.groupby('etiquette_dpe_ademe')['consommation_kwh_m2_ademe'].mean().reset_index()
    #     fig = px.bar(_data_graph, x='etiquette_dpe_ademe', y='consommation_kwh_m2_ademe', title="Consommation moyenne par m² par DPE")
    #     c12.plotly_chart(fig)
    # else:
    #     c12.markdown("No data available for average consumption per m² by DPE.")

    # 7 consommation moyenne/m2 par ancienneté/periode de construction
    # (à compléter selon disponibilité des colonnes)

    # 8 surface moyenne par dpe
    # if not data_logement.empty:
    #     _columns = ['etiquette_dpe_ademe', 'surface_habitable_logement_ademe']
    #     if any(col not in data_logement.columns for col in _columns):
    #         c11.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
    #         return
    #     _data_graph = data_logement.groupby('etiquette_dpe_ademe')['surface_habitable_logement_ademe'].mean().reset_index()
    #     fig = px.bar(_data_graph, x='etiquette_dpe_ademe', y='surface_habitable_logement_ademe', title="Surface moyenne par DPE")
    #     c11.plotly_chart(fig)
    # else:
    #     c11.markdown("No data available for average surface by DPE.")

    # 9 surface moyenne par type de chauffage
    if not data_logement.empty:
        _columns = ['type_energie_principale_chauffage_ademe', 'surface_habitable_logement_ademe']
        if add_hue:
            _columns.append('etiquette_dpe_ademe')
        if any(col not in data_logement.columns for col in _columns):
            c12.error(f"Les colonnes {_columns} ne sont pas présentes dans les données.")
            return
        if add_hue:
            _data_graph = data_logement.groupby(['type_energie_principale_chauffage_ademe', 'etiquette_dpe_ademe'])['surface_habitable_logement_ademe'].mean().reset_index()
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='surface_habitable_logement_ademe', color='etiquette_dpe_ademe', barmode='group', title="Surface moyenne par type de chauffage (par DPE)")
        else:
            _data_graph = data_logement.groupby('type_energie_principale_chauffage_ademe')['surface_habitable_logement_ademe'].mean().reset_index()
            fig = px.bar(_data_graph, x='type_energie_principale_chauffage_ademe', y='surface_habitable_logement_ademe', title="Surface moyenne par type de chauffage")
        c12.plotly_chart(fig)
    else:
        c12.markdown("No data available for average surface by heating type.")

    # 10 surface moyenne par ancienneté/periode de construction

    # autre x autre x autre (hue)


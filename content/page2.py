import authmodule
from content import *
import plotly.express as px
from .utils import plot_categorical_with_dpe_hue_plotly, plot_quantitative_with_dpe_hue_plotly

@st.cache_data
def get_data_logement_table(city_name="All", selected_dept="All", year_range=None):
    """
    Call API endpoint to get all adresses by city and arrondissement.
    """
    if city_name == "All":
        res = make_get_request("db/reader/logements/getall")
    else:
        res = make_get_request(f"db/reader/logements/getallbycity/{city_name}")
    if res.status_code == 200:
        return res.json()
    else:
        return {"data": [], "error": "Failed to fetch adresses"}

def get_data_adresse_table(city_name="All", selected_dept="All"):
    """
    Call API endpoint to get all adresses by city and arrondissement.
    """
    if city_name == "All":
        res = make_get_request("db/reader/adresses/all/allcoords")
    else:
        res = make_get_request(f"db/reader/adresses/{city_name}/allcoords")
    if res.status_code == 200:
        return res.json()
    else:
        return {"data": [], "error": "Failed to fetch adresses"}

def main(*args, **kwargs):
    
    st.markdown("#### Analyse Exploratoire (EDA) et KPIs")

    serveur_state = st.session_state.get('server_state')
    if serveur_state == 'ko':
        st.error(f"Le serveur n'est pas démarré. Veuillez démarrer le serveur pour continuer. Details : {st.session_state["server_state_details"]}")
        return
    st.markdown("""
Cette page permet d'explorer les données et de visualiser les 
indicateurs clés de performance (KPI) liés aux diagnostics de performance énergétique (DPE).
                """)

    # data retrieval
    selected_city = kwargs.get('selected_city', "All")
    selected_dept = kwargs.get('selected_dept', "All")

    data_logement = pd.DataFrame(get_data_logement_table(selected_city, selected_dept).get('data', []))
    if not data_logement.empty:
        # check available columns for my plots
        required_columns = [
            'absolute_diff_conso_prim_fin',
            'absolute_diff_conso_fin_act',
            'conso_kwh_m2',
            'conso_5_usages_par_m2_ef_ademe',
            'conso_5_usages_par_m2_ep_ademe',
            'cout_total_5_usages_energie_n1_ademe',
            'etiquette_dpe_ademe',
            'etiquette_ges_ademe',
            'periode_construction_ademe',
            'surface_habitable_logement_ademe',
            'type_energie_n1_ademe',
            'type_installation_ecs_ademe',
            'type_energie_generateur_n1_ecs_n1_ademe',
        ]
        for col in required_columns:
            if col not in data_logement.columns:
                st.error(f"La colonne '{col}' n'est pas présente dans les données.")
                return
    else:
        st.error("Aucune donnée de logement disponible pour la ville et l'arrondissement sélectionnés.")
        return


    c01, c02 = st.columns([2, 1])
    # ------ minimap using longitude and latitude --------
    data_coord_adresse = pd.DataFrame(get_data_adresse_table(selected_city, selected_dept)\
        .get('data', [{'latitude': 46.603354, 'longitude': 1.888334}]))
    
    c01.markdown("#### Carte") 
    if not data_coord_adresse.empty:
        c01.map(data_coord_adresse[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'}))
    else: # else center map on France with a default zoom to see full country
        france_center = {'latitude': 46, 'longitude': 1.8}  
        c01.map(pd.DataFrame([france_center]))
    

    c02.markdown("#### Distributions des logements exploitables")
    data_coord_adresse = data_coord_adresse\
        .drop(labels=['latitude', 'longitude'], axis=1)\
        .groupby('Ville')\
        .agg({'nombre_logements': 'sum'})\
        .reset_index()\
        .rename(columns={'nombre_logements': 'Nombre de logements trouvés'})
    n = data_coord_adresse['Nombre de logements trouvés'].sum()
    c02.metric("Nombre de logements total", f"{n:,.0f}".replace(",", " "), border=True)
    c02.dataframe(data_coord_adresse, use_container_width=True, hide_index=True)

    # ------- visualitisations des données -------
    st.markdown("----")
    _c11, _c12, _c13 = st.columns([2, 1, 2]) 
    etiquettes_diag_map = {'Etiquette DPE': 'etiquette_dpe_ademe', 'Etiquette GES': 'etiquette_ges_ademe'}
    etiquettes_diag_choix_alias = _c12.radio('Choix étiquette', etiquettes_diag_map.keys(), horizontal=True)
    dpe_color_map = {
        'A': '#1a9641',  # Dark green (best)
        'B': '#a6d96a',  # Light green
        'C': '#ffffbf',  # Yellow
        'D': '#fdae61',  # Light orange
        'E': '#f46d43',  # Orange
        'F': '#d73027',  # Red
        'G': '#a50026'   # Dark red (worst)
    }
    c11, c12 = st.columns([1, 1])
    # distributions des etiquettes DPE et GES
    etiquettes_diag_choix_varname = etiquettes_diag_map.get(etiquettes_diag_choix_alias)
    if not data_logement.empty:
        _data_graph = data_logement.groupby(etiquettes_diag_choix_varname).size().reset_index(name='Count')
        fig = px.bar(_data_graph, x=etiquettes_diag_choix_varname, y='Count', title=f"Nombre de logements par {etiquettes_diag_choix_alias}", color=etiquettes_diag_choix_varname,  color_discrete_map=dpe_color_map)
        c11.plotly_chart(fig)
    else:
        c11.markdown(f"No data available for {etiquettes_diag_choix_alias} counts.")

    # scatter plot conso reelle vs conso estimee par le DPE avec hue par etiquette diag choisie et droite x = y
    if not data_logement.empty:
        _data_graph = data_logement[['conso_kwh_m2', 'conso_5_usages_par_m2_ef_ademe', etiquettes_diag_choix_varname]].dropna()
        max_value = max(_data_graph['conso_kwh_m2'].max(), _data_graph['conso_5_usages_par_m2_ef_ademe'].max())
        # min_value = min(_data_graph['conso_kwh_m2'].min(), _data_graph['conso_5_usages_par_m2_ef_ademe'].min())
        fig = px.scatter(
            _data_graph, 
            x='conso_kwh_m2', 
            y='conso_5_usages_par_m2_ef_ademe', 
            color=etiquettes_diag_choix_varname,
            category_orders={etiquettes_diag_choix_varname: ['A', 'B', 'C', 'D', 'E', 'F', 'G']},
            title=f"Consommation réelle vs consommation estimée par le DPE (coloré par {etiquettes_diag_choix_alias})",
            labels={
                'conso_kwh_m2': 'Consommation réelle (kWh/m²)',
                'conso_5_usages_par_m2_ef_ademe': 'Consommation estimée par le DPE (kWh/m²)'
            },
            range_x=[0, 100 + max_value],
            range_y=[0, 100 + max_value],
            color_discrete_map=dpe_color_map
        )
        fig.add_shape(
            type='line',
            x0=0,
            y0=0,
            x1=max_value,
            y1=max_value,
            line=dict(color='gray', dash='dash'),
            name='x = y'
        )
        fig.update_layout(
            xaxis_title='Consommation réelle (kWh/m²)',
            yaxis_title='Consommation estimée par le DPE (kWh/m²)',
            legend_title=etiquettes_diag_choix_alias
        )
        c12.plotly_chart(fig)
    else:
        c12.markdown("No data available for DPE counts.")

    # --- differences de consommation et consommations ----
    conso_colnames_map = {
        'Consommation réelle annuelle moyenne par logement mesurée par Enedis (kwh/m2/an)': 'conso_kwh_m2',
        'Absolute difference consommation primaire finale estimée par DPE (kwh/m2/an)': 'absolute_diff_conso_prim_fin',
        'Absolute difference consommation consommation Enedis vs DPE (kwh/m2/an)': 'absolute_diff_conso_fin_act',
        'Consommation 5 usages par m2 energie finale estimée par DPE (kwh/m2/an)': 'conso_5_usages_par_m2_ef_ademe',
        'Consommation 5 usages par m2 energie primaire estimée par DPE (kwh/m2/an)': 'conso_5_usages_par_m2_ep_ademe',
        # 'cout_total_5_usages_energie_n1_ademe': 'cout_total_5_usages_energie_n1_ademe',
    }

    if data_logement.empty:
        st.markdown("No data available for plotting.")
    c11, c12 = st.columns([1, 1])
    conso_col_to_plot_alias_1 = c11.selectbox("Choisir colonne :", conso_colnames_map.keys(), index=0) 
    conso_col_to_plot_alias_2 = c12.selectbox("Choisir colonne :", conso_colnames_map.keys(), index=1) 

    _c11, _c12, _c13 = st.columns([2, 1, 2])
    add_hue = _c12.toggle("Ajouter une couleur par etiquette DPE", value=True)
    
    c11, c12 = st.columns([1, 1])
    fig = plot_quantitative_with_dpe_hue_plotly(
        df=data_logement,
        col_name=conso_colnames_map.get(conso_col_to_plot_alias_1),
        col_name_alias=conso_col_to_plot_alias_1,
        hue_col='etiquette_dpe_ademe' if add_hue else None,
        hue_col_alias='Etiquette DPE ADEME' if add_hue else '',
        plot_type='box',
        height=600,
        width=1000,
        opacity=0.9
    )
    c11.plotly_chart(fig)
    fig = plot_quantitative_with_dpe_hue_plotly(
        df=data_logement,
        col_name=conso_colnames_map.get(conso_col_to_plot_alias_2),
        col_name_alias=conso_col_to_plot_alias_2,
        hue_col='etiquette_dpe_ademe' if add_hue else None,
        hue_col_alias='Etiquette DPE ADEME' if add_hue else '',
        plot_type='box',
        height=600,
        width=1000,
        opacity=0.9
    )
    c12.plotly_chart(fig)

    st.markdown("----")
    # --- bivariate add hue (color) by DPE label ----
    other_variables_map = {
        'Période de construction du logement': 'periode_construction_ademe',
        "Type d'énergie principale utilisé": 'type_energie_n1_ademe',
        "Type d'installation Eau Chaude Sanitaire (ECS)": 'type_installation_ecs_ademe',
        "Type d'énergie générateur ECS": 'type_energie_generateur_n1_ecs_n1_ademe',
    }

    if data_logement.empty:
        st.error("No data avaible for plotting.")

    c11, c12 = st.columns([1, 1])
    other_col_to_plot_alias_1 = c11.selectbox("Choisir colonne :", other_variables_map.keys(), index=0) 
    other_col_to_plot_alias_2 = c12.selectbox("Choisir colonne :", other_variables_map.keys(), index=1) 

    _c11, _c12, _c13 = st.columns([1, 1, 1])
    # add_hue = _c12.toggle("Pour les graphiques suivants, ajouter une couleur par etiquette DPE (hue)", value=False)
    
    c11, c12 = st.columns([1, 1])
    stacked_graph_1 = c11.toggle("Stack graph 1", value=False)
    fig = plot_categorical_with_dpe_hue_plotly(
        df=data_logement,
        col_name=other_variables_map.get(other_col_to_plot_alias_1),
        col_name_alias=other_col_to_plot_alias_1,
        # hue_col='etiquette_dpe_ademe' if add_hue else None,
        log_scale_y=False,
        stacked=stacked_graph_1,
        height=600,
        width=1000,
    )
    c11.plotly_chart(fig)
    stacked_graph_2 = c12.toggle("Stack graph 2", value=False)
    fig = plot_categorical_with_dpe_hue_plotly(
        df=data_logement,
        col_name=other_variables_map.get(other_col_to_plot_alias_2),
        col_name_alias=other_col_to_plot_alias_2,
        # hue_col='etiquette_dpe_ademe' if add_hue else None,
        log_scale_y=False,
        stacked=stacked_graph_2,
        height=600,
        width=1000,
    )
    c12.plotly_chart(fig)

## visu
    if st.toggle("Afficher les données", value=False):
        st.dataframe(data_logement.head(), use_container_width=True)
        st.dataframe(data_coord_adresse.head(), use_container_width=True)

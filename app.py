from content import *
from content import page1, page2, page3

st.set_page_config(
    layout="wide",
    page_icon=load_logo(),
    initial_sidebar_state="collapsed",
    page_title="VOLT.AI | WebApp Energy Performance Analysis"
    )

pages = {
    "Présentation": page1.main,
    "Dataviz": page2.main,
    "Estimateur VOLT": page3.main
}

st.sidebar.image("content/img/banner.png", width=200)
p = st.sidebar.radio('Aller à ', list(pages.keys()))

st.sidebar.markdown("-------------------")

#@st.cache_data
def get_all_adresses():
    """
    Call API endpoint to get all adresses.
    """
    route = make_route("db/reader/adresses/getall")
    logger.info(f"Calling route : {route}")
    res = httpx.get(route)
    if res.status_code == 200:
        return res.json()
    else:
        return {"data": [], "error": "Failed to fetch adresses"}

# st.cache_data
def get_cities_names_and_codes():
    """
    Call API endpoint to get all cities.
    """
    route = make_route("db/reader/adresses/cities")
    logger.info(f"Calling route : {route}")
    res = httpx.get(route)
    if res.status_code == 200:
        return res.json()
    else:
        return {"data": [], "error": "Failed to fetch cities"}

def get_cities_names():
    """
    Call API endpoint to get all cities names.
    """
    r = get_cities_names_and_codes()
    if r.get('data'):
        return list(set([city['city_name'] for city in r['data']]))
    else:
        return []
    
# filters
st.sidebar.header("Filtres")
available_cities = get_cities_names()
available_districts = []  # TODO placeholder for districts/arrondissements
selected_city = st.sidebar.selectbox("City", ["All"] + available_cities)
selected_district = st.sidebar.selectbox("Arrondissement/District", ["All"] + available_districts)

selected_year = st.sidebar.slider("Data Source Year (enedis)", min_value=2000, max_value=2023, value=(2010, 2020))
construction_year = st.sidebar.slider("Building age Year", min_value=1900, max_value=2023, value=(1940, 1980))

if st.sidebar.button("Reset All"):
    # Reset filters
    selected_city = "All"
    selected_district = "All"
    selected_year = (2010, 2020)
    construction_year = (1940, 1980)

pages[p](
    selected_city = selected_city, 
    selected_district = selected_district, 
    selected_year = selected_year, # for data 
    construction_year = construction_year # building age filter
    )
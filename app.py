import authmodule
from content import *
from content import page1, page2, page3

st.set_page_config(
    layout="wide",
    page_icon=load_logo(),
    initial_sidebar_state="collapsed",
    page_title="VOLT.AI | WebApp Energy Performance Analysis"
    )

def get_cities_names_and_codes():
    """
    Call API endpoint to get all cities.
    """
    res = make_get_request("db/reader/adresses/cities")
    if res:
        if res.status_code == 200:
            return res.json()
        else:
            return {"data": [], "error": "Failed to fetch cities"}
    else:
        return {"data": [], "error": "Failed to fetch cities"}

def get_cities_names():
    """
    Call API endpoint to get all cities names.
    """
    r = get_cities_names_and_codes()
    if r:
        if r.get('data'):
            return list(set([city['city_name'] for city in r['data']]))
        else:
            return []
    else:
        return []

def get_departments():
    """Call API endpoint to get departments codes"""
    r = get_cities_names_and_codes()
    if r:
        if r.get('data'):
            return list(set([city['code_departement'] for city in r['data']]))
        else:
            return []
    else:
        return []

# filters
pages = {
    "Présentation": page1.main,
    "Dataviz": page2.main,
    "Estimateur VOLT": page3.main
}

st.sidebar.image("content/img/banner.png", width=200)
p = st.sidebar.radio('Aller à ', list(pages.keys()))
st.sidebar.markdown("-------------------")
st.sidebar.header("Filtres")
available_cities = get_cities_names()
available_dept = get_departments()
selected_city = st.sidebar.selectbox("Ville", ["All"] + available_cities)
selected_dept = st.sidebar.selectbox("Département", ["All"] + available_dept)

selected_year = st.sidebar.slider("Data Source Year (enedis)", min_value=2019, max_value=2023, value=(2022, 2023))
construction_year = st.sidebar.slider("Building age Year", min_value=1940, max_value=2023, value=(1940, 2023))

if st.sidebar.button("Reset All"):
    selected_city = "All"
    selected_dept= "All"
    selected_year = (2023, 2023)
    construction_year = (1940, 1980)

st.session_state["server_state"] = ping_server()[0]
st.session_state["server_state_details"] = ping_server()[1]
pages[p](
    selected_city = selected_city, 
    selected_district = selected_dept, 
    selected_year = selected_year, # for data 
    construction_year = construction_year # building age filter
    )
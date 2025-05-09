from content import *
import plotly.express as px

def main():
    
    st.title("EDA metrics and KPI")

    r = requests.get(SERVER_HOST, timeout=60).json()
    # if st.button('Init db'):
    r = requests.get(make_req("db/"), timeout=30).json()
    
    r = requests.get(make_req("/db/reader/")).json()

    r = requests.get(make_req("/db/reader/adresses/getall")).json()

    
    # filters
    st.sidebar.header("Filtres")
    selected_city = st.sidebar.selectbox("Select City", ["All"] + r.get('cities', []))
    selected_district = st.sidebar.selectbox("Select district", ["All"] + r.get('districts', []))
    selected_year = st.sidebar.slider("Select Year", min_value=2000, max_value=2023, value=(2010, 2020))
    construction_year = st.sidebar.slider("Construction Year", min_value=1900, max_value=2023, value=(1940, 1980))
    
    if st.sidebar.button("Reset All"):
        # Reset filters
        selected_city = "All"
        selected_district = "All"
        selected_year = (2010, 2020)
        construction_year = (1940, 1980)

    # Apply filters to data
    filtered_data = r.get('data')
    if selected_city != "All":
        filtered_data = [item for item in filtered_data if item['city'] == selected_city]
    if selected_district != "All":
        filtered_data = [item for item in filtered_data if item['district'] == selected_district]
    filtered_data = [item for item in filtered_data if selected_year[0] <= item['year'] <= selected_year[1]]
    

    c01, c02 = st.columns(2)
    
    # Create a minimap using longitude and latitude
    c01.markdown("#### Carte")
    map_data = pd.DataFrame(
        [{'latitude': item['latitude'], 'longitude': item['longitude']} for item in filtered_data]
    )

    if not map_data.empty:
        c01.map(map_data)
    else:
        # else center map on France with a default zoom to see full country
        france_center = {'latitude': 46.603354, 'longitude': 1.888334}  
        c01.map(pd.DataFrame([france_center]))
    
    c02.markdown("#### Adresses exploitables")
    c02.dataframe(filtered_data)

    c11, c12, c13 = st.columns(3)
    c11.markdown("#### Nombre de logements par DPE")
    r11 = requests.get(make_req("db/reader/adresses/getdpecount")).json()
    # Create a bar plot for the number of logements by DPE
    dpe_data = pd.DataFrame(r11.get('data', []))

    if not dpe_data.empty:
        dpe_data.columns = ['DPE', 'Count']
        fig = px.bar(dpe_data, x='DPE', y='Count', title="Nombre de logements par DPE")
        c11.plotly_chart(fig)
    else:
        c11.markdown("No data available for DPE counts.")



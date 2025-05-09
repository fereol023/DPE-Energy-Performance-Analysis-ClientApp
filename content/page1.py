from content import *
import time


def call_data_workflow(input_loaded):
    url, url2 = make_req("upload-input"), make_req("etl/v1/run")
    if input_loaded is not None:
        # push input to s3 first
        files = {"file": (input_loaded.name, input_loaded, "text/csv")}
        st.write(".send data to fs as input - calling : ", url)
        r = requests.post(url, files=files)
        if r.status_code == 200:
            st.success(r.json())  
        else:
            st.warning(r.json())
    st.write(".run ETL flow - calling : ", url2)
    r = requests.get(url2)
    if r.status_code == 200:
        st.success(r.json())  
    else:
        st.warning(r.json())

def main():

    st.title('Présentation générale')

    input_schema = {
        "col1": ["a"], 
        "col2": ["b"]
    }

    st.markdown("""
                #### To start, upload a csv file with consos
                *Attention, des verifs sont faites sur l'input. Respecter le schema (exple).*
                """)
    
    st.dataframe(pd.DataFrame(data=input_schema).T)

    pd.DataFrame(data=input_schema).to_csv("test_csv.csv")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])    

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV file :")
        st.dataframe(data.head())
    else:
        uploaded_file = None

    if st.button('Run data workflow'):
        call_data_workflow(uploaded_file)
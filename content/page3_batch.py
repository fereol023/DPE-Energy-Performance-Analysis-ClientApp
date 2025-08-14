from content import *


def main():

    input_schema = {
        "col1": ["a"], 
        "col2": ["b"]
    }

    st.markdown("""
                ##### To start, upload a csv file with consos
                *Attention, des verifs sont faites sur l'input. Respecter le schema (exple).*
                """)
    
    st.dataframe(pd.DataFrame(data=input_schema).T)
    os.makedirs("data/input_batch", exist_ok=True)

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])    
    if uploaded_file is not None:
        pass
        # data = pd.read_csv(uploaded_file)
        # st.write("Uploaded CSV file :")
        # st.dataframe(data.head())
    else:
        uploaded_file = None

    if st.button('Run data workflow'):
        st.warning("Not handled yet.")
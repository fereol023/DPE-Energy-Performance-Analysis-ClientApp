from content import *
from content import page1, page2, page3

# st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(layout="wide")

pages = {
    "Page 1 - Présentation": page1.main,
    "Page 2 - Dataviz": page2.main,
    "Page 2 - Démo": page3.main
}

st.sidebar.title('Navigation')
p = st.sidebar.radio('Aller à ', list(pages.keys()))

pages[p]()
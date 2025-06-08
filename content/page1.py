from content import *
import time


def main(*args, **kwargs):
    ville = kwargs.get("selected_ville", "")
    st.title("Diagnostics de performance énergétique " + ville)
    st.header("Présentation générale du projet")
    
    st.subheader("Contexte")
    st.markdown(f"""
Le changement climatique et la hausse des prix de l’énergie poussent à la sobriété énergétique.
Objectif politique : la neutralité carbone à l'horizon 2050, diminuer les GES des bâtiments d’ici 2030 
Rénovation énergétique est un levier économique clé car les bâtiments sont responsables d'une part importante des émissions de GES.
""")

    st.subheader("Problématique et objectifs")
    st.markdown(f"""
**Problématique :**
- Les estimations conventionnelles fournies dans les DPE reflètent-elles bien la réalité mesurée des consommations électriques ? 
- Et quelle est la variabilité restante due à l’hétérogénéité des modes de vie et taux d’occupation ?

**Objectifs :**
- étudier l’impact des caractéristiques du bâtiment ou des équipements (mode de chauffage, isolation, année de construction, etc.) sur la consommation électrique réelle
- modéliser la consommation électrique en fonction de la classe DPE, des habitudes de consommation et des caractéristiques des bâtiments, puis comparer avec la consommation réelle et analyser la part du delta expliquée par le DPE et celle expliquée par les habitudes
- se prononcer sur la conformité ou non des estimations de consommation présentées dans les DPE par rapport aux données réelles (consommation théorique vs consommation réelle)
- quantifier les gains potentiels liés à une amélioration de la performance énergétique d’un logement via une amélioration de la classe DPE (impact sur la consommation et éventuellement sur le prix, toutes choses égales par ailleurs)
- discuter l’impact des habitudes individuelles de consommation sur ces résultats, usage par usage : chauffage, eau chaude sanitaire, refroidissement, éclairage, autres
""")

    multi = f"""Les travaux réalisés dans le cadre de ce projet permettront :

• D’éclairer les décisions de rénovation en quantifiant les gains potentiels associés à une amélioration de la performance énergétique d’un logement reflétée par une amélioration du DPE

• De valider la conformité au réel des estimations de consommation électrique présentées dans les DPE par des comparaisons aux données de consommations réelles et de quantifier la variabilité due aux comportements individuels.
    """
    st.markdown(multi)
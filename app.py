import plotly.express as px
import streamlit as st

from calculs import base_100, moyenne_mobile, tableau_comparaison, telecharger_prix
from entreprises import ENTREPRISES, INDICE, NOM_INDICE

AVERTISSEMENT = ("Outil d'analyse à but pédagogique. Ceci n'est pas un conseil en investissement : "
                 "les performances passées ne préjugent pas des performances futures.")
PERIODES = {"6 mois": "6mo", "1 an": "1y", "2 ans": "2y", "5 ans": "5y"}

st.set_page_config(page_title="Les fournisseurs cachés de l'IA", layout="wide")
st.title("Les fournisseurs cachés de l'IA")
st.write("Des entreprises peu connues du grand public, mais sans lesquelles l'IA ne tournerait pas.")
st.warning(AVERTISSEMENT)

# --- Choix de l'utilisateur (barre latérale) ---
st.sidebar.header("Paramètres")
choix = st.sidebar.multiselect(
    "Entreprises",
    options=list(ENTREPRISES),
    default=list(ENTREPRISES),
    format_func=lambda t: ENTREPRISES[t]["nom"],
)
periode = st.sidebar.selectbox("Période", list(PERIODES), index=1)
fenetre = st.sidebar.slider("Moyenne mobile (jours)", 10, 200, 50, step=10)

if not choix:
    st.info("Choisis au moins une entreprise dans la barre latérale.")
    st.stop()


# On garde les données en mémoire 1 h pour ne pas interroger Yahoo à chaque clic.
@st.cache_data(ttl=3600)
def charger(tickers, periode):
    return telecharger_prix(tickers, periode)


prix = charger(choix + [INDICE], PERIODES[periode])
manquants = [t for t in choix + [INDICE] if t not in prix.columns]
if prix.empty or manquants:
    st.error(f"Données indisponibles pour : {', '.join(manquants) or 'tous les tickers'}. Réessaie plus tard.")
    st.stop()

noms = {t: ENTREPRISES[t]["nom"] for t in choix}
noms[INDICE] = NOM_INDICE

# --- 1. Courbe de prix et moyenne mobile ---
st.header("Prix et moyenne mobile")
ticker = st.selectbox("Entreprise", choix, format_func=lambda t: noms[t])
courbe = prix[[ticker]].rename(columns={ticker: "Prix"})
courbe[f"Moyenne mobile {fenetre} j"] = moyenne_mobile(courbe["Prix"], fenetre)
fig = px.line(courbe, labels={"value": "Prix (devise locale)", "Date": "", "variable": ""})
st.plotly_chart(fig, width="stretch")

# --- 2. Le panier comparé au Nasdaq (base 100) ---
st.header(f"Le panier « fournisseurs de l'IA » face au {NOM_INDICE}")
st.caption("Base 100 : chaque courbe démarre à 100, ce qui permet de comparer des actions de prix "
           "et de devises différents. Le panier est la moyenne des entreprises choisies (poids égaux).")
comparaison = base_100(prix)
comparaison["Panier IA"] = comparaison[choix].mean(axis=1)
comparaison = comparaison.rename(columns=noms)
fig = px.line(comparaison, labels={"value": "Base 100", "Date": "", "variable": ""})
st.plotly_chart(fig, width="stretch")

# --- 3. Tableau de comparaison ---
st.header("Tableau de comparaison")
tableau = tableau_comparaison(prix, noms)
st.dataframe(
    tableau.style.format({"Rendement": "{:+.1%}", "Volatilité annualisée": "{:.1%}"}),
    hide_index=True,
    width="stretch",
)
st.caption("Rendement : variation du prix sur la période. Volatilité annualisée : ampleur moyenne "
           "des variations quotidiennes, ramenée à un an (plus elle est haute, plus l'action bouge).")

# --- 4. Fiches entreprises ---
st.header("Rôle de chaque entreprise dans la chaîne de l'IA")
colonnes = st.columns(2)
for i, t in enumerate(choix):
    infos = ENTREPRISES[t]
    with colonnes[i % 2].container(border=True):
        st.subheader(f"{infos['nom']} ({t})")
        st.caption(infos["pays"])
        st.write(infos["role"])

st.divider()
st.caption(f"Données : Yahoo Finance via yfinance. {AVERTISSEMENT}")

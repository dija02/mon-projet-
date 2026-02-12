import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

st.set_page_config(page_title="Projet 1 - Streamlit App", layout="wide")

st.title("Projet 1 : Web Scraping & Dashboard")

# FONCTION SCRAPER SUR PLUSIEURS PAGES
def scrape_voitures(pages=3):
    data = []

    for page in range(1, pages + 1):
        url = f"https://dakar-auto.com/senegal/voitures-4?page={page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        containers = soup.find_all(
            "div",
            class_="listings-cards__list-item mb-md-3 mb-3"
        )

        for container in containers:
            try:
                title = container.find(
                    "h2",
                    class_="listing-card__header__title mb-md-2 mb-0"
                ).a.text.strip().split()

                marque = title[0]
                annee = title[-1]

                prix = container.find(
                    "h3",
                    class_="listing-card__header__price font-weight-bold text-uppercase mb-0"
                ).text.strip().replace("\u202f", "").replace(" F CFA", "")

                data.append({
                    "marque": marque,
                    "annee": annee,
                    "prix": prix
                })

            except:
                continue

    return pd.DataFrame(data)


# MENU
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Accueil",
        "Scraping en ligne",
        "Télécharger données brutes",
        "Dashboard",
        "Évaluation"
    ]
)

# ACCUEIL
if menu == "Accueil":
    st.write("Application de collecte et visualisation de données automobiles.")

# SCRAPER EN LIGNE
elif menu == "Scraping en ligne":

    pages = st.number_input("Nombre de pages à scraper", min_value=1, max_value=10, value=2)

    if st.button("Lancer le scraping"):
        df_scraped = scrape_voitures(pages)
        st.success("Scraping terminé")
        st.dataframe(df_scraped)

        csv = df_scraped.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger les données scrapées",
            csv,
            "scraping_result.csv",
            "text/csv"
        )

# TELECHARGER LES DONNEES BRUTES
elif menu == "Télécharger données brutes":

    with open("data/voiture.csv", "rb") as f:
        st.download_button("Voitures brut", f, "data/voiture.csv")

    with open("data/moto.csv", "rb") as f:
        st.download_button("Motos brut", f, "data/moto.csv")

    with open("data/locations.csv", "rb") as f:
        st.download_button("Locations brut", f, "data/locations.csv")

#DASHBOARD
elif menu == "Dashboard":

    choix = st.selectbox(
        "Choisir dataset",
        ["Voitures", "Motos", "Locations"]
    )

    if choix == "Voitures":
        df = pd.read_csv("data/voitures_clean.csv")
    elif choix == "Motos":
        df = pd.read_csv("data/motos_clean.csv")
    else:
        df = pd.read_csv("data/locations_clean.csv")

    st.subheader("Aperçu des données")
    st.dataframe(df)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Nombre d'annonces", df.shape[0])

    with col2:
        st.metric("Prix moyen", int(df["prix"].mean()))

    st.subheader("Top 10 marques")

    if "marque" in df.columns:
        top = df["marque"].value_counts().head(10)
        fig, ax = plt.subplots()
        top.plot(kind="bar", ax=ax)
        st.pyplot(fig)

elif menu == "Évaluation":

    st.subheader("Évaluation de l'application")

    st.info("Votre avis nous aide à améliorer l’application.")

    st.markdown(
        "### 👉 [Accéder au formulaire d’évaluation](https://docs.google.com/forms/d/e/1FAIpQLScE__vXc-YrV6Y1xb1kk0uFhMRC2NKdRLz6gdgr_0O5MxNqaA/viewform?usp=publish-editor)"
    )


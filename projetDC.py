import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

st.set_page_config(page_title="Projet 1 - Streamlit App", layout="wide")

st.title("Projet 1 : Web Scraping & Dashboard")

# FONCTION SCRAPER SUR PLUSIEURS PAGES

def scrape_data(categorie, pages):

    df = pd.DataFrame()

    if categorie == "Voitures":
        base_url = "https://dakar-auto.com/senegal/voitures-4"

    elif categorie == "Motos":
        base_url = "https://dakar-auto.com/senegal/motos-and-scooters-3"

    else:
        base_url = "https://dakar-auto.com/senegal/location-de-voitures-19"

    for index in range(1, pages + 1):

        url = f"{base_url}?&page={index}"

        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')

        containers = soup.find_all(
            'div',
            class_='listings-cards__list-item mb-md-3 mb-3'
        )

        data = []

        for container in containers:
            try:
                gen_inf = container.find(
                    'h2',
                    class_='listing-card__header__title mb-md-2 mb-0'
                ).a.text.strip().split()

                marque = gen_inf[0]
                annee = gen_inf[-1]

                prix = container.find(
                    'h3',
                    'listing-card__header__price font-weight-bold text-uppercase mb-0'
                ).text.strip().replace('\u202f', '').replace(' F CFA', '')

                quartier = container.find(
                    'span',
                    'town-suburb d-inline-block'
                ).text.strip()

                region = container.find(
                    'span',
                    'province font-weight-bold d-inline-block'
                ).text.strip()

                adresse = f"{quartier}, {region}"

                inf = container.find_all(
                    'li',
                    'listing-card__attribute list-inline-item'
                )

                vendeur_tag = container.find(
                    'div',
                    class_='listing-card__contact__title'
                )

                proprietaire = vendeur_tag.text.strip() if vendeur_tag else "N/A"

                # ================= VOITURES =================
                if categorie == "Voitures":

                    kilometrage = inf[1].text.strip().replace(' km', '').replace(' ', '') if len(inf) > 1 else ""
                    boite_de_vit = inf[2].text.strip() if len(inf) > 2 else ""
                    carburant = inf[3].text.strip() if len(inf) > 3 else ""

                    dic = {
                        'marque': marque,
                        'annee': annee,
                        'prix': prix,
                        'adresse': adresse,
                        'kilometrage': kilometrage,
                        'boite_de_vit': boite_de_vit,
                        'carburant': carburant,
                        'proprietaire': proprietaire
                    }

                # ================= MOTOS =================
                elif categorie == "Motos":

                    kilometrage = inf[1].text.strip().replace(' km', '').replace(' ', '') if len(inf) > 1 else ""

                    dic = {
                        'marque': marque,
                        'annee': annee,
                        'prix': prix,
                        'adresse': adresse,
                        'kilometrage': kilometrage,
                        'proprietaire': proprietaire
                    }

                # ================= LOCATIONS =================
                else:

                    dic = {
                        'marque': marque,
                        'annee': annee,
                        'prix': prix,
                        'adresse': adresse,
                        'proprietaire': proprietaire
                    }

                data.append(dic)

            except:
                pass

        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)

    return df



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

    categorie = st.selectbox(
        "Choisir une catégorie",
        ["Voitures", "Motos", "Locations"]
    )

    pages = st.number_input(
        "Nombre de pages",
        min_value=1,
        max_value=50,
        value=2
    )

    if st.button("Lancer le scraping"):
        df_scraped = scrape_data(categorie, pages)
        st.dataframe(df_scraped)


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





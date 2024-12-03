import os
import requests
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Créer un dossier pour stocker les images
OUTPUT_FOLDER = "images_profiles"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def login_to_facebook(browser, email, password):
    """
    Se connecter à Facebook
    """
    browser.get("https://mbasic.facebook.com")
    time.sleep(2)
    browser.find_element(By.NAME, "email").send_keys(email)
    browser.find_element(By.NAME, "pass").send_keys(password)
    browser.find_element(By.NAME, "login").click()
    time.sleep(5)

def scrape_profiles(browser, keyword):
    """
    Scraper les photos de profils pour un mot-clé donné et les sauvegarder
    """
    # Naviguer à la page des résultats
    search_url = f"https://www.facebook.com/search/results/?q={keyword}"
    browser.get(search_url)
    time.sleep(5)

    # Récupérer les photos de profil
    profile_images = browser.find_elements(By.CSS_SELECTOR, "img")
    st.write(f"Nombre d'images trouvées : {len(profile_images)}")

    # Télécharger et enregistrer chaque image
    for index, img in enumerate(profile_images):
        try:
            img_url = img.get_attribute("src")
            if img_url:
                # Télécharger l'image
                response = requests.get(img_url)
                if response.status_code == 200:
                    file_path = f"{OUTPUT_FOLDER}/profile_{index+1}.jpg"
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                    st.image(file_path, caption=f"Profile {index+1}", use_column_width=True)
        except Exception as e:
            st.error(f"Erreur lors du téléchargement de l'image {index+1}: {e}")

# Streamlit App
st.title("Scraper de photos de profils Facebook")

email = st.text_input("Email Facebook", type="default")
password = st.text_input("Mot de passe Facebook", type="password")
keyword = st.text_input("Mot-clé pour la recherche", placeholder="Entrez un mot-clé")

if st.button("Lancer le Scraping"):
    if not email or not password or not keyword:
        st.error("Veuillez remplir tous les champs.")
    else:
        # Lancer le navigateur
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        try:
            st.info("Connexion à Facebook...")
            login_to_facebook(browser, email, password)
            
            st.info("Scraping des photos...")
            scrape_profiles(browser, keyword)
            st.success("Scraping terminé avec succès.")
        finally:
            browser.quit()

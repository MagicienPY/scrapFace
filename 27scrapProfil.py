import os
import requests
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import cv2
import uuid

# Dossier pour les images
OUTPUT_FOLDER = "images_profiles"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Détection de visage avec OpenCV
CASCADE_PATH = 'haarcascade_frontalface_default.xml'
if not os.path.exists(CASCADE_PATH):
    st.error(f"Fichier {CASCADE_PATH} manquant. Veuillez le placer dans le dossier racine.")
    st.stop()

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

def contains_face(image_path):
    """
    Vérifie si une image contient un ou plusieurs visages.
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0

def get_browser():
    """
    Initialise le navigateur Selenium en mode headless.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return browser

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
    search_url = f"https://mbasic.facebook.com/search/people/?q={keyword}"
    browser.get(search_url)
    time.sleep(5)
    
    # Scroller pour charger plus de résultats
    for _ in range(5):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    # Récupérer les images
    profile_images = browser.find_elements(By.TAG_NAME, "img")
    downloaded_urls = set()
    st.write(f"Nombre d'images trouvées : {len(profile_images)}")

    for index, img in enumerate(profile_images):
        try:
            img_url = img.get_attribute("src")
            if img_url and img_url not in downloaded_urls:
                downloaded_urls.add(img_url)

                # Télécharger l'image
                response = requests.get(img_url)
                if response.status_code == 200:
                    unique_id = uuid.uuid4().hex
                    file_path = f"{OUTPUT_FOLDER}/profile_{unique_id}.jpg"
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                    
                    # Vérifier si l'image contient un visage
                    if contains_face(file_path):
                        st.image(file_path, caption=f"Profile {index+1}", use_column_width=True)
                    else:
                        os.remove(file_path)
        except Exception as e:
            st.error(f"Erreur lors du téléchargement de l'image {index+1}: {e}")

# Streamlit App
st.title("Scraping de Profils Facebook")

email = st.text_input("Email Facebook", type="default")
password = st.text_input("Mot de passe Facebook", type="password")
keyword = st.text_input("Mot-clé pour la recherche", placeholder="Entrez un mot-clé")

if st.button("Lancer le Scraping"):
    if not email or not password or not keyword:
        st.error("Veuillez remplir tous les champs.")
    else:
        browser = get_browser()
        try:
            st.info("Connexion à Facebook...")
            login_to_facebook(browser, email, password)

            st.info("Scraping des photos...")
            scrape_profiles(browser, keyword)
            st.success("Scraping terminé avec succès.")
        finally:
            browser.quit()

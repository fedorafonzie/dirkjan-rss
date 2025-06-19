import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

print("Script gestart: Ophalen van dagelijkse strips met unieke datums.")

DIRKJAN_URL = 'https://dirkjan.nl/'

try:
    response = requests.get(DIRKJAN_URL)
    response.raise_for_status()
    print("SUCCES: Hoofdpagina HTML opgehaald.")
except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon hoofdpagina niet ophalen. Fout: {e}")
    exit(1)

soup = BeautifulSoup(response.content, 'html.parser')
print("Zoeken naar de navigatiebalk...")
navigation_div = soup.find('div', class_='post-navigation')

if not navigation_div:
    print("FOUT: De <div class='post-navigation'> is niet gevonden.")
    exit(1)

day_links = navigation_div.find_all('a')
if not day_links:
    print("FOUT: Geen dag-links gevonden.")
    exit(1)

print(f"SUCCES: {len(day_links)} dag-links gevonden.")

fg = FeedGenerator()
fg.id(DIRKJAN_URL)
fg.title('Dirkjan Strips')
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.description('De dagelijkse Dirkjan strips.')
fg.language('nl')

print("\nVerwerken van elke dag-pagina...")
for link in reversed(day_links):
    page_url = link.get('href')
    day_name = link.text.strip()
    
    if not page_url:
        continue

    print(f"--- Verwerken: {day_name} ({page_url}) ---")

    try:
        # --- NIEUWE LOGICA: Datum extractie ---
        # Haal de datumstring (bv. '20250616') uit de URL
        date_str = page_url.strip('/').split('/')[-1].split('_')[0]
        
        # Converteer de string naar een datetime object
        # Maak het 'timezone-aware', wat best practice is voor RSS
        amsterdam_tz = pytz.timezone("Europe/Amsterdam")
        publish_date = amsterdam_tz.localize(datetime.strptime(date_str, '%Y%m%d').replace(hour=8)) # Zet publicatietijd op 08:00
        print(f"  INFO: Publicatiedatum verwerkt: {publish_date}")
        # ------------------------------------

        page_response = requests.get(page_url)
        page_response.raise_for_status()
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        
        cartoon_article = page_soup.find('article', class_='cartoon')
        if not cartoon_article: continue
            
        img_tag = cartoon_article.find('img')
        if not img_tag: continue
            
        image_url = img_tag.get('src')
        if not image_url: continue
            
        print(f"  SUCCES: Afbeelding gevonden.")

        fe = fg.add_entry()
        fe.id(image_url)
        fe.title(f'Dirkjan - {day_name}')
        fe.link(href=page_url)
        fe.pubDate(publish_date) # Voeg de unieke publicatiedatum toe
        fe.description(f'<img src="{image_url}" alt="Dirkjan Strip voor {day_name}" />')

    except Exception as e:
        print(f"  FOUT: Kon pagina {page_url} niet verwerken. Fout: {e}")

try:
    fg.rss_file('dirkjan.xml', pretty=True)
    print("\nSUCCES: 'dirkjan.xml' is aangemaakt met unieke datums.")
except Exception as e:
    print(f"\nFOUT: Kon het finale bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)

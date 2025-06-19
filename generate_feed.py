import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
# De 'pytz' import is verwijderd en vervangen door standaard-bibliotheek modules
from datetime import datetime, timezone, timedelta 

print("Script gestart: Test met alleen de strip van dinsdag 17 juni (zonder pytz).")

# Constante voor de feed-metadata
DIRKJAN_URL = 'https://dirkjan.nl/'

# Hardcoded data voor de test
test_url_info = {
    'url': 'https://dirkjan.nl/cartoon/20250617_686279286/',
    'day': 'Dinsdag'
}

# Stap 1: Initialiseer de RSS-feed met een nieuwe, unieke test-ID
fg = FeedGenerator()
fg.id('https://dirkjan.nl/feed/test-17-juni-no-pytz-v2') 
fg.title('Dirkjan Strips (Alleen Dinsdag Test, no-pytz)')
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.description('Test-feed met alleen de strip van dinsdag 17 juni.')
fg.language('nl')

# Stap 2: Verwerk de specifieke pagina
page_url = test_url_info['url']
day_name = test_url_info['day']

print(f"--- Verwerken: {day_name} ({page_url}) ---")

try:
    # --- AANGEPASTE LOGICA: Datum zonder Pytz ---
    # Haal de datumstring (bv. '20250617') uit de URL
    date_str = page_url.strip('/').split('/')[-1].split('_')[0]
    
    # Maak een "naive" datetime object aan (zonder tijdzone)
    naive_datetime = datetime.strptime(date_str, '%Y%m%d').replace(hour=8)
    
    # Maak een tijdzone-object voor de Nederlandse tijdzone in de zomer (CEST, UTC+2)
    cest_tz = timezone(timedelta(hours=2))
    
    # Voeg de tijdzone-informatie toe aan het datetime object
    publish_date = naive_datetime.replace(tzinfo=cest_tz)
    print(f"  INFO: Publicatiedatum verwerkt: {publish_date}")
    # ----------------------------------------------

    # Haal de HTML van de dag-pagina op
    page_response = requests.get(page_url)
    page_response.raise_for_status()
    page_soup = BeautifulSoup(page_response.content, 'html.parser')
    
    # Vind de afbeelding
    cartoon_article = page_soup.find('article', class_='cartoon')
    img_tag = cartoon_article.find('img')
    image_url = img_tag.get('src')
    
    print(f"  SUCCES: Afbeelding gevonden.")

    # Voeg het ene item toe aan de feed
    fe = fg.add_entry()
    fe.id(image_url) 
    fe.title(f'Dirkjan - {day_name}')
    fe.link(href=page_url)
    fe.pubDate(publish_date)
    fe.description(f'<img src="{image_url}" alt="Dirkjan Strip voor {day_name}" />')

except Exception as e:
    print(f"  FOUT: Kon pagina {page_url} niet verwerken. Fout: {e}")
    exit(1)

# Stap 3: Schrijf het finale XML-bestand weg
try:
    fg.rss_file('dirkjan.xml', pretty=True)
    print("\nSUCCES: 'dirkjan.xml' is aangemaakt met alleen de strip van dinsdag.")
except Exception as e:
    print(f"\nFOUT: Kon het finale bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)

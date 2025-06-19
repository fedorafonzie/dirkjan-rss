import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

print("Script gestart: Test met alleen de strip van dinsdag 17 juni.")

# Hardcoded lijst met alleen de URL voor dinsdag
test_url_info = {
    'url': 'https://dirkjan.nl/cartoon/20250617_686279286/',
    'day': 'Dinsdag'
}

# Stap 1: Initialiseer de RSS-feed met een unieke test-ID
fg = FeedGenerator()
# Gebruik een unieke ID voor deze test om caching te omzeilen
fg.id('https://dirkjan.nl/feed/test-17-juni-2025') 
fg.title('Dirkjan Strips (Alleen Dinsdag Test)')
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.description('Test-feed met alleen de strip van dinsdag 17 juni.')
fg.language('nl')


# Stap 2: Verwerk de ene, specifieke pagina
page_url = test_url_info['url']
day_name = test_url_info['day']

print(f"--- Verwerken: {day_name} ({page_url}) ---")

try:
    # Haal de HTML van de dag-pagina op
    page_response = requests.get(page_url)
    page_response.raise_for_status()
    page_soup = BeautifulSoup(page_response.content, 'html.parser')
    
    # Vind de afbeelding
    cartoon_article = page_soup.find('article', class_='cartoon')
    img_tag = cartoon_article.find('img')
    image_url = img_tag.get('src')
    
    # Extraheer de datum uit de URL
    date_str = page_url.strip('/').split('/')[-1].split('_')[0]
    amsterdam_tz = pytz.timezone("Europe/Amsterdam")
    publish_date = amsterdam_tz.localize(datetime.strptime(date_str, '%Y%m%d').replace(hour=8))
    
    print(f"  SUCCES: Afbeelding en datum gevonden.")

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

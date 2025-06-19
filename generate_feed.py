import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# URL van de hoofdpagina met de nieuwste strip
DIRKJAN_URL = 'https://dirkjan.nl/'

# 1. Haal de HTML op
try:
    response = requests.get(DIRKJAN_URL)
    response.raise_for_status() # Stopt het script als de pagina niet bereikbaar is
except requests.exceptions.RequestException as e:
    print(f"Fout bij het ophalen van de pagina: {e}")
    exit()

# 2. Parse de HTML met BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Zoek de container van de nieuwste strip
# Dit is het meest kwetsbare deel; de class 'cartoon-image-wrapper' moet correct zijn.
# Deze moet u zelf verifiëren door de HTML van de site te inspecteren.
latest_cartoon_wrapper = soup.find('div', class_='cartoon-image-wrapper')

if not latest_cartoon_wrapper:
    print("Kan de container van de strip niet vinden. Is de website-structuur veranderd?")
    exit()

# Haal de informatie uit de container
link_tag = latest_cartoon_wrapper.find('a')
img_tag = latest_cartoon_wrapper.find('img')

if not link_tag or not img_tag:
    print("Kan de link of afbeelding in de container niet vinden.")
    exit()

cartoon_url = link_tag['href']
cartoon_title = img_tag.get('alt', 'Dirkjan Strip') # Gebruik 'alt' tekst als titel
cartoon_img_src = img_tag['src']
cartoon_description = f'<img src="{cartoon_img_src}" alt="{cartoon_title}" />'

# 3. Genereer de RSS-feed
fg = FeedGenerator()
fg.id(DIRKJAN_URL)
fg.title('Dirkjan Strips (Custom Feed)')
fg.author({'name': 'Dirkjan Fan'})
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.subtitle('De allernieuwste Dirkjan strip, automatisch ververst.')
fg.language('nl')

# Voeg de gevonden strip toe als een item in de feed
fe = fg.add_entry()
fe.id(cartoon_url)
fe.title(cartoon_title)
fe.link(href=cartoon_url)
fe.description(cartoon_description, isSummary=False)

# 4. Sla de feed op als een XML-bestand
fg.rss_file('dirkjan.xml', pretty=True) # pretty=True maakt het bestand leesbaar

print("RSS-feed 'dirkjan.xml' succesvol aangemaakt.")
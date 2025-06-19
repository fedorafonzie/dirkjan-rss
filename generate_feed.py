import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

print("Script gestart: Ophalen van webpagina.")

# URL van de te parsen pagina
DIRKJAN_URL = 'https://dirkjan.nl/'

# Stap 1: Haal de webpagina op
try:
    response = requests.get(DIRKJAN_URL)
    response.raise_for_status()
    print("SUCCES: Website HTML opgehaald.")
except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon website niet ophalen. Fout: {e}")
    exit(1)

# Stap 2: Parse de HTML en vind de afbeelding
soup = BeautifulSoup(response.content, 'html.parser')
print("Zoeken naar de comic-afbeelding...")

# Zoek naar de <article> tag met class="cartoon"
cartoon_article = soup.find('article', class_='cartoon')

if not cartoon_article:
    print("FOUT: De <article class='cartoon'> tag is niet gevonden.")
    exit(1)

# Zoek binnen die article-tag naar de <img> tag
img_tag = cartoon_article.find('img')

if not img_tag:
    print("FOUT: De <img> tag is niet gevonden binnen de article-tag.")
    exit(1)

# Haal de URL uit het 'src' attribuut van de image-tag
image_url = img_tag.get('src')
if not image_url:
    print("FOUT: De <img> tag heeft geen 'src' attribuut.")
    exit(1)

print(f"SUCCES: Afbeelding URL gevonden: {image_url}")

# Stap 3: Bouw de RSS-feed met de gevonden afbeelding
fg = FeedGenerator()
fg.id(DIRKJAN_URL)
fg.title('Dirkjan Strips')
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.description('De allernieuwste Dirkjan strip.')
fg.language('nl')

# Voeg de strip toe als een nieuw item in de feed
fe = fg.add_entry()
fe.id(image_url)  # Gebruik de unieke image URL als ID
fe.title('Dirkjan Strip van vandaag') # Titel voor het item
fe.link(href=image_url) # Link voor nu naar de afbeelding zelf

# Dit is de cruciale stap: plaats een HTML <img> tag in de beschrijving
fe.description(f'<img src="{image_url}" alt="Dirkjan Strip" />')


# Stap 4: Schrijf het XML-bestand weg
try:
    fg.rss_file('dirkjan.xml', pretty=True)
    print("SUCCES: 'dirkjan.xml' is aangemaakt met daarin de afbeelding.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)

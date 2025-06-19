import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import re

print("Script gestart: Ophalen van dagelijkse strips.")

# URL van de hoofdpagina
DIRKJAN_URL = 'https://dirkjan.nl/'

# Stap 1: Haal de hoofdpagina op
try:
    response = requests.get(DIRKJAN_URL)
    response.raise_for_status()
    print("SUCCES: Hoofdpagina HTML opgehaald.")
except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon hoofdpagina niet ophalen. Fout: {e}")
    exit(1)

# Stap 2: Parse de HTML en vind de navigatielinks voor de dagen
soup = BeautifulSoup(response.content, 'html.parser')
print("Zoeken naar de navigatiebalk met dagen...")

navigation_div = soup.find('div', class_='post-navigation')

if not navigation_div:
    print("FOUT: De <div class='post-navigation'> is niet gevonden.")
    exit(1)

day_links = navigation_div.find_all('a')

if not day_links:
    print("FOUT: Geen dag-links gevonden in de navigatiebalk.")
    exit(1)

print(f"SUCCES: {len(day_links)} dag-links gevonden.")

# Stap 3: Initialiseer de RSS-feed
fg = FeedGenerator()
fg.id(DIRKJAN_URL)
fg.title('Dirkjan Strips')
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.description('De dagelijkse Dirkjan strips.')
fg.language('nl')

# Stap 4: Loop door elke dag-link, bezoek de pagina en voeg de strip toe
print("\nVerwerken van elke dag-pagina...")
for link in day_links:
    page_url = link.get('href')
    day_name = link.text.strip()
    
    if not page_url:
        print(f"WAARSCHUWING: Link gevonden zonder href. Overslaan.")
        continue

    print(f"--- Verwerken: {day_name} ({page_url}) ---")

    try:
        page_response = requests.get(page_url)
        page_response.raise_for_status()
        
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        
        cartoon_article = page_soup.find('article', class_='cartoon')
        if not cartoon_article:
            print("  FOUT: Kon <article class='cartoon'> niet vinden op deze pagina. Overslaan.")
            continue
            
        img_tag = cartoon_article.find('img')
        if not img_tag:
            print("  FOUT: Kon <img> tag niet vinden. Overslaan.")
            continue
            
        image_url = img_tag.get('src')
        if not image_url:
            print("  FOUT: <img> tag heeft geen 'src'. Overslaan.")
            continue
            
        print(f"  SUCCES: Afbeelding gevonden: {image_url}")

        fe = fg.add_entry()
        fe.id(page_url)
        fe.title(f'Dirkjan - {day_name}')
        fe.link(href=page_url)
        fe.description(f'<img src="{image_url}" alt="Dirkjan Strip voor {day_name}" />')

    except requests.exceptions.RequestException as e:
        print(f"  FOUT: Kon pagina {page_url} niet ophalen. Fout: {e}")

# Stap 5: Schrijf het finale XML-bestand weg
try:
    fg.rss_file('dirkjan.xml', pretty=True

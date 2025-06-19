import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import re

print("Script gestart: Genereren van feed met alleen handmatige correctie van lastBuildDate.")

DIRKJAN_URL = 'https://dirkjan.nl/'

try:
    response = requests.get(DIRKJAN_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    navigation_div = soup.find('div', class_='post-navigation')
    day_links = navigation_div.find_all('a')
except Exception as e:
    print(f"FOUT: Kon de hoofdpagina niet parsen. Fout: {e}")
    exit(1)

print(f"INFO: {len(day_links)} dag-links gevonden.")

fg = FeedGenerator()
fg.id(DIRKJAN_URL)
fg.title('Dirkjan Strips')
fg.link(href=DIRKJAN_URL, rel='alternate')
fg.description('De dagelijkse Dirkjan strips.')
fg.language('nl')

for link in reversed(day_links):
    try:
        page_url = link.get('href')
        day_name = link.text.strip()
        if not page_url: continue

        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        
        cartoon_article = page_soup.find('article', class_='cartoon')
        img_tag = cartoon_article.find('img')
        image_url = img_tag.get('src')
        if not image_url: continue

        # Voeg item toe aan de feed ZONDER pubDate
        fe = fg.add_entry()
        fe.id(image_url)
        fe.title(f'Dirkjan - {day_name}')
        fe.link(href=page_url)
        fe.description(f'<img src="{image_url}" alt="Dirkjan Strip voor {day_name}" />')
    except Exception as e:
        print(f"INFO: Kon item voor {page_url} niet verwerken. Fout: {e}")


# Handmatige correctie van lastBuildDate
try:
    # Genereer de feed als een string
    xml_string_met_foute_datum = fg.rss_str(pretty=True).decode('utf-8')

    # Creëer de correcte datumstring in CEST (+02:00)
    cest_tz = timezone(timedelta(hours=2))
    now_cest = datetime.now(timezone.utc).astimezone(cest_tz)
    correct_date_string = now_cest.strftime("%a, %d %b %Y %H:%M:%S %z")

    # Vervang de volledige <lastBuildDate> tag in de string
    gecorrigeerde_xml_string = re.sub(
        r'<lastBuildDate>.*?</lastBuildDate>',
        f'<lastBuildDate>{correct_date_string}</lastBuildDate>',
        xml_string_met_foute_datum
    )

    # Schrijf de gecorrigeerde string naar het .xml bestand
    with open('dirkjan.xml', 'w', encoding='utf-8') as f:
        f.write(gecorrigeerde_xml_string)
    
    print("\nSUCCES: 'dirkjan.xml' is aangemaakt met handmatig gecorrigeerde lastBuildDate.")

except Exception as e:
    print(f"\nFOUT: Kon het finale bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)

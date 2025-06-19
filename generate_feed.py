import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta

print("Script gestart: Generatie van unieke feed-bestandsnaam, unieke item-IDs, unieke datums en redirect.")

# --- Stap 1: Genereer een unieke bestandsnaam voor de XML ---
unique_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
xml_filename = f"dirkjan_feed_{unique_timestamp}.xml"
print(f"INFO: Unieke bestandsnaam voor deze run: {xml_filename}")

# --- Stap 2: Maak de inhoud voor het index.html redirect-bestand ---
redirect_html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>Dirkjan RSS Feed</title>
<meta http-equiv="refresh" content="0; url={xml_filename}" />
<link rel="alternate" type="application/rss+xml" href="{xml_filename}" title="Dirkjan RSS Feed">
</head>
<body>
<p>Doorverwijzing naar de RSS feed: <a href="{xml_filename}">{xml_filename}</a>.</p>
</body>
</html>
"""

# --- Stap 3: Haal de strip-informatie op ---
DIRKJAN_URL = 'https://dirkjan.nl/'
try:
    response = requests.get(DIRKJAN_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    navigation_div = soup.find('div', class_='post-navigation')
    day_links = navigation_div.find_all('a')
    print(f"INFO: {len(day_links)} dag-links gevonden om te verwerken.")
except Exception as e:
    print(f"FOUT: Kon de hoofdpagina niet parsen. Fout: {e}")
    exit(1)

# --- Stap 4: Bouw de RSS-feed ---
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

        date_str = page_url.strip('/').split('/')[-1].split('_')[0]
        # Gebruik een consistente tijdzone voor de publicatiedatum
        cet_tz = timezone(timedelta(hours=2))
        publish_date = datetime.strptime(date_str, '%Y%m%d').replace(hour=8).replace(tzinfo=cet_tz)

        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')
        cartoon_article = page_soup.find('article', class_='cartoon')
        img_tag = cartoon_article.find('img')
        image_url = img_tag.get('src')
        if not image_url: continue

        fe = fg.add_entry()
        # Gebruik de unieke afbeelding-URL als item-ID
        fe.id(image_url)
        fe.title(f'Dirkjan - {day_name}')
        fe.link(href=page_url)
        # Voeg de unieke publicatiedatum toe
        fe.pubDate(publish_date)
        fe.description(f'<img src="{image_url}" alt="Dirkjan Strip voor {day_name}" />')
    except Exception as e:
        print(f"INFO: Kon item voor {page_url} niet verwerken. Fout: {e}")

# --- Stap 5: Schrijf BEIDE bestanden weg ---
try:
    fg.rss_file(xml_filename, pretty=True)
    print(f"SUCCES: '{xml_filename}' aangemaakt.")
    
    with open("index.html", "w") as f:
        f.write(redirect_html_content)
    print("SUCCES: 'index.html' redirect-bestand aangemaakt.")
except Exception as e:
    print(f"FOUT: Kon de bestanden niet wegschrijven. Foutmelding: {e}")
    exit(1)

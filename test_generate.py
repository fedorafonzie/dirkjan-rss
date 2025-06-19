print("Start van het Python test-script...")

try:
    # Maak een simpel index.html bestand aan en schrijf er een regel in
    with open("index.html", "w") as f:
        f.write("<h1>Deze pagina is door Python gemaakt!</h1>")

    print("Bestand 'index.html' succesvol aangemaakt.")

except Exception as e:
    # Als er iets misgaat met het schrijven van het bestand, geef een foutmelding
    print(f"Fout tijdens het aanmaken van het bestand: {e}")
    exit(1) # Stop de workflow met een foutcode

print("Test-script succesvol afgerond.")
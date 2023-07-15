import string

from bs4 import BeautifulSoup as bs
import requests
import time

import airlines_db as db

# Utilisation de la page en anglais, celle en français a un é que request n'arrive pas à interprété
WIKIPEDIA_BASE_URL = u'https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_{}'

print(WIKIPEDIA_BASE_URL.encode('utf-8', errors='ignore'))


def import_airports_from_wikipedia():
    """
    Imports all airports found in Wikipedia
    """
    # Connexion à la base
    air_db = db.AirlinesDb()
    air_db.connect()
    total = 0
    # parcours des lettres majuscules
    for letter in string.ascii_uppercase:
        url = WIKIPEDIA_BASE_URL.format(letter)
        print(url)
        res = requests.get(url)
        soup = bs(res.text, "html.parser")
        # Analyse du site : focus sur les balises "tr" de la balise "tbody"
        all_tr = soup.find('tbody').find_all("tr")

        batch_size = 0
        for tag in all_tr:
            all_tds = tag.find_all("td")
            if len(all_tds) > 0:
                iata_code = all_tds[0].text
                icao_code = all_tds[1].text
                airport_name = all_tds[2].text
                if iata_code:
                    batch_size += 1
                    air_db.add_airport(iata_code, icao_code, airport_name)
        print(f"lettre {letter}: {batch_size} aéroports")
        total += batch_size
        # Pause a little bit to avoid making too many calls per second
        print("Pause ...")
        time.sleep(0.1)

    air_db.close()
    print(f"Total {total} aéroports")


if __name__ == '__main__':
    import_airports_from_wikipedia()

import re
import hashlib
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sok.se"
START_URL = "https://sok.se/olympiska-spel/tavlingar/spelen/milano-cortina-2026/truppen.html"

def make_athlete_id(name: str, sport: str) -> str:
    # Stabilt id baserat på namn+sport (så att samma person får samma id vid omkörning)
    h = hashlib.sha1(f"{name}|{sport}".encode("utf-8")).hexdigest()[:10]
    return f"swe_{h}"

def parse_page(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # Varje kort innehåller typiskt:
    # ### Namn
    # #### Sport
    # På sidan syns de som h3/h4 (ibland med varierande wrappers)
    names = [h.get_text(strip=True) for h in soup.find_all(["h3"])]

    # Sports ligger ofta i h4 direkt efter h3 i flödet,
    # men för att vara robust plockar vi par via närmaste h4 efter varje h3.
    rows = []
    for h3 in soup.find_all("h3"):
        name = h3.get_text(strip=True)
        h4 = h3.find_next("h4")
        sport = h4.get_text(" ", strip=True) if h4 else ""
        sport = re.sub(r"\s+", " ", sport).strip()
        if name and sport:
            rows.append((name, sport))
    return rows, soup

def find_next_page_url(soup: BeautifulSoup, current_url: str):
    # Sidan har en "Nästa"-länk i pagineringen.
    a = soup.find("a", string=re.compile(r"^Nästa$", re.IGNORECASE))
    if not a or not a.get("href"):
        return None
    return urljoin(current_url, a["href"])

def main():
    all_rows = []
    url = START_URL

    for _ in range(50):  # säkerhetsstopp
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        rows, soup = parse_page(r.text)
        all_rows.extend(rows)

        next_url = find_next_page_url(soup, url)
        if not next_url:
            break
        url = next_url

    # Rensa dubletter
    df = pd.DataFrame(all_rows, columns=["name", "sport"]).drop_duplicates()

    # Skapa athlete_id
    df["athlete_id"] = df.apply(lambda x: make_athlete_id(x["name"], x["sport"]), axis=1)

    # Ordna kolumner och sortera
    df = df[["athlete_id", "name", "sport"]].sort_values(["sport", "name"]).reset_index(drop=True)

    # Skriv till data/athletes.csv
    out_path = "data/athletes.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Skrev {len(df)} rader till {out_path}")

if __name__ == "__main__":
    main()

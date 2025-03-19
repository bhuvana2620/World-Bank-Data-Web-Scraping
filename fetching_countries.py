import requests
import sqlite3
from bs4 import BeautifulSoup
import re  # To extract country codes

# Database setup
DB_NAME = "worldbankorg.db"

def fetch_countries():
    """Scrape World Bank Country Data and Extract Country Codes."""
    url = "https://data.worldbank.org/country"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract country links
    country_links = soup.find_all('a', href=True)
    countries = []

    for link in country_links:
        country_name = link.get_text().strip()

        if '/country/' in link['href']:
            country_url = "https://data.worldbank.org" + link['href']
            
            # Extract country code using regex
            match = re.search(r'/country/([a-zA-Z]{2,3})', link['href'])
            country_code = match.group(1).upper() if match else "N/A"

            countries.append((country_code, country_name, country_url))

    return countries

def save_to_database(countries):
    """Save extracted data to SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT UNIQUE,
            name TEXT,
            url TEXT
        )
    """)

    # Insert data (Ensuring country_code is unique)
    cursor.executemany("INSERT OR REPLACE INTO countries (country_code, name, url) VALUES (?, ?, ?)", countries)

    conn.commit()
    conn.close()
    print(f"✅ Data saved to database {DB_NAME}")

if __name__ == "__main__":
    country_data = fetch_countries()
    save_to_database(country_data)
    print("✅ Scraping and Database Update Complete!")

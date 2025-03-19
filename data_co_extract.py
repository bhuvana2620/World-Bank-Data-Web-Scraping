import sqlite3
import requests
import json
from datetime import datetime
import uuid

def get_countries_from_db(db_path):
    """Retrieve country codes from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT country_code FROM countries")  # Ensure 3-letter country codes
    countries = {row[0]: row[0] for row in cursor.fetchall()}  # Create a mapping
    conn.close()
    return countries

def fetch_worldbank_data(country, indicator):
    """Fetch indicator data from the World Bank API."""
    url = f"http://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=100"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 1:
            return data[1]
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching data for {country}, Indicator {indicator}: {e}")
    return []

def store_data_to_db(db_path, data, country_mapping):
    """Store retrieved data into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indicators_data (
            id TEXT PRIMARY KEY,
            country TEXT,
            indicator TEXT,
            indicator_description TEXT,
            year INTEGER,
            value REAL,
            retrieved_at TEXT
        )
    ''')
    
    for record in data:
        if record.get("value") is not None:
            country_code = country_mapping.get(record['country']['id'], record['country']['id'])  # Ensure correct 3-letter code
            indicator_desc = {
                "SI.POV.DDAY": "Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)",
                "SP.DYN.LE00.IN": "Life expectancy at birth, total (years)",
                "SP.POP.TOTL": "Population, total",
                "SP.POP.GROW": "Population growth (annual %)",
                "SM.POP.NETM": "Net migration",
                "NY.GDP.MKTP.CD": "GDP (current US$)",
                "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
                "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
                "SL.UEM.TOTL.ZS": "Unemployment, total (% of total labor force)",
                "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
                "BX.TRF.PWKR.DT.GD.ZS": "Personal remittances, received (% of GDP)",
                "HD.HCI.OVRL": "Human Capital Index (HCI) (scale 0-1)",
                "AG.LND.FRST.ZS": "Forest area (% of land area)",
                "EG.ELC.ACCS.ZS": "Access to electricity (% of population)",
                "ER.H2O.FWTL.ZS": "Annual freshwater withdrawals (% of internal resources)",
                "EG.ELC.RNWX.ZS": "Electricity production from renewables, excluding hydroelectric (% of total)",
                "SH.STA.SMSS.ZS": "People using safely managed sanitation services (% of population)",
                "VC.IHR.PSRC.P5": "Intentional homicides (per 100,000 people)",
                "GC.DOD.TOTL.GD.ZS": "Central government debt, total (% of GDP)",
                "IQ.SPI.OVRL": "Statistical performance indicators (SPI): Overall score (scale 0-100)",
                "IT.NET.USER.ZS": "Individuals using the Internet (% of population)",
                "SG.GEN.PARL.ZS": "Proportion of seats held by women in national parliaments (%)",
                "BX.KLT.DINV.WD.GD.ZS": "Foreign direct investment, net inflows (% of GDP)",
                "EN.ATM.CO2E.PC": "CO2 emissions (metric tons per capita)"
            }
            
            cursor.execute('''
                INSERT OR REPLACE INTO indicators_data (id, country, indicator, indicator_description, year, value, retrieved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                country_code,
                record['indicator']['id'],
                indicator_desc.get(record['indicator']['id'], 'Description not available'),
                record['date'],
                record['value'],
                datetime.utcnow().isoformat()
            ))
    
    conn.commit()
    conn.close()

def main():
    db_path = "worldbankorg.db"
    
    indicators = [
        "SI.POV.DDAY", "SP.DYN.LE00.IN", "SP.POP.TOTL", "SP.POP.GROW", "SM.POP.NETM",
        "NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD", "NY.GDP.MKTP.KD.ZG", "SL.UEM.TOTL.ZS", "FP.CPI.TOTL.ZG",
        "BX.TRF.PWKR.DT.GD.ZS", "HD.HCI.OVRL", "AG.LND.FRST.ZS", "EG.ELC.ACCS.ZS", "ER.H2O.FWTL.ZS",
        "EG.ELC.RNWX.ZS", "SH.STA.SMSS.ZS", "VC.IHR.PSRC.P5", "GC.DOD.TOTL.GD.ZS", "IQ.SPI.OVRL",
        "IT.NET.USER.ZS", "SG.GEN.PARL.ZS", "BX.KLT.DINV.WD.GD.ZS", "EN.ATM.CO2E.PC"
    ]
    
    country_mapping = get_countries_from_db(db_path)
    
    all_data = []
    for country in country_mapping.keys():
        for indicator in indicators:
            data = fetch_worldbank_data(country, indicator)
            if data:
                all_data.extend(data)
    
    store_data_to_db(db_path, all_data, country_mapping)
    print("Data retrieval and storage complete.")

if __name__ == "__main__":
    main()

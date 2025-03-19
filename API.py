from fastapi import FastAPI, HTTPException
import sqlite3
import os
from typing import List, Optional

app = FastAPI()
DB_PATH = "worldbankorg.db"

def fetch_data_from_db(query: str, params: tuple = ()):
    """Fetch data from the SQLite database safely."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row  # Fetch results as dictionaries
            cursor = conn.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall()
            return data
    except sqlite3.Error as e:
        print(f"SQLite Error: {str(e)}")  # Debugging info
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/")
def home():
    return {"message": "Welcome to the World Bank Data API"}

@app.get("/countries")
def get_countries():
    """Get list of available countries from the 'countries' table."""
    query = "SELECT DISTINCT country_code, name FROM countries"
    countries = fetch_data_from_db(query)
    return {"countries": [{"code": row[0], "name": row[1]} for row in countries]}

@app.get("/indicators")
def get_indicators():
    """Get list of available indicators along with descriptions."""
    query = "SELECT DISTINCT indicator, indicator_description FROM indicators_data"
    indicators = fetch_data_from_db(query)
    return {"indicators": [{"code": row[0], "description": row[1]} for row in indicators]}

@app.get("/data/{country_code}")
def get_country_data(country_code: str, indicator: Optional[str] = None, year: Optional[int] = None):
    """Fetch data for a specific country, optionally filtered by indicator and year."""
    
    # Validate country code
    country_check_query = "SELECT 1 FROM countries WHERE country_code = ?"
    country_exists = fetch_data_from_db(country_check_query, (country_code,))
    
    if not country_exists:
        raise HTTPException(status_code=404, detail=f"Country code '{country_code}' not found in database")

    # Fetch indicator data for the given country code
    query = "SELECT country, indicator, indicator_description, year, value FROM indicators_data WHERE country = ?"
    params = [country_code]

    if indicator:
        query += " AND indicator = ?"
        params.append(indicator)

    if year:
        query += " AND year = ?"
        params.append(year)

    data = fetch_data_from_db(query, tuple(params))

    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    # Print indicator details for debugging
    for row in data:
        print(f"Country: {row[0]}, Indicator: {row[1]}, Description: {row[2]}, Year: {row[3]}, Value: {row[4]}")

    return {
        "country_code": country_code,
        "data": [
            {
                "indicator": row[1],
                "indicator_description": row[2],  # Now fetched from database
                "year": row[3],
                "value": row[4]
            }
            for row in data
        ]
    }

@app.get("/data/indicator/{indicator}")
def get_indicator_data(indicator: str, year: Optional[int] = None):
    """Fetch data for all countries for a specific indicator, optionally filtered by year."""
    query = "SELECT country, year, value, indicator_description FROM indicators_data WHERE indicator = ?"
    params = [indicator]

    if year:
        query += " AND year = ?"
        params.append(year)

    data = fetch_data_from_db(query, tuple(params))

    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    # Print indicator details for debugging
    for row in data:
        print(f"Country: {row[0]}, Indicator: {indicator}, Description: {row[3]}, Year: {row[1]}, Value: {row[2]}")

    return {
        "indicator": indicator,
        "indicator_description": data[0][3] if data else "Description not available",  # Now fetched from database
        "data": [
            {
                "country": row[0],
                "year": row[1],
                "value": row[2]
            }
            for row in data
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
# **World Bank Data Web Scraping**

## **Overview**
This project involves web scraping, data storage, and API development using FastAPI to extract country data from the World Bank.

## **Instructions**
- Scrape data from World Bank Countries to obtain the list of countries and relevant data.
- Store the data in an SQLite database (worldbankorg.db).
- Develop a FastAPI-based API that can return country-specific data.

## **Installation & Setup**
### **Prerequisites**
- Ensure you have Python installed (Python 3.8+ recommended). Install the required dependencies:
```bash
python3 -m pip install fastapi uvicorn sqlite3 requests beautifulsoup4 selenium webdriver-manager aiosqlite
```
## **Running the ETL Pipeline**
- To extract and store data, run:
```bash
python3 data_co_extract.py
```
Once the data is stored, run the following SQL command to update country codes in the indicators_data table:
```bash
UPDATE indicators_data
SET country = (
    SELECT country_code
    FROM countries
    WHERE substr(country, 1, 2) = substr(country_code, 1, 2) 
)
WHERE EXISTS (
    SELECT 1 FROM countries WHERE substr(country, 1, 2) = substr(country_code, 1, 2)
);
```
## **Running the FastAPI Application**
```bash
python3 API.py
```
The API will be available at: http://127.0.0.1:8000

## **API Endpoints**  
```bash
GET /countries → Returns a list of countries

GET /indicators → Returns a list of indicators

GET /data/{country_code} → Fetches country-specific data

GET /data/indicator/{indicator} → Fetches data for a specific indicator
```
## **Review Criteria**  
- **Method used for web scraping**: Efficient extraction of country data.

- **Data storage & ETL process:** Clean transformation and storage in SQLite.

- **API Performance:** FastAPI implementation and query efficiency.

- **Code Readability & Documentation:** Well-structured code and clear explanations.

import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_sp500():
    try:
        # URL of the Wikipedia page
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Fetch the page
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info("Fetched page successfully")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all wikitable sortable tables
        tables = soup.find_all('table', class_='wikitable sortable')
        if not tables:
            logger.error("No wikitable sortable tables found")
            return
        
        # Select the correct table (first one with "Symbol" header)
        target_table = None
        for i, table in enumerate(tables):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            logger.info(f"Table {i+1} headers: {headers}")
            if "Symbol" in headers:
                target_table = table
                logger.info(f"Selected table {i+1} with Symbol header")
                break
        
        if not target_table:
            logger.error("No table found with 'Symbol' header")
            return
        
        # Extract data
        data = []
        # Get headers
        headers = [th.get_text(strip=True) for th in target_table.find_all('th')]
        data.append(headers)
        logger.info(f"Headers: {headers}")
        
        # Get rows
        for row in target_table.find_all('tr')[1:]:  # Skip header row
            cells = [td.get_text(strip=True) for td in row.find_all('td')]
            if cells:  # Skip empty rows
                # Optionally limit to 4 columns if desired
                # cells = cells[:4]  # Uncomment to get only Symbol, Security, Sector, Sub-Industry
                data.append(cells)
        
        if not data[1:]:  # Check if there are data rows beyond headers
            logger.error("No data rows extracted")
            return
        
        logger.info(f"Extracted {len(data)} rows, {len(data[0])} columns")
        
        # Connect to Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('your-service-account-key.json', scope)
        client = gspread.authorize(creds)
        
        # Open the Google Sheet
        sheet = client.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        
        # Clear existing data
        sheet.clear()
        
        # Write new data
        sheet.update('A1', data)
        logger.info(f"Updated Google Sheet at {datetime.datetime.now()}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    scrape_sp500()

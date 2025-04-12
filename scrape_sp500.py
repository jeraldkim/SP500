import requests
from bs4 import BeautifulSoup
import json
from github import Github
import os
from dotenv import load_dotenv
import yfinance as yf
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("PAT")
REPO_NAME = "jeraldkim/SP500"  # Replace with your repo
FILE_PATH = "sp500_companies.json"

if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found. Please set GITHUB_TOKEN in .env file.")

# Web scraping
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', {'id': 'constituents'})

# Initialize list to store company data
companies = []

# Get table headers
headers = [th.text.strip() for th in table.find('tr').find_all('th')]

# Iterate through table rows (skip header row)
for row in table.find_all('tr')[1:]:
    cells = row.find_all('td')
    if cells:
        company_data = {}
        for i, cell in enumerate(cells):
            if headers[i] == 'Symbol' and cell.find('a'):
                company_data[headers[i]] = cell.find('a').text.strip()
            else:
                company_data[headers[i]] = cell.text.strip()
        companies.append(company_data)

# Fetch price data using yfinance
today = datetime.now().date()
yesterday = today - timedelta(days=1)

for company in companies:
    symbol = company['Symbol']
    try:
        # Fetch last two days' data to calculate daily change
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            close_today = hist['Close'][-1]
            close_yesterday = hist['Close'][-2]
            daily_change = ((close_today - close_yesterday) / close_yesterday) * 100
            company['ClosePrice'] = round(close_today, 2)
            company['DailyChangePercent'] = round(daily_change, 2)
            company['Date'] = today.strftime("%Y-%m-%d")
        else:
            company['ClosePrice'] = None
            company['DailyChangePercent'] = None
            company['Date'] = today.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        company['ClosePrice'] = None
        company['DailyChangePercent'] = None
        company['Date'] = today.strftime("%Y-%m-%d")

# Save to local JSON file temporarily
with open('sp500_companies.json', 'w', encoding='utf-8') as f:
    json.dump(companies, f, indent=4)

# Push to GitHub
try:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    with open('sp500_companies.json', 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        file = repo.get_contents(FILE_PATH)
        repo.update_file(
            path=FILE_PATH,
            message=f"Update sp500_companies.json with price data for {today}",
            content=content,
            sha=file.sha
        )
        print(f"Updated {FILE_PATH} in {REPO_NAME}")
    except:
        repo.create_file(
            path=FILE_PATH,
            message=f"Add sp500_companies.json with price data for {today}",
            content=content
        )
        print(f"Created {FILE_PATH} in {REPO_NAME}")
    os.remove('sp500_companies.json')
except Exception as e:
    print(f"Error pushing to GitHub: {e}")

print("Script completed")

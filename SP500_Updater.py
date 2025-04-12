import requests
from bs4 import BeautifulSoup
import json
from github import Github
import os

# GitHub configuration
GITHUB_TOKEN = "your-personal-access-token"  # Replace with your PAT
REPO_NAME = "your-username/your-repo"       # Replace with your repo (e.g., "johnDoe/my-data")
FILE_PATH = "sp500_companies.json"          # File path in the repo

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

# Save to local JSON file temporarily
with open('sp500_companies.json', 'w', encoding='utf-8') as f:
    json.dump(companies, f, indent=4)

# Push to GitHub
try:
    # Initialize GitHub client
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # Read the JSON file content
    with open('sp500_companies.json', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file exists in repo
    try:
        file = repo.get_contents(FILE_PATH)
        # Update existing file
        repo.update_file(
            path=FILE_PATH,
            message="Update sp500_companies.json with latest data",
            content=content,
            sha=file.sha
        )
        print(f"Updated {FILE_PATH} in {REPO_NAME}")
    except:
        # Create new file
        repo.create_file(
            path=FILE_PATH,
            message="Add sp500_companies.json with S&P 500 data",
            content=content
        )
        print(f"Created {FILE_PATH} in {REPO_NAME}")

    # Clean up local file
    os.remove('sp500_companies.json')

except Exception as e:
    print(f"Error pushing to GitHub: {e}")

print("Script completed")

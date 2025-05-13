import requests
import pandas as pd
import re
import webbrowser
from bs4 import BeautifulSoup

# Get the BGG collection data for a given username
username = input("Enter BGG username: ")
base_url = f"https://boardgamegeek.com/collection/user/{username}?objecttype=thing&ff=1&subtype=boardgame"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table containing the collection data
table = soup.find('table', class_='collection_table')

# Find all rows in the table
rows = table.find_all('tr')

# Initialize an empty list to store the headers
headers = []

# Find the header row and extract the headers
header_row = rows[0]
header_cells = header_row.find_all('th')
for cell in header_cells[0:7]:
    headers.append(cell.get_text(strip=True))

# Initialize an empty list to store the data
data = []

# Iterate through the rows and extract the data
for row in rows[1:]:  # Skip the header row
    cells = row.find_all('td')
    row_data = []
    for cell in cells:
        row_data.append(cell.get_text(strip=True))
    data.append(row_data)

# Pandas DataFrame to store the data
df = pd.DataFrame(data, columns=headers)

# Drop unwanted/blank columns
df = df.drop(columns=['Version', 'UserRating', 'UserPlays'])

# Replace N/A strings with 0 in Geek rating column
df = df.replace('N/A', 0)

# Round Geek Rating to 2 decimal places
df['Geek Rating'] = df['Geek Rating'].astype(float).round(2)

# Remove comment dates from the 'Comment' column
df['Comment'] = df['Comment'].str[:-10]

# Correct spacing issues in the 'Comment' column
def split_by_caps(text):
    return re.findall('[A-Z][^A-Z]*', text)

df['Comment'] = df['Comment'].apply(split_by_caps).astype("string")
df['Comment'] = df['Comment'].str.strip('[]')
df['Comment'] = df['Comment'].str.replace("'", '')

# Remove parentheses and text within from the 'Title' column
def remove_parentheses(text):
    return re.sub(r'\(.*?\)', '', str(text))

df['Title'] = df['Title'].apply(remove_parentheses)
df['Title'] = df['Title'].str.rstrip()

# Print the DataFrame to see the data
# print(df.to_string())

# Choice of HTML or export to CSV
while True:
    delivery = input("Select 'H' for html or 'C' for csv file\n")
    upper_input = delivery.upper()

# Write and display HTML file
    if upper_input == "H" :
        BGG_collection = df.to_html(index=False)
        with open(f'BGG_{username}.html', 'w') as f:
            f.write(BGG_collection)
            webbrowser.open(f'BGG_{username}.html')
            break
    elif upper_input == "C":
        df.to_csv(f'BGG_{username}.csv', encoding='windows-1252', index=False)
        break
    else:
        print("Please select a valid method")

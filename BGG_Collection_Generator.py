import requests
import pandas as pd
import numpy as np
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

# Remove unicode space from Status column
df['Status'] = df['Status'].str.replace('\xa0', ' ')

# Print the DataFrame to see the data
# print(df.to_string())
html_table = df.to_html(index=False)

# Style the HTML table
def highlight_colors(str):
    if str == 'Owned':
        return 'color: green; font-weight: bold;'
    elif str == 'For Trade':
        return 'color: purple; font-weight: bold;'
    elif str == 'Want To Buy':
        return 'color: blue; font-weight: bold;'
    else:
        return ''
    
styled_html = df.style\
    .set_table_attributes('style="width: 100%; background-color: black; color: #D3D3D3; border-collapse: collapse; border: 1px solid #D3D3D3"')\
    .set_table_styles([{'selector': 'th', 'props': [('background-color', '#000000'), ('color', '#D3D3D3'), ('font-weight', 'bold'), ('text-align', 'center'), ('border', '1px solid #D3D3D3')]}])\
    .set_properties(**{'text-align': 'left','border': '1px solid #D3D3D3', 'padding': '5px'})\
    .set_properties(subset=['Geek Rating', 'Status'], **{'text-align': 'center'})\
    .format({'Geek Rating': '{:.2f}'})\
    .map(highlight_colors, subset=['Status'])\
    .hide(axis='index')\
    .to_html()

# Choice of HTML or export to CSV
while True:
    delivery = input("Select 'H' for html or 'C' for csv file\n")
    upper_input = delivery.upper()

# Write and display HTML file
    if upper_input == "H" :
        with open(f'BGG_{username}.html', 'w') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>{username}'s BGG Collection</title>
</head>
<body spand style="background-color: black;">
<h1 style="color: #D3D3D3; text-align: center;">{username}'s BGG Collection</h1>
    {styled_html}
</body>
</html>
""")
            webbrowser.open_new_tab(f'BGG_{username}.html')
            break
    elif upper_input == "C":
        df.to_csv(f'BGG_{username}.csv', encoding='windows-1252', index=False)
        break
    else:
        print("Please select a valid method")

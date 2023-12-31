import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import csv
import os.path

#trial 3

url = "https://services.utdallas.edu/transit/garages/_code.php"  
def scrape_website_and_save(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='parking')

        for i, table in enumerate(tables, start=1):
            current_date = datetime.now() - timedelta(hours=5)

            # Convert the integer to a string representation of the day of the week
            day_name = current_date.strftime('%A')
            if (i == 2):
                i = 3
            elif (i == 3):
                i = 4

            filename = f"{day_name}_Garage_{i}.csv"
            header_written = os.path.isfile(filename)
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['Date', 'Hour', 'Minute', 'Permit Type', 'Spaces Left'])
                if not header_written:
                    writer.writeheader()

                rows = table.find_all('tr')
                
                for row in rows:
                    columns = row.find_all('td', attrs={'class': ["rightalign", "parking_gold","parking_orange","parking_purple","parking_pay_by_space"]})
                    date = datetime.now() - timedelta(hours=5)
                    hour = date.hour
                    minute = date.minute
                    permit_type = ''
                    spaces_left = ''
                    for column in columns:
                        class_name = column.get('class')
                        if (class_name == ['rightalign']):
                            spaces_left = column.get_text()
                            writer.writerow({'Date': date.date(), 'Hour': hour, 'Minute': minute, 'Permit Type': permit_type, 'Spaces Left': spaces_left})
                        else:
                            permit_type = column.get_text()
                        

        
    else:
        print("Error: Unable to retrieve data from the website.")


scrape_website_and_save(url)

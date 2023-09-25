import requests
from bs4 import BeautifulSoup
import time
import datetime
import csv
import os.path


url = "https://services.utdallas.edu/transit/garages/_code.php"  
def scrape_website_and_save(url):
    response = requests.get(url)
    while True:
        now = time.localtime()  # Get the current time
        if (now.tm_hour >= 7 and now.tm_hour < 18):
            scraping_interval = 30  # Every 30 seconds
        else:
            scraping_interval = 3600  # Every hour
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table', class_='parking')

            for i, table in enumerate(tables, start=1):
                filename = f"table_{i}.csv"
                header_written = os.path.isfile(filename)
                with open(filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['Date', 'Hour', 'Minute', 'Permit Type', 'Spaces Left'])
                    if not header_written:
                        writer.writeheader()

                    rows = table.find_all('tr')
                    
                    for row in rows:
                        columns = row.find_all('td', attrs={'class': ["rightalign", "parking_gold","parking_orange","parking_purple","parking_pay_by_space"]})
                        date = datetime.datetime.now()
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
                            

            print("Data saved successfully.")
            time.sleep(scraping_interval) 
        else:
            print("Error: Unable to retrieve data from the website.")

# Call the function to start scraping and saving data
scrape_website_and_save(url)

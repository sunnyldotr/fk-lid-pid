from flask import Flask, request, render_template, send_file
import csv
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Render the HTML form
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the search term from the form
    search_term = request.form.get('search_term', 'shoes for men')
    search = search_term.replace(" ", "+")

    # Configure Selenium
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    # List of URLs to scrape
    urls = [
        f"https://www.flipkart.com/search?q={search}&sort=recency_desc&page={i}" for i in range(1, 30)
    ]

    raw_data = []
    csv_filename = f"flipkart_product_links_{search_term.replace(' ', '_')}.csv"

    try:
        for page_number, url in enumerate(urls, start=1):
            driver.get(url)
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cPHDOP")))

            link_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'cPHDOP')]//a")
            for element in link_elements:
                link = element.get_attribute("href")
                if link and not link.endswith("&marketplace=FLIPKART"):
                    parsed_url = urlparse.urlparse(link)
                    query_params = urlparse.parse_qs(parsed_url.query)
                    pid = query_params.get('pid', [''])[0]
                    lid = query_params.get('lid', [''])[0]
                    raw_data.append({
                        "search_term": search_term,
                        "page_number": page_number,
                        "link": link,
                        "pid": pid,
                        "lid": lid
                    })

        # Filter data to remove duplicates and pick only records where pid is present
        unique_data = {d["link"]: d for d in raw_data if d["pid"]}.values()

        # Save unique data to a CSV file
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["search_term", "page_number", "link", "pid", "lid"])
            writer.writeheader()
            writer.writerows(unique_data)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

    finally:
        driver.quit()

    # Provide the file for download
    return send_file(csv_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

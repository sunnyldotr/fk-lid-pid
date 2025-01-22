from flask import Flask, request, jsonify
import csv
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get search term from the POST request
    search_term = request.json.get('search_term', 'shoes for men')
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

        # Return JSON response
        return jsonify(list(unique_data))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

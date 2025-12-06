from selenium import webdriver
import time
from selenium.webdriver.common.by import By


def get_news():
    headlines = []
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # Ensure that the path to chromedriver is correctly set up
        # If chromedriver is not in your PATH, you might need to specify it:
        # driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)

        url = 'https://www.google.com/finance'
        driver.get(url)
        time.sleep(3)

        anchor_elements = driver.find_elements(By.CSS_SELECTOR, "div.z4rs2b > a")
        for a in anchor_elements[:10]:
            text = a.text.strip()
            link = a.get_attribute("href")
            if text and link:
                headlines.append((text, link))
        driver.quit()
        return headlines
    except Exception as e:
        print(f"Error fetching financial news: {e}")
        headlines = []
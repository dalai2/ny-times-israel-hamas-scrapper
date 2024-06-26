import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_driver():
    """Initialize the Selenium WebDriver with headless options."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Initialize the WebDriver
driver = init_driver()

# Open the NY Times page for Israel-Hamas conflict
url = 'https://www.nytimes.com/news-event/israel-hamas-gaza'
logging.info(f"Opening URL: {url}")
driver.get(url)

# Function to load all articles by scrolling
def load_all_articles():
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        logging.info("Scrolling down the page")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new articles to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            logging.info("Reached the end of the page")
            break
        last_height = new_height

# Load all articles
load_all_articles()

# Parse the loaded content
logging.info("Parsing page content")
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all article links
logging.info("Finding article links")
articles = []
for article in soup.find_all('a', href=True):
    link = article['href']
    if '/2024/' in link and link.startswith('/'):
        articles.append('https://www.nytimes.com' + link)

# Function to scrape a single news article
def scrape_article(url):
    logging.info(f"Scraping article: {url}")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    headline = soup.find('h1').text if soup.find('h1') else ''
    paragraphs = soup.find_all('p')
    article_text = ' '.join([para.text for para in paragraphs])
    return {'headline': headline, 'text': article_text}

# Scrape each article
scraped_articles = []
for link in articles:
    try:
        article_data = scrape_article(link)
        scraped_articles.append(article_data)
    except Exception as e:
        logging.error(f"Failed to scrape {link}: {e}")

# Save the articles to a DataFrame
df = pd.DataFrame(scraped_articles)
csv_file = 'nytimes_israel_hamas_articles_may.csv'
logging.info(f"Saving articles to {csv_file}")
df.to_csv(csv_file, index=False)
print(df.head())

# Close the WebDriver
driver.quit()

# 🎬 IMDb Top 250 Movie Scraper (with Visualization and Error Handling)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

url = "https://www.imdb.com/chart/top/"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-gpu")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/119.0.6045.105 Safari/537.36")

print("🌐 Fetching IMDb Top 250 movies... Please wait")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)
WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item'))
)

movies = driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')
print(f"✅ Found {len(movies)} movie entries")

data = []

for idx, movie in enumerate(movies, start=1):
    try:
        title_block = movie.find_element(By.CSS_SELECTOR, 'h3.ipc-title__text').text.strip()
        if '.' in title_block:
            rank, title = title_block.split('.', 1)
            rank, title = rank.strip(), title.strip()
        else:
            rank, title = str(idx), title_block
    except:
        rank, title = str(idx), "N/A"
    try:
        year = movie.find_element(By.CSS_SELECTOR, 'span.cli-title-metadata-item:nth-of-type(1)').text
    except:
        year = "N/A"
    try:
        rating = movie.find_element(By.CSS_SELECTOR, 'span.ipc-rating-star--rating').text
    except:
        rating = "N/A"
    if not rank.isdigit():
        continue  
    try:
        rating_value = float(rating)
    except:
        rating_value = None

    data.append({
        "Rank": int(rank),
        "Title": title,
        "Year": year,
        "Rating": rating_value
    })

driver.quit()
print("🟢 Data extraction completed!")

df = pd.DataFrame(data)
df.to_csv("imdb_top_250_final.csv", index=False, encoding="utf-8")
print(f"📁 Saved {len(df)} movies to imdb_top_250_final.csv")

print("📊 Generating visualizations...")

plt.figure(figsize=(10, 5))
sns.histplot(df['Rating'], bins=20, kde=True)
plt.title("Distribution of IMDb Ratings")
plt.xlabel("Rating")
plt.ylabel("Number of Movies")
plt.tight_layout()
plt.show()

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
top10 = df.nlargest(10, 'Rating')

plt.figure(figsize=(10, 6))
sns.barplot(data=top10, x='Rating', y='Title', palette='viridis')
plt.title("🎖 Top 10 IMDb Movies by Rating")
plt.xlabel("Rating")
plt.ylabel("Movie Title")
plt.tight_layout()
plt.show()

df['Decade'] = (df['Year'] // 10) * 10
decade_avg = df.groupby('Decade')['Rating'].mean().reset_index()

plt.figure(figsize=(10, 5))
sns.lineplot(data=decade_avg, x='Decade', y='Rating', marker='o')
plt.title("⭐ Average IMDb Rating by Decade")
plt.xlabel("Decade")
plt.ylabel("Average Rating")
plt.tight_layout()
plt.show()

print("✅ Visualization complete!")




import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# ----------------------------------
# Load NSE Codes
# ----------------------------------
data_df = pd.read_csv('NSE Symbols.CSV')
name_company1 = [
    {"company": data_df["Company Name"][i], "code": data_df["Scrip"][i]}
    for i in range(len(data_df))
]

# ----------------------------------
# Load FinBERT Once
# ----------------------------------
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}


def finbert_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)[0]

    sentiment = label_map[int(torch.argmax(probs))]
    score = float(torch.max(probs))
    return sentiment, score


# ----------------------------------
# Fetch News + Apply FinBERT
# ----------------------------------
def get_company_news(company):
    headlines = []
    driver = None
    sentiment_summary = {"Positive": 0, "Neutral": 0, "Negative": 0}

    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        first_word = company.strip().lower().split()[0]

        # Find Scrip Code
        scrip_code = None
        for entry in name_company1:
            if entry["company"].strip().lower().split()[0] == first_word:
                scrip_code = entry["code"]
                break

        if not scrip_code:
            raise ValueError(f"No scrip code found for {company}")

        url = f"https://www.google.com/finance/quote/{scrip_code}:NSE"
        driver.get(url)
        time.sleep(3)

        anchors = driver.find_elements(By.CSS_SELECTOR, "div.z4rs2b > a")

        # Extract first 10 headlines
        for a in anchors[:10]:
            text = a.text.strip()
            link = a.get_attribute("href")

            if text:
                sentiment, score = finbert_sentiment(text)
                sentiment_summary[sentiment] += 1

                headlines.append({
                    "headline": text,
                    "link": link,
                    "sentiment": sentiment,
                    "confidence": score
                })

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()

    # Compute final market sentiment
    if sentiment_summary["Positive"] > sentiment_summary["Negative"]:
        overall = "POSITIVE MARKET SENTIMENT"
    elif sentiment_summary["Negative"] > sentiment_summary["Positive"]:
        overall = "NEGATIVE MARKET SENTIMENT"
    else:
        overall = "NEUTRAL MARKET SENTIMENT"

    return {
        "company": company,
        "overall_sentiment": overall,
        "summary": sentiment_summary,
        "headlines": headlines
    }


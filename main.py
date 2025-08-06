# Importing Necessary Packeages
import os
import requests
import google.generativeai as genai
from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

# Function to get news data from newsdata.io API
def getNewsData(news_api_key, city_name="Delhi"):
    baseUrl = "https://newsdata.io/api/1/news"
    search_query = f"(flu OR dengue OR virus OR outbreak OR hospital OR fever) AND {city_name} India"

    queryData = {
        "q": search_query,
        "country": "in",
        "category": "health",
        "language": "en"
    }

    headers = {
        "X-ACCESS-KEY": news_api_key
    }

    result = requests.get(baseUrl, headers=headers, params=queryData)
    if result.status_code != 200:
        raise Exception(f"Error : {result.status_code} - {result.text}")

    return result.json()


# Function to Extract Relevant Information from the API Result
def extract(news_data):
    articles = []
    for i, article in enumerate(news_data["results"]):
        title = article.get('title', 'No Title')
        description = article.get('description', 'No description available.')
        url = article.get('link', '#')
        source = article.get('source_name', 'Unknown Source')
        published_at = article.get('pubDate', 'Unknown Date')

        articles.append(
            f"Article {i+1} (Source: {source}, Published: {published_at}):\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"URL: {url}\n"
        )
    return articles




# Function to Create a news letter type email response using LLM
def generateNewsletter(gemini_api_key, news_data, city_name="Delhi"):
    # Setting up LLM
    # Instantiating Gemini
    genai.configure(api_key=gemini_api_key)
    LLM = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
        You are an AI-powered Local Health Monitor for the city of {city_name}.
        Your primary task is to review the provided news articles and identify any **notable, urgent, or emerging public health issues or warnings** specific to {city_name} or India that would be important for a local resident to know.

        **Examples of notable health issues you should report:**
        - Disease outbreaks (e.g., flu, dengue, cholera, measles, COVID-19 spikes).
        - Significant changes in air quality, pollution warnings, or environmental health hazards.
        - Public health advisories, warnings, or new guidelines from official health organizations.
        - Localized health emergencies, significant hospital news directly impacting residents' health (e.g., hospital capacity alerts).
        - Warnings about contaminated food or water.
        - Information about new local health initiatives, vaccination drives, or free health camps that are critical for public awareness.
        - Alerts about specific health risks (e.g., heatstroke warnings, monsoon-related diseases).

        **Examples of what is NOT a notable health issue for this report (do NOT include these):**
        - General national political news.
        - Broad economic news.
        - General medical research findings that are not localized or urgent for immediate public action.
        - Sports or entertainment news, or general lifestyle advice.
        - News about hospital administration or internal policy changes that don't directly impact patient care or public health.

        **Input News Articles for Analysis:**
        Each article snippet has a Title, Description, Source, Publication Date, and URL. You **do NOT have access to the full article content**, so make your assessment based solely on the provided Title and Description.

        **Your Task:**
        1.  Carefully read through each provided article snippet.
        2.  Identify if any article describes a **notable, urgent, or emerging public health issue** relevant to {city_name} or its residents, according to the criteria above.
        3.  **If you find ONE or more notable health issues:**
            * Generate a concise, informative summary in **beautiful Markdown format**, suitable for direct inclusion in an email body.
            * The summary should be friendly, easy to read, and actionable.
            * **Start with a friendly greeting:** "Hello there!" or "Good morning/afternoon/evening!"
            * **Suggest an email subject line** on the first line, formatted as: `Subject: [Your Suggested Subject Line]`
            * Use a clear, bold heading: `## Local Health Update for {city_name}`.
            * For each notable issue, provide a brief, **one-sentence summary** of the issue, followed by a direct link to the article.
            * Use Markdown bullet points (`* `) for each issue.
            * Add a horizontal rule (`---`) for visual separation before the closing.
            * Conclude with a friendly closing: "Stay informed and well! Your Local Health Monitor."
        4.  **If you find NO notable health issues after reviewing ALL articles:**
            * Respond with the exact phrase: "No notable health issues detected today for {city_name}."
            * Do NOT generate any other text or Markdown if there are no issues.

        **Example of desired output (if issues are found):**
        ```markdown
        Subject: Urgent: Local Health Update for {city_name}

        Hello there!

        Here's a quick summary of today's important health news in {city_name}:

        * **[Brief, one-sentence summary of Issue 1].** Read more: [Link to Article 1]
        * **[Brief, one-sentence summary of Issue 2].** Read more: [Link to Article 2]
        * **[Brief, one-sentence summary of Issue 3].** Read more: [Link to Article 3]

        ---
        Stay informed and well! Your Local Health Monitor.
        ```

        **Example of desired output (if NO issues are found):**
        `No notable health issues detected today for {city_name}.`

        ---
        **News Data for Analysis:**
        {news_data}
    """
    response = LLM.generate_content(prompt)
    return response.text

# Main Pipeline
def main(gemini_api_key, news_api_key, city_name="Delhi"):
    # Getting news data from newsdata.io API
    news_data = getNewsData(news_api_key, city_name)

    # Extracting relveant information from the API Result
    extracted_news_data = extract(news_data)

    # Generate LLM Based Summary
    result = generateNewsletter(gemini_api_key, extracted_news_data, city_name)

    # LLM Result
    return result

# API Endpoint to check server
@app.get("/")
def health():
    return {
        "message": "CommuniCare"
    }

# API Endpoint to return result
@app.get("/generate-newsletter")
def generateNewsLetter():
    gemini_key = os.getenv("GEMINI_API_KEY")
    news_key = os.getenv("NEWS_API_KEY")

    if not gemini_key or not news_key:
        return {"error": "Missing API keys. Check your .env file or environment variables."}
    
    result = main(gemini_key, news_key)
    return {
        "newsletter": result
    }
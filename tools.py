import wikipedia
from datetime import datetime
import re
import json
import requests
from bs4 import BeautifulSoup
import hashlib


def wikipedia_tool(query: str) -> str:
    """Search Wikipedia for a summary on the given query."""
    try:
        return wikipedia.summary(query)
    except wikipedia.DisambiguationError as e:
        return f"Multiple results found: {', '.join(e.options[:5])}..."
    except wikipedia.PageError:
        return "No Wikipedia page found for that topic."
    except Exception as e:
        return f"Wikipedia lookup failed: {str(e)}"

def duckduckgo_tool(query: str) -> str: 
    """Perform a quick search using DuckDuckGo's lite API."""
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
        )
        data = response.json()
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            first_related = data["RelatedTopics"][0]
            if isinstance(first_related, dict) and first_related.get("Text"):
                return first_related["Text"]
        return "No quick answer found."
    except Exception as e:
        return f"DuckDuckGo search failed: {str(e)}"

def llm_weather_tool(query: str = "") -> dict:
    try:
        # Step 1: Get lat/lon from query
        if query.strip():
            geo_url = "https://nominatim.openstreetmap.org/search"
            geo_params = {"q": query, "format": "json", "limit": 1}
            geo_res = requests.get(geo_url, params=geo_params, headers={"User-Agent": "llm-weather-tool"})
            geo_res.raise_for_status()
            geo_data = geo_res.json()
            lat = float(geo_data[0]['lat'])
            lon = float(geo_data[0]['lon'])
            city_name = geo_data[0]['display_name']
        else:
            ip_res = requests.get("http://ip-api.com/json/")
            ip_res.raise_for_status()
            ip_data = ip_res.json()
            lat = float(ip_data['lat'])
            lon = float(ip_data['lon'])
            city_name = f"{ip_data['city']}, {ip_data['regionName']}, {ip_data['country']}"
    except Exception as e:
        try:
            ip_res = requests.get("http://ip-api.com/json/")
            ip_res.raise_for_status()
            ip_data = ip_res.json()
            lat = float(ip_data['lat'])
            lon = float(ip_data['lon'])
            city_name = f"{ip_data['city']}, {ip_data['regionName']}, {ip_data['country']}"
        except Exception as e:
            return f"error: Could not retrieve City Information. {str(e)}"
    try:
        # Step 2: Get NWS forecast URL
        headers = {"User-Agent": "llm-weather-tool (synologyLLM@email.com)"}
        point_url = f"https://api.weather.gov/points/{lat},{lon}"
        point_res = requests.get(point_url, headers=headers)
        point_res.raise_for_status()
        point_data = point_res.json()
        forecast_url = point_data["properties"]["forecast"]

        # Step 3: Get forecast
        forecast_res = requests.get(forecast_url, headers=headers)
        forecast_res.raise_for_status()
        forecast_data = forecast_res.json()
        periods = forecast_data["properties"]["periods"]
        if not periods:
            return {"error": "No forecast data available."}
        current = periods[0]
    except Exception as e:
        return {"error": "Could not Retrieve forcast data"}

    result = {
        "location": city_name,
        current["name"]: {
            "forecast": current["detailedForecast"],
            "precipitation": f"{current['probabilityOfPrecipitation']['value']}%",
            "start_time": current["startTime"],
        }
    }
    #Add the next 2 weather periods for future forcast
    for period in periods[1:3]: 
        result[period["name"]] = {
            "forecast": period["detailedForecast"],
            "precipitation": f"{period['probabilityOfPrecipitation']['value']}%",
            "start_time": period["startTime"],
        }
    return result

def current_time_tool(query: str = None) -> str:
    try:
        if location:
            tz_list_url = "http://worldtimeapi.org/api/timezone"
            resp = requests.get(tz_list_url)
            resp.raise_for_status()
            timezones = resp.json()
            
            # Find timezone containing the location string
            matched_tz = next((tz for tz in timezones if location.replace(" ", "_").lower() in tz.lower()), None)
            if matched_tz:
                time_url = f"http://worldtimeapi.org/api/timezone/{matched_tz}"
                time_resp = requests.get(time_url)
                time_resp.raise_for_status()
                time_data = time_resp.json()
                datetime_str = time_data.get("datetime", None)
                if datetime_str:
                    # Example datetime_str: '2025-08-08T17:50:52.123456+01:00'
                    dt = datetime.fromisoformat(datetime_str)
                    return dt.strftime("%Y-%m-%d %H:%M:%S") + f" ({matched_tz})"
            else:
                return f"Could not find timezone info for '{location}'."
        
        # fallback: local PC time
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    
    except Exception as e:
        return f"Time lookup failed: {str(e)}"

fetched_articles_by_user = {}
def npr_news_tool(query: str = None, num_articles: int = 5, user_id: str = None) -> dict:
    global fetched_articles_by_user
    if not user_id:
        user_id = "llm"
    fetched_articles = fetched_articles_by_user.setdefault(user_id, set())
    counter = 0

    base_url = 'https://www.npr.org/sections/news/'
    try:
        url_data = requests.get(base_url).text
    except Exception as e:
        return {"error": f"Website Error: {str(e)}"}
    soup = BeautifulSoup(url_data, "html.parser")
    article_links = soup.find_all('h2', class_="title")[:num_articles]

    for link in article_links:
        article_link = link.a['href'].strip()
        article_url = f"{article_link}"
        try:
            article_data = requests.get(article_url).text
        except:
            print(f'Article Retrieval Error, trying again later')
            continue  # Skip to the next article URL if there's an error
        article_soup = BeautifulSoup(article_data, "html.parser")
        title = article_soup.find('article', attrs={'class': "story"}).find_all('p')
        paragraphs = article_soup.find('article', attrs={'class': "story"}).find_all('p')
        joined_paragraphs = '\n'.join([p.text.strip() for p in paragraphs])
        news_text = f'{joined_paragraphs}'
        if len(news_text) < 1000:
            continue
        # Generate a unique identifier for the news article
        article_id = hashlib.sha256(article_url.encode()).hexdigest()
        # Check if the article has already been fetched
        if article_id not in fetched_articles:
            fetched_articles.add(article_id)
            return {
                "title": link.get_text(strip=True),
                "text": news_text
            }
        else:
            counter += 1
            if counter >= num_articles:
                return {"message": "No new articles found"}
            else:
                continue


wiki_tool = {
    "type": "function",
    "function": {
        "name": "wikipedia_search",
        "description": "Get a Wikipedia summary for a given topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The topic to search on Wikipedia"}
            },
            "required": ["query"],
        },
    },
}

ddg_tool = {
    "type": "function",
    "function": {
        "name": "duckduckgo_search",
        "description": "Get a quick factual answer from the web using DuckDuckGo.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for quick info"}
            },
            "required": ["query"],
        },
    },
}

weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Fetch weather information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "City name or location (optional). Leave empty for IP-based location."}
            },
            "required": [],
        },
    },
}

time_tool = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get current local time, or time of a specified location (city or region).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "City name or location (optional). Leave empty to get local PC time."}
            },
            "required": [],
        },
    },
}

news_tool = {
    "type": "function",
    "function": {
        "name": "get_current_news",
        "description": "Fetches the latest NPR news articles.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Leave empty and get latest news articles"}
            },
            "required": [],
        },
    },
}

ALL_TOOLS = [wiki_tool, ddg_tool, weather_tool, time_tool, news_tool]

def dispatch_tool(tool_name: str, args: dict, user_id=None) -> str:
    if tool_name == "wikipedia_search":
        return wikipedia_tool(**args)
    if tool_name == "duckduckgo_search":
        return duckduckgo_tool(**args)
    if tool_name == "get_current_weather":
        return llm_weather_tool(**args)
    if tool_name == "get_current_time":
        return current_time_tool(**args)
    if tool_name == "get_current_news":
        return npr_news_tool(**args, user_id=user_id)
    return f"Tool '{tool_name}' not found."
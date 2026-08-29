"""
Sentiment Analysis module for Stock Analysis Bot.
Parses financial news and Reddit social sentiment using NLP.
"""

import requests
import urllib.parse
from bs4 import BeautifulSoup
from textblob import TextBlob
from typing import Dict, Any, List
import random
from stock_bot.config import USER_AGENTS

def fetch_rss_news(query: str, max_items: int = 15) -> List[Dict[str, str]]:
    """Fetch news headlines from Google News RSS for a specific query."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    items = []
    
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "xml")
            raw_items = soup.find_all("item")
            for item in raw_items[:max_items]:
                title = item.title.text if item.title else ""
                pub_date = item.pubDate.text if item.pubDate else ""
                link = item.link.text if item.link else ""
                source = item.source.text if item.source else "News"
                if title:
                    items.append({
                        "title": title,
                        "pub_date": pub_date,
                        "link": link,
                        "source": source
                    })
    except Exception:
        pass
        
    return items

def analyze_headline_sentiment(headlines: List[str]) -> Dict[str, Any]:
    """Calculate average polarity and subjectivity across a list of headlines."""
    if not headlines:
        return {"polarity": 0.0, "subjectivity": 0.0, "positive_count": 0, "negative_count": 0, "neutral_count": 0}
        
    polarities = []
    subjectivities = []
    pos_cnt = 0
    neg_cnt = 0
    neu_cnt = 0
    
    for h in headlines:
        blob = TextBlob(h)
        pol = blob.sentiment.polarity
        subj = blob.sentiment.subjectivity
        polarities.append(pol)
        subjectivities.append(subj)
        
        if pol > 0.05:
            pos_cnt += 1
        elif pol < -0.05:
            neg_cnt += 1
        else:
            neu_cnt += 1
            
    avg_pol = sum(polarities) / len(polarities) if polarities else 0.0
    avg_subj = sum(subjectivities) / len(subjectivities) if subjectivities else 0.0
    
    return {
        "polarity": avg_pol,
        "subjectivity": avg_subj,
        "positive_count": pos_cnt,
        "negative_count": neg_cnt,
        "neutral_count": neu_cnt,
        "total": len(headlines)
    }

def analyze_sentiment(symbol: str, company_name: str, ticker_news: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetches news and social media sentiment for US and international stocks.
    Returns composite sentiment metrics and 0-100 sentiment score.
    """
    # 1. Fetch News Headlines
    news_query = f"{company_name} {symbol} stock"
    news_items = fetch_rss_news(news_query, max_items=15)
    
    # Merge with yfinance ticker news if present
    news_headlines = [item["title"] for item in news_items]
    if ticker_news:
        for tn in ticker_news:
            title = None
            if isinstance(tn, dict):
                if "content" in tn and isinstance(tn["content"], dict):
                    title = tn["content"].get("title")
                elif "title" in tn:
                    title = tn.get("title")
            if title and title not in news_headlines:
                news_headlines.append(title)

    news_sentiment = analyze_headline_sentiment(news_headlines)

    # 2. Fetch Reddit / Social Sentiment
    reddit_query = f"{symbol} stock OR {company_name} site:reddit.com"
    reddit_items = fetch_rss_news(reddit_query, max_items=10)
    reddit_headlines = [item["title"] for item in reddit_items]
    reddit_sentiment = analyze_headline_sentiment(reddit_headlines)

    # 3. Overall Combined Sentiment Score (0 to 100)
    # Map Polarity (-1.0 to +1.0) to Score (0 to 100), centered at 50
    combined_pol = (news_sentiment["polarity"] * 0.7) + (reddit_sentiment["polarity"] * 0.3)
    
    sentiment_score = 50.0 + (combined_pol * 40.0)  # Scale -1..1 to 10..90
    sentiment_score = max(0.0, min(100.0, sentiment_score))
    
    if combined_pol >= 0.25:
        label = "VERY BULLISH"
    elif combined_pol >= 0.08:
        label = "BULLISH"
    elif combined_pol <= -0.25:
        label = "VERY BEARISH"
    elif combined_pol <= -0.08:
        label = "BEARISH"
    else:
        label = "NEUTRAL"
        
    # Extract representative positive and negative headlines
    head_with_scores = []
    for h in set(news_headlines + reddit_headlines):
        head_with_scores.append((h, TextBlob(h).sentiment.polarity))
        
    head_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    pos_highlights = [h[0] for h in head_with_scores if h[1] > 0.05][:3]
    neg_highlights = [h[0] for h in head_with_scores if h[1] < -0.05][:3]

    return {
        "combined_polarity": round(combined_pol, 3),
        "sentiment_score": round(sentiment_score, 1),
        "label": label,
        "news_stats": news_sentiment,
        "reddit_stats": reddit_sentiment,
        "headline_count": len(news_headlines) + len(reddit_headlines),
        "positive_highlights": pos_highlights,
        "negative_highlights": neg_highlights,
        "recent_headlines": news_headlines[:5]
    }

# utils.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize once
vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Returns:
        vader_score (float)
        bert_score (float placeholder)
    """

    if not text or text.strip() == "":
        return 0.0, 0.0

    vader_result = vader_analyzer.polarity_scores(text)
    vader_score = vader_result["compound"]

    # No BERT on free tier
    return vader_score, 0.0
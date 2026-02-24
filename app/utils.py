# utils.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize once
vader_analyzer = SentimentIntensityAnalyzer()
def analyze_sentiment(text):
    """
    Returns:
        vader_score (float)
        bert_score (float placeholder)
        final_score (float)
    """

    if not text or text.strip() == "":
        return 0.0, 0.0, 0.0

    vader_result = vader_analyzer.polarity_scores(text)
    vader_score = vader_result["compound"]

    bert_score = 0.0  # placeholder (no BERT on free tier)

    # Since no BERT, final_score = vader_score
    final_score = vader_score

    return vader_score, bert_score


def analyze_sentiments(text):
    """
    Returns:
        vader_score (float)
        bert_score (float placeholder)
        final_score (float weighted score)
    """

    if not text or text.strip() == "":
        return 0.0, 0.0, 0.0

    vader_result = vader_analyzer.polarity_scores(text)
    vader_score = vader_result["compound"]

    bert_score = 0.0  # placeholder

    # Weighted logic (future ready)
    vader_weight = 1.0
    bert_weight = 0.0

    final_score = (vader_score * vader_weight) + (bert_score * bert_weight)

    return vader_score, bert_score, final_score
# utils.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Initialize once (important for performance)
vader_analyzer = SentimentIntensityAnalyzer()

# Load pretrained BERT sentiment model
bert_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    """
    Returns:
        vader_score (float)
        bert_score (float)
    """

    if not text or text.strip() == "":
        return 0.0, 0.0

    # -----------------------------
    # VADER
    # -----------------------------
    vader_result = vader_analyzer.polarity_scores(text)
    vader_score = vader_result["compound"]  # -1 to 1

    # -----------------------------
    # BERT
    # -----------------------------
    bert_result = bert_pipeline(text[:512])[0]  # limit to 512 tokens
    bert_label = bert_result["label"]
    bert_confidence = bert_result["score"]

    # Convert BERT label to numeric scale
    if bert_label == "POSITIVE":
        bert_score = bert_confidence
    else:
        bert_score = -bert_confidence

    return vader_score, bert_score

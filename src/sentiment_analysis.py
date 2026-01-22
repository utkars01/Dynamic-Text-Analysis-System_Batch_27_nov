positive_words = {
    "good", "great", "excellent", "amazing", "awesome", "fantastic",
    "love", "loved", "lovely", "nice", "perfect", "best", "wonderful",
    "satisfied", "happy", "pleased", "delightful", "positive",
    "recommend", "recommended", "worth", "value", "reliable", "smooth",
    "fast", "quick", "comfortable", "beautiful", "impressive",
    "brilliant", "outstanding", "superb", "exceptional", "efficient",
    "friendly", "helpful", "affordable", "durable", "accurate",
    "easy", "simple", "convenient"
}

negative_words = {
    "bad", "worst", "poor", "terrible", "awful", "hate", "hated",
    "boring", "disappointed", "waste", "problem", "negative",
    "slow", "delay", "damaged", "broken", "useless", "cheap",
    "defective", "refund", "return", "complaint", "unhappy",
    "frustrating", "annoying", "pathetic", "failure", "faulty",
    "hard", "difficult", "confusing", "expensive", "overpriced",
    "unreliable", "rude", "late", "missing", "incomplete"
}

def get_sentiment(text):
    text = str(text).lower()

    pos_score = sum(word in text for word in positive_words)
    neg_score = sum(word in text for word in negative_words)

    if pos_score > neg_score:
        return "Positive"
    elif neg_score > pos_score:
        return "Negative"
    else:
        return "Neutral"


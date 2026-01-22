from src.input_handling import load_csv
from src.preprocessing import clean_text
from src.topic_modeling import train_lda
from src.summarization import extractive_summary

df = load_csv("data/raw/amazon_reviews_labeled.csv")
df["clean_text"] = df["review"].apply(clean_text)

lda, topics, coherence = train_lda(df["clean_text"])

print("Topics:")
for t in topics:
    print(t)

print("\nCoherence Score:", coherence)

summary = extractive_summary(df["review"])
print("\nSummary:")
print(summary)

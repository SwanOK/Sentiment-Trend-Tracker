import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    # Get the compound score: -1 (most neg) to 1 (most pos)
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def main():
    print("--- Sentiment Trend Tracker ---")

    # 1. Load the dataset
    try:
        df = pd.read_csv('comments.csv')
    except FileNotFoundError:
        print("Error: comments.csv not found!")
        return

    # 2. Apply sentiment analysis
    print("Analyzing sentiments...")
    df['sentiment'] = df['text'].apply(analyze_sentiment)

    # 3. Calculate ratios
    counts = df['sentiment'].value_counts()
    print("\nResults:\n", counts)

    # 4. Visualization
    plt.figure(figsize=(8, 6))
    sns.set_palette("pastel")
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="viridis", legend=False)
    plt.title('Sentiment Analysis of Comments')
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Comments')

    # Save the plot to the folder
    plt.savefig('sentiment_report.png')
    print("\nSuccess! Report saved as 'sentiment_report.png'")
    plt.show()

if __name__ == "__main__":
    main()
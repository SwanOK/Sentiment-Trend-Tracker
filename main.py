import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    # Get the compound score: -1 (most neg) to 1 (most pos)
    score = analyzer.polarity_scores(str(text))['compound']
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def fetch_live_hn_comments(limit=50):
    """Fetches real-time comments from the top stories on Hacker News using their free API."""
    print("\nFetching live text from Hacker News top stories...")
    
    try:
        # 1. Get the IDs of the current top stories
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(top_stories_url).json()
        
        comments_list = []
        
        # 2. Iterate through stories to grab comment text
        for story_id in story_ids[:10]: # Look into the top 10 stories
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_data = requests.get(story_url).json()
            
            # Check if the story has kids (comments)
            if story_data and "kids" in story_data:
                for comment_id in story_data["kids"]:
                    comment_url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
                    comment_data = requests.get(comment_url).json()
                    
                    # Ensure the comment text exists and isn't deleted
                    if comment_data and "text" in comment_data and not comment_data.get("deleted"):
                        # Basic clean-up of common HTML tags returned by HN API
                        clean_text = comment_data["text"].replace("<p>", " ").replace("</p>", "")
                        comments_list.append(clean_text)
                        
                    if len(comments_list) >= limit:
                        break
            if len(comments_list) >= limit:
                break
                
        if not comments_list:
            print("No recent comments could be pulled.")
            return None
            
        return pd.DataFrame(comments_list, columns=['text'])
        
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None

def main():
    print("--- Sentiment Trend Tracker ---")
    print("1. Analyze local CSV (comments.csv)")
    print("2. Fetch & Analyze live Hacker News comments (No API Key Required)")
    choice = input("Select an option (1 or 2): ").strip()

    df = None

    if choice == '1':
        # Load the dataset locally
        try:
            df = pd.read_csv('comments.csv')
        except FileNotFoundError:
            print("Error: comments.csv not found!")
            return
    elif choice == '2':
        # Fetch live data from the API
        df = fetch_live_hn_comments(limit=50)
        if df is None or df.empty:
            print("No data retrieved. Exiting.")
            return
    else:
        print("Invalid choice. Exiting.")
        return

    # Apply sentiment analysis
    print("\nAnalyzing sentiments...")
    df['sentiment'] = df['text'].apply(analyze_sentiment)

    # Calculate ratios
    counts = df['sentiment'].value_counts()
    print("\nResults:\n", counts)

    # Visualization
    plt.figure(figsize=(8, 6))
    sns.set_palette("pastel")
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="viridis", legend=False)
    
    source_title = "Hacker News Live" if choice == '2' else "Comments"
    plt.title(f'Sentiment Analysis of {source_title}')
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Comments')

    # Save the plot to the folder
    plt.savefig('sentiment_report.png')
    print("\nSuccess! Report saved as 'sentiment_report.png'")

if __name__ == "__main__":
    main()
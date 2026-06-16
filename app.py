import os
import sys
import json
import string
import argparse
import numpy as np
from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- NLTK Setup ---
import nltk
# Set NLTK data paths dynamically for write-access in serverless environments (like Vercel)
nltk_data_path = os.path.join('/tmp', 'nltk_data') if sys.platform != 'win32' else os.path.expanduser('~/nltk_data')
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

for resource in ['punkt', 'stopwords', 'punkt_tab']:
    try:
        if resource == 'punkt':
            nltk.data.find('tokenizers/punkt')
        elif resource == 'punkt_tab':
            nltk.data.find('tokenizers/punkt_tab')
        else:
            nltk.data.find('corpora/stopwords')
    except LookupError:
        # Download resource to writable path quietly
        nltk.download(resource, download_dir=nltk_data_path, quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# --- FAQ Data Loading ---
FAQ_FILE = 'faqs.json'
faqs = []

try:
    if not os.path.exists(FAQ_FILE):
        raise FileNotFoundError(f"Missing FAQ file: '{FAQ_FILE}'")
    with open(FAQ_FILE, 'r', encoding='utf-8') as f:
        faqs = json.load(f)
except Exception as e:
    print(f"Error loading FAQs: {e}", file=sys.stderr)

# --- NLP Preprocessing ---
def preprocess_text(text):
    """
    Preprocess user input or FAQ questions:
    - Lowercase text
    - Remove punctuation
    - Tokenize into words
    - Remove English stop words
    """
    if not text or not isinstance(text, str):
        return ""
    
    # 1. Lowercasing
    text = text.lower()
    
    # 2. Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 3. Tokenization
    tokens = word_tokenize(text)
    
    # 4. Remove stop words
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = set()
    
    filtered_tokens = [w for w in tokens if w not in stop_words]
    
    return " ".join(filtered_tokens)

# --- TF-IDF Vectorizer & Index Creation ---
# Preprocess the FAQ questions and fit the Vectorizer at startup
faq_questions = [faq.get('question', '') for faq in faqs]
preprocessed_questions = [preprocess_text(q) for q in faq_questions]

vectorizer = TfidfVectorizer()
tfidf_matrix = None

if preprocessed_questions and any(q.strip() for q in preprocessed_questions):
    try:
        tfidf_matrix = vectorizer.fit_transform(preprocessed_questions)
    except Exception as e:
        print(f"Error fitting TfidfVectorizer: {e}", file=sys.stderr)

# --- Similarity-based Question Matching ---
def get_response(user_query, threshold=0.3):
    """
    Calculate the similarity between the user query and the FAQ dataset,
    returning the matching answer or a fallback response if below the threshold.
    """
    fallback_message = "Sorry, I couldn't find an appropriate answer for your question."
    
    if not faqs:
        return "Sorry, the FAQ database is empty or could not be loaded."
        
    if tfidf_matrix is None:
        return "Sorry, the search index is not initialized."

    # 1. Preprocess user query
    clean_query = preprocess_text(user_query)
    
    # Check if empty query after preprocessing
    if not clean_query.strip():
        return fallback_message

    try:
        # 2. Transform query into TF-IDF vector
        query_vector = vectorizer.transform([clean_query])
        
        # 3. Compute cosine similarities
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        # 4. Find index of highest similarity
        max_idx = np.argmax(similarities)
        max_score = similarities[max_idx]
        
        # 5. Return answer if matching score is above threshold
        if max_score >= threshold:
            return faqs[max_idx].get('answer', fallback_message)
        else:
            return fallback_message
            
    except Exception as e:
        print(f"Error during matching: {e}", file=sys.stderr)
        return fallback_message

# --- Flask Server Setup ---
app = Flask(__name__)

@app.route('/')
def index():
    """Render the main Chat UI."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Chat API endpoint: processes question and returns matching answer."""
    try:
        # Check if the FAQ file is present; handle error dynamically
        if not faqs:
            return jsonify({'error': 'FAQ data is unavailable. Please verify faqs.json is present.'}), 500

        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid request format. JSON body with a "message" key is required.'}), 400
            
        user_message = data['message']
        
        # Handle empty string input
        if not isinstance(user_message, str) or not user_message.strip():
            return jsonify({'response': "Sorry, I couldn't find an appropriate answer for your question."})

        # Get response using similarities
        bot_response = get_response(user_message)
        
        return jsonify({'response': bot_response})

    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        return jsonify({'error': 'Internal server error occurred.'}), 500

# --- App Execution Entry ---
if __name__ == '__main__':
    # Argument parser to support both Web and Console modes
    parser = argparse.ArgumentParser(description="FAQ Chatbot with NLP")
    parser.add_argument('--console', '-c', action='store_true', help="Run the chatbot in CLI console mode.")
    args = parser.parse_args()

    if args.console:
        print("=" * 60)
        print("   FAQ NLP CHATBOT - CONSOLE MODE (Type 'exit' to quit)   ")
        print("=" * 60)
        while True:
            try:
                user_input = input("You: ")
                if user_input.strip().lower() == "exit":
                    print("Bot: Goodbye!")
                    break
                response = get_response(user_input)
                print("Bot:", response)
                print()
            except (KeyboardInterrupt, EOFError):
                print("\nBot: Goodbye!")
                break
            except Exception as e:
                print(f"Bot: An error occurred. ({e})")
    else:
        # Run local web server
        app.run(debug=True, host='127.0.0.1', port=5000)

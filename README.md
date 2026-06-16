# NLP FAQ Chatbot

An intelligent FAQ chatbot built with Python using Natural Language Processing (NLP) to process questions and map them to responses. The application implements text preprocessing (tokenization, lowercasing, punctuation, and stop words removal) using **NLTK** and matches questions with high accuracy using a **TF-IDF Vectorizer + Cosine Similarity** framework.

This project includes **both** a premium, modern Web Chat Interface (Flask) and an interactive CLI console mode.

---

## Features

- **NLP Preprocessing**: Tokenization, lowercasing, punctuation removal, and stop word removal using the Natural Language Toolkit (NLTK).
- **TF-IDF + Cosine Similarity Matching**: Maps user queries to the closest predefined question.
- **Similarity Thresholding**: Configured with a `0.3` similarity threshold. If a query falls below this match confidence, it outputs a friendly fallback response.
- **Dual Runtime Interface**:
  - **Flask Web Interface**: A premium responsive web page using HSL blue/white design theme, ambient background gradients, glassmorphism card styling, responsive design, simulated bot typing animations, quick action FAQ pills, and a clear chat button.
  - **Interactive CLI Console Loop**: A lightweight command-line mode for direct terminal interaction.
- **Robust Exception Handling**: Graceful error wrappers for missing FAQ dataset configurations, invalid requests, and network errors.

---

## Folder Structure

```text
Chatbot/
├── app.py                # Main backend containing Flask routes & NLP similarity matching
├── faqs.json             # Dataset containing FAQ question/answer pairs
├── requirements.txt      # List of dependencies
├── README.md             # Project documentation
├── templates/
│   └── index.html        # Front-end structure for the web interface
└── static/
    ├── style.css         # Custom CSS styling (Blue/White theme & glassmorphic aesthetics)
    └── script.js         # Frontend interactive scripts (fetching APIs, typing indicator)
```

---

## Technologies Used

- **Backend / NLP**: Python, Flask, NLTK, Scikit-learn, NumPy, Pandas
- **Frontend**: HTML5, Vanilla CSS3 (Custom Variables, Flexbox, Animations), Vanilla JS (ES6 Async-Await Fetch API)
- **Icons**: Lucide Icons CDN

---

## Installation Steps

Ensure you have Python 3.8+ installed on your system.

1. **Clone or Navigate to the Directory**:
   ```bash
   cd c:/Users/Prethikesh/Desktop/Chatbot
   ```

2. **Install Dependencies**:
   Install all the packages defined in the requirements file:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On first execution, the application will automatically download the necessary NLTK datasets (`punkt` and `stopwords`) if they are not cached locally.*

---

## How to Run the Application

The application supports two execution modes:

### 1. Web Mode (Default)
To start the Flask local web server, run:
```bash
python app.py
```
After the server initializes, open your browser and navigate to:
**[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

### 2. CLI Console Mode
To run the interactive loop directly inside your terminal, pass the `--console` or `-c` flag:
```bash
python app.py --console
```
Type your question at the `You:` prompt. Type `exit` to exit the loop.

---

## FAQ Dataset Examples

The predefined FAQ database in `faqs.json` contains answers for the following queries (and similar semantic questions):
- *What are your working hours?*
- *How can I reset my password?*
- *Where is my order?*
- *Do you offer refunds?*
- *How do I contact customer support?*
- *What payment methods are accepted?*
- *Can I cancel my order?*
- *How long does shipping take?*
- *Do you provide international shipping?*
- *How can I update my profile information?*

---

## Code Quality Standards

- **Modular Design**: Separate, self-contained modules for loading dataset, tokenizing text, executing similarity indices, handling console arguments, and hosting web endpoints.
- **PEP 8 Compliant**: Adheres to Standard Python formatting with clean naming conventions, descriptive variable bindings, and docstrings.
- **Error Boundaries**: Protects route handling from empty user strings, bad json requests, missing directories, or model computation edge cases.

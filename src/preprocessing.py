import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string

import os

# Configure NLTK to use /tmp/ on Vercel for writable space
nltk_data_dir = '/tmp/nltk_data'
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
nltk.data.path.append(nltk_data_dir)

def ensure_nltk_resources():
    # Only download if not already cached in /tmp/
    try:
        nltk.data.find('tokenizers/punkt', paths=[nltk_data_dir])
    except LookupError:
        nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
        nltk.download('punkt_tab', download_dir=nltk_data_dir, quiet=True)
        nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)

ps = PorterStemmer()

def transform_text(text):
    ensure_nltk_resources()
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)

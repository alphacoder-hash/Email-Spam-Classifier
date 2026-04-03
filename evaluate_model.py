import pandas as pd
import pickle
import sys
import os
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix, classification_report

# Add src to path for preprocessing
sys.path.append(os.path.join(os.getcwd(), 'src'))
from preprocessing import transform_text

def evaluate():
    # 1. Load Data
    df = pd.read_csv('data/spam.csv', encoding='latin-1')
    df.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], inplace=True, errors='ignore')
    df.rename(columns={'v1':'target', 'v2':'text'}, inplace=True)
    
    from sklearn.preprocessing import LabelEncoder
    encoder = LabelEncoder()
    df['target'] = encoder.fit_transform(df['target'])
    df = df.drop_duplicates(keep='first')

    # Load Model and Vectorizer
    tfidf = pickle.load(open('models/vectorizer.pkl', 'rb'))
    model = pickle.load(open('models/model.pkl', 'rb'))

    # Preprocess a sample for testing
    print("Preprocessing test data...")
    df['transformed_text'] = df['text'].apply(transform_text)
    
    X = tfidf.transform(df['transformed_text']).toarray()
    y = df['target'].values

    # Predict
    print("Evaluating model...")
    y_pred = model.predict(X)

    print("\n--- Model Performance Report ---")
    print(f"Accuracy: {accuracy_score(y, y_pred):.4f}")
    print(f"Precision: {precision_score(y, y_pred):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print("\nClassification Report:")
    print(classification_report(y, y_pred))

if __name__ == "__main__":
    evaluate()

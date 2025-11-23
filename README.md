Sentiment Analysis Project
📌 Project Overview
This project performs sentiment analysis on text data using deep learning models (LSTM/GRU). The model classifies text into positive, negative, or neutral sentiments. The goal is to provide meaningful insights from textual data.
🛠️ Features
Preprocessing of raw text: removing duplicates, cleaning text, normalizing case.
Feature extraction using Word Embeddings (Word2Vec/GloVe).
Sequence padding for uniform input length.
Sentiment label encoding for model compatibility.
Deep learning models: LSTM and GRU for sequential text data.
Model evaluation using Accuracy, Precision, Recall, F1-Score, and confusion matrix visualization.
📊 Results
Achieved 70% accuracy on test data.
LSTM outperformed CNN and MLP models.
Confusion matrix confirms strong generalization across sentiments.
<img width="1275" height="800" alt="Screenshot 2025-11-23 at 7 30 10 PM" src="https://github.com/user-attachments/assets/3fb171ee-543e-4fcb-b0c6-3d82fc146942" />
<img width="1280" height="800" alt="Screenshot 2025-11-23 at 7 29 46 PM" src="https://github.com/user-attachments/assets/e569ab51-4e60-4add-<img width="1280" height="800" alt="Screenshot 2025-11-23 at 7 29 22 PM" src="https://github.com/user-attachments/assets/17c9698b-e3d0-4a5e-8ca5-44dfe0b61490" />
b73c-7c0aa2cc7800" />
<img width="1280" height="800" alt="Screenshot 2025-11-23 at 7 29 22 PM" src="https://github.com/user-attachments/assets/60b91105-f550-4b0b-8d6b-20f63fe6fcb8" />


🔧 Future Work
Experiment with pre-trained embeddings like BERT for improved accuracy.
Hyperparameter tuning to optimize model performance.
Extend to multi-lingual sentiment analysis.
📄 References
Word2Vec Paper
GloVe Paper
Keras LSTM Documentation

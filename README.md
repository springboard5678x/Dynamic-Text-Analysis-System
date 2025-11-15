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
![inferface](https://github.com/user-attachments/assets/8fcbac66-283b-4c91-ae9a-8deb9c5f0657)
![negtive page](https://github.com/user-attachments/assets/a0009e89-87f8-4cab-a100-ae6477b464af)
![interface2](https://github.com/user-attachments/assets/3103c064-e2c7-4f88-9da7-41a84d6ca35e)
🔧 Future Work
Experiment with pre-trained embeddings like BERT for improved accuracy.
Hyperparameter tuning to optimize model performance.
Extend to multi-lingual sentiment analysis.
📄 References
Word2Vec Paper
GloVe Paper
Keras LSTM Documentation

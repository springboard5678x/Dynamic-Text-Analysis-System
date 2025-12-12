 🎯 Narrative Nexus

### Dynamic Text Analysis System

Narrative Nexus is a Streamlit-based NLP application that analyzes customer reviews using:

* Sentiment Detection
* Extractive Summary
* Topic Distribution
* Keyword Extraction
* Word Cloud
* Combined Visualization Dashboard

---

## 📁 Project Structure

```
.
├── app.py
├── models/
│   ├── vectorizer.pkl
│   ├── model.pkl
│   ├── label_encoder.pkl
│   ├── lda_model_v1.gensim
│   ├── lda_model_v1.gensim.state
│   ├── lda_model_v1.gensim.expElogbeta.npy
│   └── dictionary_v1.gensim
├── Infosys/
│   └── Training notebooks
├── requirements.txt
└── README.md
```

---

## 🚀 Features

### 1️⃣ Sentiment Detection

Predicts Positive / Neutral / Negative with probability pie chart and top contributing words.

### 2️⃣ Extractive Summary

Shows top 3 key sentences + actionable insights.

### 3️⃣ Topic Distribution

Displays topic probabilities and top words for each topic (LDA model).

### 4️⃣ Word Cloud

Generates a cloud of most frequent meaningful words.

### 5️⃣ Visualization Dashboard

Shows sentiment chart, top words, topic distribution, and word cloud together.

---

## 🛠 Installation

### Clone the repository

```bash
git clone https://github.com/springboard5678x/Dynamic-Text-Analysis-System.git
cd Dynamic-Text-Analysis-System
```

### Create & activate virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 📦 Required Models (place inside `/models`)

* vectorizer.pkl
* model.pkl
* label_encoder.pkl
* lda_model_v1.gensim
* dictionary_v1.gensim
* lda_model_v1.gensim.state
* lda_model_v1.gensim.expElogbeta.npy

---

## 📊 Technologies Used

* Python
* Streamlit
* Scikit-learn
* Gensim LDA
* NLTK
* Matplotlib / WordCloud

---

## 👩‍💻 Author

Gurugubelli Manisha

Infosys Springboard Internship Project

---

## 📄 License

MIT License



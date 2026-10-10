# Project Specification: AI-Powered Agriculture Assistant (MVP)

## 1. Project Overview & Objectives
The **AI-Powered Agriculture Assistant** is a full-stack web application designed to bridge information gaps for smallholder farmers[cite: 1, 2]. It integrates conversational AI, machine learning-driven crop recommendations, computer vision for disease detection, crop yield predictions, and weather advisories into a single unified platform[cite: 1, 2, 3].

---

## 2. Core Architecture & Tech Stack

### 2.1. Frontend
* **Technologies**: HTML5, CSS3, JavaScript, and Bootstrap for a fully responsive, mobile-friendly user interface[cite: 4].
* **UI Components**: Embedded chat widget UI for the conversational assistant and separate login/dashboard views for Farmers and Administrators[cite: 4].

### 2.2. Backend & API
* **Language & Framework**: Python using **Django** (preferred for built-in authentication, ORM, and admin panel) or **Flask** for lightweight setups[cite: 4].
* **Architecture**: Client-server REST architecture where frontend views communicate with backend endpoints to handle database operations and ML inference[cite: 4].

### 2.3. Database
* **Relational Database**: MySQL or PostgreSQL[cite: 4].
* **Data Storage Schema**: User accounts, chat conversation logs, ML prediction logs, and scraped agricultural FAQ knowledge bases[cite: 4].

---

## 3. Functional Modules

### 3.1. Conversational AI Chatbot
* **NLP Pipeline**: Intent recognition and entity extraction (using NLTK or spaCy) for queries covering crop selection, fertilizers, pests, and government schemes[cite: 1, 4].
* **Model Alternatives**: 
  * *Option A (Generative)*: Seq2seq encoder-decoder LSTM model using TensorFlow/Keras (with word2vec embeddings) trained on query-response logs[cite: 1, 4].
  * *Option B (Retrieval/Keyword)*: ChatterBot library or Django-based keyword matching against a curated knowledge base targeting response times under 2 seconds[cite: 1, 4].
* **Accessibility & Channels**: Multilingual and regional-language support treated as core architecture[cite: 1]. Messaging-platform delivery integration (e.g., Telegram Bot API or WhatsApp Business API) to lower user adoption friction[cite: 1, 5].
* **Roadmap Expansion**: Multi-modal inputs supporting image/video queries and voice/video features[cite: 1, 6].

### 3.2. Crop Disease Detection (Computer Vision)
* **Architecture**: Convolutional Neural Network (CNN) image classifier built with TensorFlow/Keras or PyTorch[cite: 1, 5].
* **Input Specifications**: Leaf photos processed at $64 \times 64$ RGB input dimensions using custom CNN layers (3 convolution + max-pooling blocks) or pre-trained transfer learning models (MobileNet, ResNet)[cite: 1, 5].
* **Dataset**: Trained/fine-tuned on the **PlantVillage dataset** (54,306 images, 37 classes, 13 species, 21 diseases)[cite: 1, 5].
* **Output Requirement**: Returns both the predicted disease name and an **actionable treatment/spray recommendation** instead of a raw classification label[cite: 1].

### 3.3. Crop Recommendation System
* **Input Features**: Soil nutrients ($N, P, K$), soil pH, temperature, humidity, and rainfall[cite: 1].
* **Machine Learning Models**: 
  * Primary: **Random Forest Classifier** (achieving 90%-91.8% accuracy)[cite: 1].
  * Alternatives: Decision Tree, SVM, or ensemble majority-voting models (CHAID + Random Tree + KNN + Naïve Bayes, achieving ~88% accuracy)[cite: 1].
* **Persistence & Deployment**: Serialized using `joblib` or `pickle` for rapid inference in web views[cite: 4, 5].
* **Geo-feature**: Location-similarity recommendation mode matching a user's field parameters to similar regional crop outcomes[cite: 1].

### 3.4. Crop Yield Prediction
* **Problem Type**: Regression problem using the same soil and climate feature set[cite: 2].
* **Algorithms**: Random Forest Regression, Linear Regression, and Decision Tree Regression[cite: 2].
* **Evaluation Metrics**: Evaluated using Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and $R^2$ score[cite: 2].

### 3.5. Weather & Advisory Module
* **Weather Integration**: OpenWeatherMap API integration providing 5-10 day forecasts (temperature, humidity, atmospheric pressure, and wind speed)[cite: 2, 5].
* **Agricultural Feeds**: Market prices, government scheme updates, and seasonal advisories scraped from government portals and agricultural databases[cite: 2].
* **Smart Irrigation**: Logic driven by incoming soil-moisture metrics and weather forecast lookaheads[cite: 2].

---

## 4. Data Sourcing, Tooling & Fairness Constraints

### 4.1. Libraries & Tooling Stack
* **NLP & Data Preprocessing**: NLTK, spaCy, pandas, NumPy[cite: 4, 5].
* **Machine Learning**: `scikit-learn`[cite: 4, 5].
* **Computer Vision**: OpenCV, Pillow, TensorFlow/Keras, PyTorch[cite: 5].
* **Testing & Version Control**: Git, unit/integration testing suites for APIs and model inference[cite: 5].
* **Deployment**: Docker containerization deployed on cloud VMs/PaaS platforms (e.g., Render, Railway, AWS EC2) with webhook routes configured for messaging bots[cite: 6].

### 4.2. Datasets Required
* **PlantVillage Dataset** (Disease detection)[cite: 5].
* **Kisan Call Center (KCC) Dataset** or regional query logs (Conversational training data)[cite: 5].
* **Kaggle Crop Recommendation Dataset** ($N, P, K$, pH, temperature, humidity, rainfall to crop label)[cite: 5].
* **Web-Scraped Q&A Corpora** harvested via Python BeautifulSoup scripts[cite: 5].

### 4.3. Algorithmic Fairness & Knowledge Equity
* **Local Grounding Constraint**: To counter global conservation injustices and data skew toward Global North institutional sources in generic LLMs, responses *must* be grounded in local knowledge bases (such as regional agricultural extension data and local-language FAQs)[cite: 2].
* **Provenance Tracking**: Log and disclose data sources/provenance within chatbot answers where applicable[cite: 2].
* **Smallholder Representation**: Deliberately incorporate smallholder and localized farming practices alongside formal agronomy datasets[cite: 2].

---

## 5. Suggested Minimum Viable Product (MVP) Scope
1. **Crop Recommendation**: Random Forest model utilizing NPK and weather inputs[cite: 3].
2. **Conversational Interface**: Lightweight Django/ChatterBot or intent-matching NLP chatbot[cite: 3].
3. **Disease Detection**: CNN leaf image classifier connected to PlantVillage data[cite: 3].
4. **Weather Module**: OpenWeatherMap API integration for localized forecasts[cite: 3].
5. **Phase 2 Expansion**: Multilingual/regional-language support and IoT sensor integrations[cite: 1, 3, 6].
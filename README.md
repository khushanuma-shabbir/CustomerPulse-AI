# 🎯 CustomerPulse AI

> AI-Powered Support Ticket Prioritization System

Enterprise support teams receive hundreds of tickets daily. **CustomerPulse AI** uses machine learning to automatically predict ticket priority (Critical/High/Medium/Low) and explain the reasoning behind each prediction.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Machine Learning** | scikit-learn, Pandas, NumPy |
| **Backend API** | Python 3.11, FastAPI, Uvicorn |
| **Frontend Dashboard** | Streamlit, Plotly |
| **Database** | Supabase (PostgreSQL) |
| **Model** | Logistic Regression (72% accuracy) |

---

## ✨ Features

- 🤖 **AI Priority Prediction** - Predicts Critical/High/Medium/Low with 72% accuracy
- 🧠 **Explainable AI** - Shows reasons for each prediction
- 📊 **Interactive Dashboard** - Real-time analytics and visualizations
- 🔌 **REST API** - 7 endpoints with Swagger documentation
- 📈 **SLA Monitoring** - Track tickets at risk of SLA breach

---

## 🚀 Quick Start

### 1. Setup
```powershell
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. Train Model
```powershell
python train_model.py
```

### 4. Run Dashboard
```powershell
streamlit run app/dashboard.py
```
Opens at: **http://localhost:8501**

### 5. Run API
```powershell
python app/main.py
```
API docs at: **http://localhost:8000/docs**

---

## 📊 Model Performance

```
Model: Logistic Regression
Overall Accuracy: 72.0%
Critical Recall: 77.3%
Macro F1-Score: 70.1%
```

---

## 📁 Project Structure

```
CustomerPulse AI/
├── app/
│   ├── main.py              # FastAPI backend
│   ├── dashboard.py         # Streamlit dashboard
│   ├── priority_engine.py   # ML prediction engine
│   ├── preprocess.py        # Data preprocessing
│   ├── data_loader.py       # Data loading
│   └── supabase_client.py   # Database connection
├── model/
│   ├── priority_model.pkl   # Trained model
│   └── model_metrics.json   # Performance metrics
├── train_model.py           # Training pipeline
└── requirements.txt         # Dependencies
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/tickets` | GET | List all tickets |
| `/tickets/{id}` | GET | Get ticket + prediction |
| `/predict` | POST | Predict priority |
| `/stats` | GET | Statistics |

**Swagger UI:** http://localhost:8000/docs

---

## 📦 Dependencies

```
fastapi==0.141.1
uvicorn==0.52.4
streamlit==1.58.0
scikit-learn==1.9.0
pandas==3.0.5
numpy==2.4.6
plotly==6.7.0
supabase==2.31.0
python-dotenv==1.2.3
```

---

## 🎓 Project Info

**B.Tech IT Final Year Project**  
AI-powered ticket prioritization with explainable predictions

Built with ❤️ using Python, FastAPI, Streamlit & scikit-learn

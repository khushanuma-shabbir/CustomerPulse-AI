# 🎯 CustomerPulse AI

> **AI-Powered Support Ticket Prioritization System**

Enterprise support teams receive hundreds of tickets daily. Manual prioritization is time-consuming and inconsistent. **CustomerPulse AI** uses machine learning to automatically predict ticket priority (Critical/High/Medium/Low) and provides human-readable explanations for each prediction.

---

## 💡 Problem & Solution

**Problem:** Support engineers manually assess hundreds of tickets, leading to delayed responses, SLA breaches, and missed critical issues.

**Solution:** AI-powered system that analyzes 22 ticket attributes (customer tier, SLA status, production impact, etc.) and predicts priority with 72% accuracy, helping teams respond faster to what matters most.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Machine Learning** | scikit-learn, Pandas, NumPy | Model training & data processing |
| **Backend API** | Python 3.11, FastAPI, Uvicorn | REST API with auto-documentation |
| **Frontend Dashboard** | Streamlit, Plotly | Interactive UI & visualizations |
| **Database** | Supabase (PostgreSQL) | Cloud-based data storage |
| **ML Model** | Logistic Regression | Priority classification (72% accuracy) |

---

## ✨ Key Features

### 🤖 AI Priority Prediction
- Trained on 1,000 real support tickets
- Predicts: Critical, High, Medium, Low
- 72% overall accuracy, 77% Critical recall
- <100ms prediction time

### 🧠 Explainable AI
- Rule-based explanation engine
- Identifies top 5 factors per prediction
- Example reasons: "SLA at risk (30 min remaining)", "Major production impact", "Platinum customer"

### 📊 Interactive Dashboard
- Real-time ticket analytics
- Priority distribution charts
- SLA breach monitoring
- Customer tier breakdown
- Search & filter capabilities
- CSV/Excel upload support

### 🔌 REST API
- 7 RESTful endpoints
- Swagger UI documentation
- JSON request/response
- Batch prediction support
- CORS enabled

---

## 📊 ML Model Details

### Dataset
- **Size:** 1,000 enterprise support tickets
- **Features:** 22 attributes (customer tier, SLA, impact, product, etc.)
- **Target:** 4 priority levels
- **Split:** 80% train, 20% test

### Model Performance
```
Algorithm: Logistic Regression (selected from 4 models)
Overall Accuracy: 72.0%
Macro Precision: 69.6%
Macro Recall: 70.8%
Macro F1-Score: 70.1%

Per-Class Performance:
- Critical: 82.9% precision, 77.3% recall ✅
- High: 67.9% precision, 66.7% recall
- Medium: 56.3% precision, 58.1% recall
- Low: 71.4% precision, 81.1% recall
```

**Why Logistic Regression?** Balanced performance across all classes, especially high Critical recall (77%) to avoid missing urgent tickets.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account (for database)

### Installation

**1. Setup Environment**
```powershell
.\venv\Scripts\Activate
pip install -r requirements.txt
```

**2. Configure Database**
Create `.env` file:
```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

**3. Train Model**
```powershell
python train_model.py
```
Output: `model/priority_model.pkl` (trained model) + `model/model_metrics.json` (evaluation results)

### Running the Application

**Option A: Streamlit Dashboard** _(Recommended for demos)_
```powershell
streamlit run app/dashboard.py
```
Opens at: **http://localhost:8501**

**Option B: FastAPI Backend** _(For integrations)_
```powershell
python app/main.py
```
API docs: **http://localhost:8000/docs**

---

## 🌐 API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | API information | Base info |
| `/health` | GET | Health check | Status: OK |
| `/tickets` | GET | List tickets | `?priority=Critical&limit=50` |
| `/tickets/{id}` | GET | Get ticket + AI prediction | `/tickets/TKT-001` |
| `/predict` | POST | Predict priority | JSON body with 22 features |
| `/stats` | GET | Aggregate statistics | Total, counts by priority |

**Full Documentation:** http://localhost:8000/docs (Swagger UI)

---

## 💡 Example Prediction

**Input:**
```json
{
  "customer_tier": "Platinum",
  "issue_type": "Outage",
  "current_severity": "Critical",
  "sla_remaining_hours": 0.5,
  "production_impact": "Major",
  "affected_users_estimate": 10000
}
```

**Output:**
```json
{
  "predicted_priority": "Critical",
  "confidence": 0.94,
  "reasons": [
    "SLA at risk (only 0.5 hours remaining)",
    "Major production impact",
    "Large number of affected users (10000+)",
    "Platinum tier customer",
    "Critical severity reported"
  ]
}
```

---

## 📁 Project Structure

```
CustomerPulse AI/
├── app/
│   ├── main.py              # FastAPI REST API
│   ├── dashboard.py         # Streamlit dashboard UI
│   ├── priority_engine.py   # ML prediction + explanations
│   ├── preprocess.py        # Data preprocessing pipeline
│   ├── data_loader.py       # Supabase data loading
│   ├── file_uploader.py     # CSV/Excel upload handler
│   ├── queue_engine.py      # Dynamic queue management
│   ├── queue_state.py       # State tracking
│   └── supabase_client.py   # Database connection
├── model/
│   ├── priority_model.pkl   # Trained ML model
│   └── model_metrics.json   # Evaluation metrics
├── data/                    # Upload directory
├── train_model.py           # ML training pipeline
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
└── README.md                # This file
```

---

## 🔧 Dependencies

**Core:**
- `python==3.11`
- `fastapi==0.141.1` - REST API framework
- `uvicorn==0.52.4` - ASGI server
- `streamlit==1.58.0` - Dashboard UI

**Machine Learning:**
- `scikit-learn==1.9.0` - ML algorithms
- `pandas==3.0.5` - Data manipulation
- `numpy==2.4.6` - Numerical computing

**Database & Visualization:**
- `supabase==2.31.0` - Database client
- `plotly==6.7.0` - Interactive charts
- `python-dotenv==1.2.3` - Environment config

---

## 🎓 Project Highlights

✅ **End-to-end ML pipeline** (data → training → deployment)  
✅ **Production-ready** (API + Dashboard)  
✅ **Explainable AI** (not a black box)  
✅ **Human-in-the-loop** (AI assists, humans decide)  
✅ **Real-world application** (solves actual business problem)

---

## 🔮 Future Enhancements

- NLP analysis of ticket descriptions (BERT/LSTM)
- Auto-assignment to best team member
- SLA breach prediction
- JIRA/ServiceNow integration
- Email/Slack alerts for critical tickets

---

## 📝 License

**B.Tech IT Final Year Project**  
Built with ❤️ using Python, FastAPI, Streamlit, scikit-learn & Supabase

---

*CustomerPulse AI - Helping support teams respond to what matters most, faster.* 🚀

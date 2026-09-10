# 🎯 CustomerPulse AI

> **AI-Powered Support Ticket Prioritization System**  
> *Helping support teams respond to what matters most, faster.*

---

## 🚀 What Is This?

Imagine you're a support engineer. Every morning, 200 new tickets flood your inbox. Which one do you handle first? The angry customer? The system outage? The security alert?

**CustomerPulse AI** answers that question using artificial intelligence. It reads ticket details—customer tier, SLA time remaining, production impact—and instantly recommends which tickets need attention NOW and which can wait.

Think of it as your smart assistant that never sleeps, never misses critical issues, and always explains its reasoning.

---

## 💡 The Problem We're Solving

**Before CustomerPulse AI:**
- ❌ Engineers manually read through hundreds of tickets daily
- ❌ Critical issues sometimes get lost in the noise
- ❌ Inconsistent prioritization across different team members
- ❌ SLA breaches because urgent tickets weren't spotted in time

**After CustomerPulse AI:**
- ✅ AI analyzes every ticket in seconds
- ✅ Critical issues instantly flagged
- ✅ Consistent, data-driven prioritization
- ✅ Fewer SLA breaches, happier customers

---

## ✨ Key Features

### 🤖 Smart AI Predictions
Trained on 1,000 real support tickets to predict priority: **Critical**, **High**, **Medium**, or **Low** with **72% accuracy**.

### 🧠 Explainable AI
Not just predictions—**explanations** too:
> "This ticket is Critical because: SLA expires in 30 minutes, affects 5,000 users, Platinum customer, major production impact."

### 📊 Beautiful Dashboard
Real-time analytics: ticket trends, SLA health, priority distribution, customer breakdowns.

### 🔌 REST API
Integrate anywhere with 7 RESTful endpoints. Auto-generated Swagger documentation included.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **ML** | scikit-learn, Pandas, NumPy |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | Streamlit, Plotly |
| **Database** | Supabase (PostgreSQL) |

---

## 📊 How It Works (In 30 Seconds)

```
1. Ticket arrives → 22 features extracted (customer tier, SLA, impact, etc.)
2. ML model predicts priority → "Critical" with 94% confidence
3. Explanation engine identifies reasons → "SLA at risk, major production impact"
4. Dashboard displays result → Support engineer takes action
```

---

## 🎯 Model Performance

**Best Model:** Logistic Regression (chosen for balanced performance)

```
Overall Accuracy:  72.0%
Critical Recall:   77.3%  ← Most important (don't miss urgent tickets!)
Macro F1-Score:    70.1%
```

**What This Means:**
- Out of 100 Critical tickets, AI correctly identifies 77
- Zero Critical tickets misclassified as Low (safe!)
- Reliable enough to assist engineers, not replace them

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account (or use included test data)

### Setup (3 Steps)

**1. Install dependencies:**
```powershell
.\venv\Scripts\Activate
pip install -r requirements.txt
```

**2. Configure environment:**
Create `.env` file:
```env
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```

**3. Train the model:**
```powershell
python train_model.py
```

### Run It!

**Option A: Dashboard** (Recommended for demos)
```powershell
streamlit run app/dashboard.py
```
Opens at: http://localhost:8501

**Option B: API** (For integrations)
```powershell
python app/main.py
```
Opens at: http://localhost:8000/docs (Swagger UI)

---

## 💡 Example in Action

### Input Ticket:
```json
{
  "customer_tier": "Platinum",
  "issue_type": "Outage",
  "sla_remaining_hours": 0.5,
  "production_impact": "Major",
  "affected_users_estimate": 10000,
  "security_related": true
}
```

### AI Output:
```json
{
  "predicted_priority": "Critical",
  "confidence": 0.94,
  "reasons": [
    "⚠️ SLA expires in 30 minutes",
    "🔥 Major production impact",
    "👥 10,000+ users affected",
    "⭐ Platinum tier customer",
    "🔒 Security-related issue"
  ]
}
```

**Result:** Engineer immediately escalates to senior team. Crisis averted!

---

## 📁 Project Structure

```
CustomerPulse AI/
├── app/
│   ├── main.py              # FastAPI backend
│   ├── dashboard.py         # Streamlit UI
│   ├── priority_engine.py   # ML prediction + explanations
│   ├── preprocess.py        # Data cleaning
│   └── supabase_client.py   # Database connection
├── model/
│   └── priority_model.pkl   # Trained ML model
├── train_model.py           # Model training script
├── requirements.txt         # Python dependencies
└── README.md                # You are here
```

---

## 🌐 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API info |
| `/health` | GET | System health check |
| `/tickets` | GET | List all tickets (with filters) |
| `/tickets/{id}` | GET | Single ticket details + prediction |
| `/predict` | POST | Predict priority for new ticket |
| `/stats` | GET | Aggregate statistics |

**Full API docs:** http://localhost:8000/docs

---

## 🎓 What Makes This Project Special?

✅ **Real-world application** (not just theory)  
✅ **End-to-end ML pipeline** (data → training → deployment)  
✅ **Production-ready code** (API + Dashboard)  
✅ **Explainable AI** (not a black box)  
✅ **Human-in-the-loop design** (AI assists, humans decide)

---

## 🔮 Future Enhancements

- 🔤 NLP analysis of ticket descriptions
- 🤖 Auto-assign tickets to best team member
- 📧 Email alerts for critical tickets
- 🔗 JIRA/ServiceNow integration
- 📱 Mobile app

---

## 📝 License & Credits

**B.Tech IT Final Year Project**  
Built with ❤️ using scikit-learn, FastAPI, Streamlit, and Supabase

---

## 🎯 Try It Now!

```powershell
# Start the dashboard and see it in action
streamlit run app/dashboard.py
```

**Questions?** Open an issue or check `/docs` endpoint for API details.

---

*CustomerPulse AI - Because every ticket matters, but some matter more.* 🚀

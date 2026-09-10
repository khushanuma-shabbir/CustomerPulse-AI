# 🎤 CustomerPulse AI - Presentation Guide

## 📋 Presentation Structure (15-20 minutes)

### 1. Introduction (2 minutes)

**Title Slide:**
```
CustomerPulse AI
AI-Powered Customer Support Ticket Prioritization System

B.Tech IT Final Year Project
[Your Name]
[Your College]
```

**Opening Statement:**
> "In enterprise support environments like HPE, support teams receive hundreds of customer tickets daily. Manual prioritization is time-consuming, inconsistent, and error-prone. CustomerPulse AI uses machine learning to assist support engineers in quickly identifying urgent tickets while providing transparent explanations for each prediction."

---

### 2. Problem Statement (2 minutes)

**Slide Content:**
- **Challenge**: Manual ticket prioritization in high-volume support environments
- **Issues**:
  - Time-consuming assessment
  - Inconsistent prioritization across engineers
  - Risk of missing critical issues
  - SLA breaches due to delayed response

**Key Statistics:**
- 1000+ tickets analyzed
- 4 priority levels (Critical, High, Medium, Low)
- Multiple factors to consider (22 attributes)

**Business Impact:**
- Lost revenue from delayed critical issues
- Poor customer satisfaction
- SLA violations and penalties
- Inefficient resource allocation

---

### 3. Proposed Solution (2 minutes)

**Slide Content:**

**CustomerPulse AI provides:**
1. **AI-Powered Prediction**: ML model predicts ticket priority
2. **Explanation Engine**: Human-readable reasons for each prediction
3. **REST API**: Integration-ready backend
4. **Enterprise Dashboard**: Real-time analytics and monitoring

**Key Principle:**
> Human-in-the-Loop: AI assists support engineers, does not replace them

**Architecture Diagram:**
```
Supabase DB → Data Processing → ML Model → Priority Engine → FastAPI + Dashboard → Support Engineers
```

---

### 4. Technology Stack (1 minute)

**Slide Content:**

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, FastAPI |
| **Machine Learning** | scikit-learn, Pandas, NumPy |
| **Database** | Supabase (PostgreSQL) |
| **Frontend** | Streamlit, Plotly |
| **Deployment** | Uvicorn, ASGI |

**Why These Technologies?**
- Python: Industry standard for ML
- FastAPI: Modern, fast, auto-documented API
- scikit-learn: Proven ML library
- Streamlit: Rapid dashboard development
- Supabase: Cloud-based PostgreSQL

---

### 5. Dataset & Features (2 minutes)

**Slide Content:**

**Dataset:**
- Source: Supabase database
- Size: 1,000 enterprise support tickets
- Target: 4 priority levels (Critical, High, Medium, Low)

**Feature Categories:**

**Customer Information (3 features):**
- Customer tier (Platinum, Gold, Silver, Standard)
- Customer sentiment
- Contact frequency

**Product Information (3 features):**
- Product name
- Product category
- Product criticality

**Ticket Attributes (6 features):**
- Issue type
- Channel
- Current severity
- Status
- Urgency keywords
- Assigned team

**Impact Assessment (4 features):**
- Production impact
- Business impact
- Affected users
- Security-related

**SLA Information (3 features):**
- SLA target hours
- SLA remaining hours
- SLA breached

**History (3 features):**
- Reopen count
- Previous escalation
- Waiting time

**Total: 22 Features Used**

---

### 6. ML Methodology (3 minutes)

**Slide Content:**

**Step 1: Data Preprocessing**
- Feature selection (22 features)
- Categorical encoding (OneHotEncoder)
- Missing value handling
- Boolean conversion (Yes/No → 1/0)

**Step 2: Train-Test Split**
- 80% training (800 tickets)
- 20% testing (200 tickets)
- Stratified split (maintains class distribution)

**Step 3: Model Training**
Four algorithms compared:
1. Random Forest Classifier
2. **Logistic Regression** ⭐ (Selected)
3. Decision Tree Classifier
4. Gradient Boosting Classifier

**Step 4: Model Selection**
- Primary metric: Macro F1-Score
- Best model: Logistic Regression (70.1% F1)
- Balanced performance across all classes

---

### 7. Model Performance (3 minutes)

**Slide Content:**

**Overall Performance:**
| Metric | Value |
|--------|-------|
| Accuracy | **72.0%** |
| Macro Precision | **69.6%** |
| Macro Recall | **70.8%** |
| Macro F1-Score | **70.1%** |

**Per-Class Performance:**
| Priority | Precision | Recall | F1-Score |
|----------|-----------|--------|----------|
| Critical | 82.9% | 77.3% | 80.0% |
| High | 67.9% | 66.7% | 67.3% |
| Medium | 56.3% | 58.1% | 57.1% |
| Low | 71.4% | 81.1% | 76.0% |

**Key Achievements:**
- ✅ No Critical tickets misclassified as Low
- ✅ High Critical precision (82.9%)
- ✅ Good Low priority recall (81.1%)
- ✅ Balanced performance

**Confusion Matrix:**
```
Predicted →   Critical  High  Medium  Low
Actual ↓
Critical         58      13      4      0  ← 77% correct
High             11      38      5      3
Medium            1       3     18      9
Low               0       2      5     30  ← 81% correct
```

---

### 8. Explainable AI (2 minutes)

**Slide Content:**

**Explanation Engine:**
- Rule-based reasoning system
- Identifies top 5 factors per prediction
- Human-readable explanations

**Example Critical Prediction:**
```
Predicted Priority: Critical
Confidence: 97.5%

Reasons:
• Major production impact
• SLA at risk (only 1.5 hours remaining)
• Large number of affected users (5000+)
• Platinum tier customer
• Critical severity reported
```

**Why Explanations Matter:**
- Builds trust in AI predictions
- Helps engineers understand urgency
- Transparent decision-making
- Compliance and auditing

---

### 9. LIVE DEMO (5 minutes)

**Demo Script:**

**Part 1: Dashboard (2 minutes)**
```powershell
# Start dashboard
streamlit run app\dashboard.py
```

**Show:**
1. Overview metrics (total tickets, priority breakdown)
2. Distribution charts (pie chart, bar chart)
3. SLA status monitoring
4. Customer tier breakdown
5. Filters in action (filter by Critical priority)
6. Ticket search

**Part 2: AI Prediction (2 minutes)**
1. Expand a Critical ticket
2. Click "Generate AI Prediction"
3. Show predicted priority, confidence, and reasons
4. Compare with ground truth
5. Expand a Low priority ticket
6. Generate prediction and compare

**Part 3: API Documentation (1 minute)**
```powershell
# Start API
python app\main.py
```
- Open http://localhost:8000/docs
- Show Swagger UI
- Demonstrate `/predict` endpoint
- Show request/response format

---

### 10. System Architecture (1 minute)

**Slide Content:**

**Component Architecture:**
```
┌─────────────────────┐
│   Supabase DB       │
│   (1000 Tickets)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Processing    │
│  • Feature Eng.     │
│  • Preprocessing    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ML Model          │
│  Logistic Regression│
│  (72% Accuracy)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Priority Engine    │
│  • Prediction       │
│  • Explanation      │
└─────┬─────────┬─────┘
      │         │
      ▼         ▼
┌──────────┐ ┌──────────┐
│ FastAPI  │ │Streamlit │
│ Backend  │ │Dashboard │
└──────────┘ └──────────┘
      │         │
      └────┬────┘
           │
           ▼
    ┌─────────────┐
    │   Users     │
    │  (Support   │
    │  Engineers) │
    └─────────────┘
```

**API Endpoints:**
- GET `/` - API info
- GET `/tickets` - List tickets
- GET `/tickets/{id}` - Ticket details
- POST `/predict` - Predict priority
- GET `/stats` - Statistics

---

### 11. Key Features (1 minute)

**Slide Content:**

**1. AI-Powered Prediction**
- 72% accuracy
- <100ms response time
- Confidence scores

**2. Explainable AI**
- Top 5 reasons per prediction
- Transparent reasoning
- Human-readable

**3. Enterprise Dashboard**
- Real-time analytics
- Interactive visualizations
- Filtering and search

**4. REST API**
- 7 endpoints
- Auto-generated docs
- JSON responses

**5. Human-in-the-Loop**
- AI assists, humans decide
- Comparison with ground truth
- Audit trail

---

### 12. Challenges & Solutions (1 minute)

**Slide Content:**

| Challenge | Solution |
|-----------|----------|
| **Class Imbalance** | Stratified split, balanced weights |
| **Many Categorical Features** | OneHotEncoder with unknown handling |
| **Missing Values** | Median/mode imputation |
| **Feature Leakage** | Excluded original_priority_score |
| **Explainability** | Rule-based reasoning engine |
| **Performance** | Optimized model, caching |

---

### 13. Limitations & Future Work (1 minute)

**Current Limitations:**
- Text analysis not implemented (issue descriptions)
- Medium class performance (57% F1)
- No real-time learning
- Manual model retraining required

**Future Enhancements:**

**Short Term:**
- NLP analysis of issue descriptions
- SHAP/LIME explanations
- Automated retraining pipeline

**Medium Term:**
- Deep learning models (LSTM/BERT)
- Real-time monitoring
- Auto-assignment recommendations

**Long Term:**
- JIRA/ServiceNow integration
- Mobile application
- Multi-language support

---

### 14. Project Impact (1 minute)

**Slide Content:**

**Business Value:**
- ⏱️ Faster ticket triage
- 🎯 Consistent prioritization
- 🚨 Reduced risk of missing critical issues
- 📊 Data-driven decision making
- 💰 Potential SLA breach reduction

**Technical Value:**
- ✅ Production-ready code
- ✅ Comprehensive documentation
- ✅ Modular architecture
- ✅ Easy deployment
- ✅ API-first design

**Academic Value:**
- 📚 Applied ML in real-world scenario
- 🔬 Evaluated multiple algorithms
- 📊 Proper train/test methodology
- 📝 Complete documentation

---

### 15. Conclusion (1 minute)

**Slide Content:**

**Project Summary:**
- ✅ Built end-to-end ML system
- ✅ Achieved 72% accuracy (4-class problem)
- ✅ Created explainable AI
- ✅ Developed REST API
- ✅ Built enterprise dashboard

**Key Takeaway:**
> CustomerPulse AI demonstrates how AI can assist human decision-making in enterprise support environments, providing both accurate predictions and transparent explanations.

**Technology Stack:**
Python • FastAPI • scikit-learn • Streamlit • Supabase

**Project Status:**
Production Ready ✅

---

## 🎯 Demo Preparation Checklist

### Before Presentation
- [ ] Model trained (`model/priority_model.pkl` exists)
- [ ] Database connection working
- [ ] API server tested
- [ ] Dashboard tested
- [ ] Internet connection stable (for Supabase)
- [ ] Browser tabs ready:
  - http://localhost:8000/docs
  - http://localhost:8501
- [ ] Backup slides ready
- [ ] Code ready to show if asked

### Have Ready to Show
- [ ] Dashboard with real-time data
- [ ] API documentation (Swagger UI)
- [ ] Sample prediction with explanation
- [ ] Model performance metrics
- [ ] Confusion matrix
- [ ] Architecture diagram

### Terminal Commands Ready
```powershell
# Start API
cd "d:\Project\CustomerPulse AI"
.\venv\Scripts\Activate
python app\main.py

# Start Dashboard (new terminal)
cd "d:\Project\CustomerPulse AI"
.\venv\Scripts\Activate
streamlit run app\dashboard.py
```

---

## 🗣️ Sample Q&A

### Q: Why did you choose Logistic Regression over Random Forest?
**A:** "Logistic Regression achieved the highest Macro F1-score (70.1%) and provides better generalization. While Gradient Boosting had slightly higher accuracy, Logistic Regression offers more balanced performance across all priority classes, which is crucial for not missing critical tickets."

### Q: How do you handle new ticket data?
**A:** "The system uses OneHotEncoder with handle_unknown='ignore', so new categorical values are handled gracefully. However, for significant data drift, the model should be retrained periodically with recent tickets."

### Q: What makes your AI explainable?
**A:** "We implemented a rule-based explanation engine that identifies the top 5 factors influencing each prediction based on ticket attributes like SLA status, production impact, affected users, and customer tier. This provides transparency and helps engineers understand why a ticket was prioritized at a certain level."

### Q: How accurate is 72%? Is that good enough?
**A:** "For a 4-class classification problem with imbalanced data, 72% is solid performance. More importantly, we have 82.9% precision for Critical tickets and 0% misclassification of Critical as Low, which means we're not missing urgent issues. The system assists engineers - they make final decisions."

### Q: Can this system replace support engineers?
**A:** "Absolutely not. CustomerPulse AI follows a human-in-the-loop approach. It assists support engineers by providing AI-powered recommendations, but final prioritization decisions remain with human experts who have domain knowledge and context that the AI doesn't have."

### Q: How do you handle text data in issue descriptions?
**A:** "Currently, we don't use issue descriptions for ML predictions. This is a planned future enhancement using NLP techniques like BERT or LSTM. The current model focuses on structured features which already achieves good performance."

### Q: What happens if the model makes a wrong prediction?
**A:** "The system provides confidence scores and explanations. If the confidence is low or the reasoning seems off, engineers can override the prediction. Additionally, all predictions can be logged for model retraining and improvement."

### Q: How long does training take?
**A:** "Training on 1000 tickets takes about 30-60 seconds on a standard laptop. The preprocessing and model training are well-optimized using scikit-learn."

### Q: Is this production-ready?
**A:** "The core functionality is production-ready. For enterprise deployment, we'd need to add authentication, monitoring, automated retraining pipelines, and integration with existing ticketing systems like JIRA or ServiceNow."

### Q: What was the biggest challenge?
**A:** "Balancing model performance across all priority classes, especially the Medium class which showed the most confusion with other priorities. We addressed this through stratified sampling, balanced class weights, and careful feature engineering."

---

## 💡 Tips for Successful Presentation

### Do's ✅
- ✅ Start with the business problem
- ✅ Show the live demo early
- ✅ Explain technical terms simply
- ✅ Emphasize human-in-the-loop approach
- ✅ Highlight explainability
- ✅ Show metrics and confusion matrix
- ✅ Prepare for questions
- ✅ Have backup slides

### Don'ts ❌
- ❌ Don't dive too deep into math
- ❌ Don't skip the demo
- ❌ Don't oversell AI capabilities
- ❌ Don't ignore limitations
- ❌ Don't assume audience knows ML
- ❌ Don't rush through metrics
- ❌ Don't forget to credit tools/libraries

### Presentation Style
- **Pace**: Moderate, clear
- **Tone**: Professional, confident
- **Language**: Simple, accessible
- **Visuals**: Clean, professional
- **Demo**: Smooth, rehearsed

---

## 📊 Suggested Slide Deck Outline

1. Title Slide
2. Introduction & Problem Statement
3. Business Impact
4. Proposed Solution
5. System Architecture
6. Technology Stack
7. Dataset Overview
8. Features Used (22 attributes)
9. ML Methodology
10. Model Comparison
11. Performance Metrics
12. Confusion Matrix
13. Explainable AI
14. **LIVE DEMO** (Dashboard)
15. **LIVE DEMO** (API)
16. Key Features
17. Challenges & Solutions
18. Limitations & Future Work
19. Project Impact
20. Conclusion
21. Thank You / Q&A

**Total: ~20 slides for 15-20 minute presentation**

---

## 🎬 Demo Script (Detailed)

### Dashboard Demo (3 minutes)

**Step 1: Overview (30 seconds)**
```
1. Open dashboard (should already be running)
2. Point out main metrics at top
3. "As you can see, we have 1000 tickets total"
4. "377 Critical, 286 High, 155 Medium, 182 Low"
```

**Step 2: Visualizations (30 seconds)**
```
1. Show priority distribution pie chart
2. Show production impact chart
3. Show SLA status
4. "These visualizations help support teams understand ticket distribution"
```

**Step 3: Filters (30 seconds)**
```
1. Click sidebar
2. Select "Critical" priority filter
3. "Now showing only 377 critical tickets"
4. Show SLA breached filter
5. "We can identify at-risk tickets immediately"
```

**Step 4: Ticket Details (1 minute)**
```
1. Scroll to ticket list
2. Expand a Critical ticket (TKT-001 or similar)
3. Read issue description briefly
4. Point out ground truth: "This ticket is marked as Critical"
```

**Step 5: AI Prediction (1 minute)**
```
1. Click "Generate AI Prediction"
2. Wait for prediction (1-2 seconds)
3. "The AI also predicts Critical with 97% confidence"
4. Read the reasons:
   - "Major production impact"
   - "SLA at risk"
   - "Large number of affected users"
   - "Platinum tier customer"
5. "Notice how the AI explains its reasoning"
6. Show another ticket for contrast (Low priority)
```

### API Demo (2 minutes)

**Step 1: API Documentation (1 minute)**
```
1. Switch to browser tab with Swagger UI
2. "FastAPI automatically generates interactive documentation"
3. Show list of endpoints
4. Click on POST /predict
5. "This is the prediction endpoint"
```

**Step 2: Make Prediction (1 minute)**
```
1. Click "Try it out"
2. Use pre-filled example or modify
3. Click "Execute"
4. Show response:
   - predicted_priority
   - confidence
   - reasons array
5. "The API returns JSON that can be integrated with any system"
```

---

**Good luck with your presentation! 🎉**

*Remember: Confidence, clarity, and demonstrating real value are key!*

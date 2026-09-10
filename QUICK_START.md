# 🚀 CustomerPulse AI - Quick Start Guide

## Prerequisites Checklist
- ✅ Python 3.11 installed
- ✅ Virtual environment activated
- ✅ Dependencies installed
- ✅ `.env` file configured with Supabase credentials
- ✅ Model trained (`model/priority_model.pkl` exists)

---

## Option 1: Run API Server

### Method A: Using Batch File (Windows)
```
Double-click: start_api.bat
```

### Method B: Manual Command
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Start API server
python app\main.py
```

### Access Points
- **API Root**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test API
```powershell
# Get all tickets
curl http://localhost:8000/tickets?limit=10

# Get statistics
curl http://localhost:8000/stats

# Get specific ticket
curl http://localhost:8000/tickets/TKT-001
```

---

## Option 2: Run Dashboard

### Method A: Using Batch File (Windows)
```
Double-click: start_dashboard.bat
```

### Method B: Manual Command
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Start dashboard
streamlit run app\dashboard.py
```

### Access Dashboard
Open browser: http://localhost:8501

---

## Common Commands

### 1. Test Database Connection
```powershell
.\venv\Scripts\Activate
python test_supabase.py
```

### 2. Train/Retrain Model
```powershell
.\venv\Scripts\Activate
python train_model.py
```
Expected time: 30-60 seconds

### 3. Test Priority Engine
```powershell
.\venv\Scripts\Activate
python -m app.priority_engine
```

### 4. Run Preprocessing Only
```powershell
.\venv\Scripts\Activate
python -m app.preprocess
```

### 5. Exploratory Data Analysis
```powershell
.\venv\Scripts\Activate
python -m app.eda
```

---

## API Usage Examples

### 1. Make a Prediction
```python
import requests

url = "http://localhost:8000/predict"
ticket = {
    "customer_tier": "Platinum",
    "product": "Database Server",
    "product_category": "Infrastructure",
    "product_criticality": "Critical",
    "issue_type": "Outage",
    "channel": "Phone",
    "current_severity": "Critical",
    "sla_target_hours": 4.0,
    "sla_remaining_hours": 1.5,
    "sla_breached": 0,
    "reopen_count": 0,
    "customer_contact_count": 3,
    "production_impact": "Major",
    "business_impact": "High",
    "affected_users_estimate": 5000,
    "security_related": 1,
    "customer_sentiment": "Frustrated",
    "urgency_keywords": "Critical",
    "waiting_time_hours": 2.0,
    "status": "Open",
    "assigned_team": "Infrastructure",
    "previous_escalation": 0
}

response = requests.post(url, json=ticket)
print(response.json())
```

### 2. Get Ticket Statistics
```python
import requests

response = requests.get("http://localhost:8000/stats")
stats = response.json()

print(f"Total Tickets: {stats['total_tickets']}")
print(f"Critical Tickets: {stats['critical_tickets']}")
print(f"Priority Distribution: {stats['priority_distribution']}")
```

### 3. Filter Tickets
```python
import requests

# Get only Critical tickets
response = requests.get(
    "http://localhost:8000/tickets?priority=Critical&limit=50"
)
tickets = response.json()['tickets']
```

---

## Dashboard Features

### Main Views
1. **Overview Metrics**
   - Total tickets
   - Priority breakdown (Critical, High, Medium, Low)
   - Distribution charts

2. **Filters (Sidebar)**
   - Priority filter
   - Status filter
   - Customer tier filter
   - SLA breach filter

3. **Analytics Charts**
   - Priority distribution pie chart
   - Production impact bar chart
   - SLA status breakdown
   - Customer tier distribution
   - Security issues count

4. **Ticket List**
   - Search by ticket ID or description
   - Expandable ticket details
   - AI prediction button (per ticket)
   - Explanation display

### Using AI Predictions in Dashboard
1. Open dashboard
2. Scroll to "Ticket Details & AI Predictions"
3. Expand any ticket
4. Click "Generate AI Prediction"
5. View predicted priority, confidence, and reasons
6. Compare with ground truth

---

## Troubleshooting

### Problem: Model not loaded
**Error**: `Priority engine not available`

**Solution**:
```powershell
# Train the model first
python train_model.py
```

### Problem: Database connection failed
**Error**: `Database error` or connection timeout

**Solution**:
1. Check `.env` file exists
2. Verify `SUPABASE_URL` and `SUPABASE_KEY`
3. Test connection:
```powershell
python test_supabase.py
```

### Problem: Import errors
**Error**: `ModuleNotFoundError`

**Solution**:
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Port already in use
**Error**: `Address already in use: 8000`

**Solution**:
```powershell
# Use different port
uvicorn app.main:app --port 8001

# Or for dashboard
streamlit run app\dashboard.py --server.port 8502
```

### Problem: Streamlit not found
**Error**: `streamlit: command not found`

**Solution**:
```powershell
pip install streamlit plotly
```

---

## Development Workflow

### Making Changes to Code

1. **Modify ML Model**
   ```powershell
   # Edit train_model.py
   # Retrain model
   python train_model.py
   
   # Test predictions
   python -m app.priority_engine
   ```

2. **Modify API Endpoints**
   ```powershell
   # Edit app/main.py
   # Restart API server (auto-reloads if using uvicorn --reload)
   uvicorn app.main:app --reload
   ```

3. **Modify Dashboard**
   ```powershell
   # Edit app/dashboard.py
   # Streamlit auto-reloads when file changes
   ```

4. **Update Preprocessing**
   ```powershell
   # Edit app/preprocess.py
   # Test preprocessing
   python -m app.preprocess
   
   # Retrain model with new preprocessing
   python train_model.py
   ```

---

## Performance Tips

### API Performance
- Use batch predictions for multiple tickets
- Enable caching for repeated queries
- Limit response size with pagination

### Dashboard Performance
- Use filters to reduce displayed tickets
- Cache is enabled (5 minutes TTL)
- Limit search results to top 20 tickets

### Model Performance
- Current model: ~72% accuracy
- Prediction time: < 100ms per ticket
- Batch processing: ~50 tickets/second

---

## Project Checklist

### Before Presentation
- [ ] Model trained with good metrics (>70% accuracy)
- [ ] API server runs without errors
- [ ] Dashboard displays correctly
- [ ] All endpoints tested
- [ ] Sample predictions ready to demonstrate
- [ ] README.md up to date
- [ ] Code comments added

### For Demonstration
1. Show dashboard first (most impressive visually)
2. Demonstrate AI prediction on a Critical ticket
3. Show API documentation (Swagger UI)
4. Explain model performance metrics
5. Discuss human-in-the-loop approach
6. Present future improvements

### For Documentation
- README.md - Complete project documentation
- QUICK_START.md - This file
- model/model_metrics.json - Training results
- Code comments - Inline documentation

---

## Next Steps

### Immediate (Already Done)
✅ Data preprocessing
✅ ML model training
✅ API development
✅ Dashboard creation
✅ Model evaluation

### Short Term (Optional Enhancements)
- [ ] Add user authentication
- [ ] Implement model retraining pipeline
- [ ] Add email notifications
- [ ] Create admin panel
- [ ] Add more visualizations

### Long Term (Future Work)
- [ ] NLP analysis of issue descriptions
- [ ] Deep learning models
- [ ] Real-time ticket monitoring
- [ ] Mobile app
- [ ] Integration with JIRA/ServiceNow

---

## Support

### Getting Help
1. Check this Quick Start guide
2. Review README.md
3. Check API documentation at `/docs`
4. Review code comments
5. Check model metrics in `model/model_metrics.json`

### Useful Files
- `README.md` - Comprehensive documentation
- `train_model.py` - ML training pipeline
- `app/main.py` - API application
- `app/dashboard.py` - Dashboard application
- `app/priority_engine.py` - Prediction logic
- `model/model_metrics.json` - Performance metrics

---

**Happy Prioritizing! 🎯**

*CustomerPulse AI - AI-Assisted Support Ticket Management*

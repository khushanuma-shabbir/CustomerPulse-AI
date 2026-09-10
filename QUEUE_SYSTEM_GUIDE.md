# CustomerPulse AI - Dynamic Queue System Guide

## 🎯 Overview

CustomerPulse AI has been upgraded from a static priority prediction system to a **dynamic, time-aware ticket queue** with aging, starvation detection, and solve functionality.

---

## ✨ New Features

### 1. **CSV/Excel Upload**
- Upload ANY number of tickets (5, 50, 500, 10,000+)
- Supports both `.csv` and `.xlsx` files
- Automatic data validation and normalization
- Handles missing columns gracefully

### 2. **Time-Aware Calculations**
- Uses **actual current datetime** (not hardcoded)
- Dynamic ticket age: `current_time - created_at`
- Dynamic SLA remaining: `sla_target - ticket_age`
- Real-time SLA breach detection

### 3. **Aging Logic**
Older tickets gradually get priority boosts:
- **24+ hours**: Low → Medium
- **48+ hours**: Medium → High  
- **72+ hours**: High → Critical

### 4. **Starvation Detection**
Tickets repeatedly bypassed by higher-priority tickets get boosted:
- Tracks `times_bypassed` for each ticket
- Applies starvation boost when bypass count ≥ 5
- Prevents tickets from being ignored forever

### 5. **Dynamic Queue Ranking**
Final priority combines:
- ML prediction (base priority)
- SLA risk score
- Business/customer impact
- Aging boost
- Starvation boost
- Security/urgency factors

### 6. **Solve Functionality**
- Click "Solve" button on any ticket
- Ticket marked as SOLVED and removed from active queue
- Remaining tickets automatically re-ranked
- Queue recalculates with updated time/aging

### 7. **Next Ticket Recommendation**
- Prominently displays #1 priority ticket
- Shows why it's the top priority
- Includes all key metrics (age, SLA, impact, etc.)

### 8. **Export Queue**
- Download analyzed queue as CSV
- Includes all scores, priorities, and reasons

---

## 🚀 How to Use

### Step 1: Start Dashboard
```bash
streamlit run dashboard.py
```

Dashboard opens at: http://localhost:8501

### Step 2: Upload Tickets

**Option A: Upload CSV/Excel**
1. Click "Upload CSV or Excel file"
2. Select your file
3. Click "Process File"

**Option B: Load from Supabase**
1. Click "Load Historical Tickets"
2. System loads first 100 tickets from database

### Step 3: View Dynamic Queue

The dashboard shows:
- **Next Ticket to Solve** - Top priority with prominent display
- **Queue Overview** - Metrics by priority level
- **Active Queue Table** - All tickets ranked by final score

### Step 4: Solve Tickets

1. Review the #1 recommended ticket
2. Click "✅ SOLVE THIS TICKET"
3. System automatically:
   - Marks ticket as SOLVED
   - Removes it from active queue
   - Recalculates remaining tickets
   - Shows new #1 ticket

### Step 5: Export Results

Click "Download Queue as CSV" to export the analyzed queue

---

## 📊 Priority Scoring System

### Final Score Formula
```
final_score = 
    (ML_score × 1.0) +
    (SLA_risk_score × 1.5) +
    (Impact_score × 1.2) +
    (Aging_boost × 0.8) +
    (Starvation_boost × 1.0) +
    (Security_score × 1.3) +
    (Urgency_score × 0.7)
```

### Priority Thresholds
- **Critical**: Score ≥ 15
- **High**: Score 10-15
- **Medium**: Score 5-10
- **Low**: Score < 5

---

## 🔧 Technical Architecture

### New Modules

**`app/queue_engine.py`**
- Time-aware calculations
- Aging logic
- Starvation detection
- Final score calculation
- Queue ranking

**`app/file_uploader.py`**
- CSV/Excel reading
- Column validation
- Data normalization
- Duplicate detection

**`app/queue_state.py`**
- Tracks solved tickets
- Maintains queue history
- Starvation metrics
- Session state management

### Modified Files

**`dashboard.py`**
- CSV/Excel upload UI
- Dynamic queue display
- Solve button functionality
- Real-time recalculation
- Export functionality

---

## 📋 CSV File Format

### Required Columns
```
ticket_id, created_at, customer_tier, product, product_category,
product_criticality, issue_type, channel, current_severity,
sla_target_hours, production_impact, business_impact
```

### Optional Columns
```
sla_breached, reopen_count, customer_contact_count,
affected_users_estimate, security_related, customer_sentiment,
urgency_keywords, waiting_time_hours, status, assigned_team,
previous_escalation, issue_description
```

### Example Row
```csv
ticket_id,created_at,customer_tier,product,issue_type,sla_target_hours,...
TKT-001,2026-09-10T10:00:00,Platinum,Core Platform,Outage,4,...
```

---

## 🧪 Testing Workflow

### Test 1: Upload Variable Row Counts
- Upload 5 tickets ✓
- Upload 100 tickets ✓
- Upload 500 tickets ✓

### Test 2: Time Awareness
- Check ticket age updates with current time ✓
- Verify SLA remaining decreases over time ✓

### Test 3: Aging Logic
- Old ticket (24+ hours) gets boost ✓
- Very old ticket (72+ hours) becomes Critical ✓

### Test 4: Starvation Detection
- Ticket bypassed 5+ times gets boost ✓
- Starvation status displayed ✓

### Test 5: Solve Functionality
- Solve #1 ticket ✓
- Ticket removed from queue ✓
- Remaining tickets re-ranked ✓
- New #1 ticket appears ✓

### Test 6: Queue Recalculation
- After solve, scores update ✓
- Positions adjust dynamically ✓

---

## ⚙️ Configuration

### Aging Thresholds (in `app/queue_engine.py`)
```python
AGING_MEDIUM_THRESHOLD = 24   # hours
AGING_HIGH_THRESHOLD = 48     # hours
AGING_CRITICAL_THRESHOLD = 72 # hours
```

### Starvation Thresholds
```python
STARVATION_BYPASS_THRESHOLD = 5   # times bypassed
STARVATION_AGE_THRESHOLD = 12     # minimum age in hours
```

### SLA Risk Thresholds
```python
SLA_CRITICAL_THRESHOLD = 2  # hours remaining
SLA_HIGH_THRESHOLD = 4      # hours remaining
```

### Score Weights
```python
WEIGHT_ML_PRIORITY = 1.0
WEIGHT_SLA_RISK = 1.5
WEIGHT_IMPACT = 1.2
WEIGHT_AGING = 0.8
WEIGHT_STARVATION = 1.0
WEIGHT_SECURITY = 1.3
WEIGHT_URGENCY = 0.7
```

---

## 🎓 Key Concepts

### ML Priority vs Final Priority

**ML Priority**: Base prediction from trained model
- Uses historical patterns
- Static at prediction time

**Final Priority**: Dynamic priority after adjustments
- ML Priority + Time factors + Business rules
- Updates with time and queue changes

### Aging vs Starvation

**Aging**: Ticket has been waiting for a long time
- Based purely on ticket age
- Gradual priority increase

**Starvation**: Ticket repeatedly bypassed
- Based on queue position history
- Triggered when other tickets keep jumping ahead

### Human-in-the-Loop

- AI **recommends** next ticket to solve
- Human engineer **decides** to solve
- Engineer clicks "Solve" after actual resolution
- System assists, humans retain control

---

## 🔄 Workflow Example

1. **Upload**: Engineer uploads today's 50 tickets
2. **Analysis**: System runs ML predictions
3. **Scoring**: Dynamic scores calculated (SLA, aging, impact)
4. **Ranking**: Tickets sorted by final score
5. **Display**: #1 ticket shown: "TKT-2045 - Critical - SLA 1.2h remaining"
6. **Solve**: Engineer resolves issue, clicks "Solve"
7. **Recalculate**: Queue updates, new #1 appears
8. **Repeat**: Continue until all critical tickets handled

---

## 📌 Important Notes

- **Training data**: Historical 1000 tickets in Supabase
- **Uploaded data**: NEW current tickets (not for retraining)
- **Model reuse**: Same trained model, different inference data
- **Time**: Always uses actual current datetime
- **Row count**: NO hardcoded limits (5 to 10,000+ supported)

---

## 🚨 Troubleshooting

### "Missing required columns" error
- Check your CSV has all required columns
- Download template from sidebar

### "TypeError: tz-aware datetime" error
- Fixed in queue_engine.py
- System handles timezone differences automatically

### "AttributeError: dict/int" error
- Fixed with defensive queue_history handling
- System converts old integer values to dict format

### Dashboard not loading
```bash
# Restart dashboard
streamlit run dashboard.py
```

---

## 📦 Dependencies

New packages installed:
- `openpyxl` - Excel .xlsx support
- `xlrd` - Excel .xls support

Existing packages:
- `streamlit` - Dashboard
- `pandas` - Data processing
- `scikit-learn` - ML model
- `plotly` - Charts

---

## 🎉 Success Criteria

✅ CSV/Excel upload works for any row count
✅ Time-aware calculations use actual current time
✅ Aging logic boosts old tickets
✅ Starvation detection identifies bypassed tickets
✅ Solve button removes tickets and recalculates queue
✅ Next ticket recommendation prominently displayed
✅ Export functionality works
✅ All existing ML model functionality preserved
✅ Supabase integration still works
✅ FastAPI backend unchanged

---

## 📚 Files Modified Summary

| File | Changes |
|------|---------|
| `app/queue_engine.py` | Time-aware scoring, aging, starvation logic |
| `app/file_uploader.py` | CSV/Excel upload and validation |
| `app/queue_state.py` | Solved ticket tracking, queue history |
| `dashboard.py` | Upload UI, queue view, solve buttons |
| `requirements.txt` | Added openpyxl, xlrd |

---

**System Status**: ✅ Fully Operational

**Dashboard**: http://localhost:8501

**Next Steps**: Upload your CSV and start prioritizing! 🚀

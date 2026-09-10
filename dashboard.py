"""
Dynamic Time-Aware Queue Dashboard for CustomerPulse AI
CSV/Excel Upload → ML Prediction → Dynamic Queue → Solve Functionality
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import pickle
from io import BytesIO

# Import new modules
from app.file_uploader import FileUploader, FileUploadError
from app.queue_engine import QueueEngine, QueueConfig
from app.queue_state import QueueState
from app.priority_engine import PriorityEngine

load_dotenv()

# Simple page config
st.set_page_config(
    page_title="CustomerPulse AI - Dynamic Queue",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'queue_state' not in st.session_state:
    st.session_state.queue_state = QueueState()

if 'uploaded_tickets' not in st.session_state:
    st.session_state.uploaded_tickets = None

if 'ranked_queue' not in st.session_state:
    st.session_state.ranked_queue = None

if 'last_recalculation' not in st.session_state:
    st.session_state.last_recalculation = None

# Dark theme CSS
st.markdown("""
<style>
    /* Dark background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Headers - White text */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Metric labels and text */
    [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Sidebar dark */
    [data-testid="stSidebar"] {
        background-color: #1a1d24;
    }
    
    /* Text color white */
    p, label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Priority badges */
    .priority-badge {
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        font-size: 1.2rem;
    }
    .critical { background-color: #e74c3c; color: white; }
    .high { background-color: #f39c12; color: white; }
    .medium { background-color: #f1c40f; color: black; }
    .low { background-color: #27ae60; color: white; }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        color: white !important;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #1e293b;
        color: white;
    }
    
    /* Divider */
    hr {
        border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_supabase():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@st.cache_data(ttl=300)
def load_tickets_data():
    try:
        supabase = init_supabase()
        response = supabase.table("tickets").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading tickets: {e}")
        return pd.DataFrame()


@st.cache_resource
def load_priority_model():
    """Load the trained ML model"""
    try:
        with open('model/priority_model.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None


@st.cache_resource
def init_queue_engine():
    """Initialize queue engine"""
    return QueueEngine()


@st.cache_resource
def init_file_uploader():
    """Initialize file uploader"""
    return FileUploader()


def process_tickets_through_pipeline(df: pd.DataFrame, ml_model, queue_engine: QueueEngine, 
                                     queue_state: QueueState) -> pd.DataFrame:
    """
    Process tickets through complete pipeline:
    1. ML prediction
    2. Dynamic time-aware scoring
    3. Aging logic
    4. Starvation detection
    5. Final ranking
    
    Args:
        df: DataFrame with ticket data
        ml_model: Trained ML model
        queue_engine: Queue engine instance
        queue_state: Queue state instance
        
    Returns:
        DataFrame with predictions and scores
    """
    results = []
    current_time = datetime.now()
    
    # Get starvation data from queue state
    starvation_data = queue_state.get_starvation_data()
    
    # Register tickets as active
    ticket_ids = df['ticket_id'].tolist()
    queue_state.add_active_tickets(ticket_ids)
    
    # Process each ticket
    for idx, row in df.iterrows():
        ticket_dict = row.to_dict()
        
        # Skip if already solved
        if queue_state.is_solved(ticket_dict['ticket_id']):
            continue
        
        # Step 1: ML Prediction
        try:
            # Preprocess and predict
            processed = preprocess_ticket_for_prediction(ticket_dict)
            df_single = pd.DataFrame([processed])
            ml_priority = ml_model.predict(df_single)[0]
            
            try:
                proba = ml_model.predict_proba(df_single)[0]
                class_labels = ml_model.named_steps['classifier'].classes_
                priority_idx = list(class_labels).index(ml_priority)
                ml_confidence = float(proba[priority_idx])
            except:
                ml_confidence = None
        except Exception as e:
            ml_priority = 'Medium'
            ml_confidence = None
        
        # Step 2: Dynamic queue scoring
        # Build proper queue_history structure for this ticket
        ticket_id = ticket_dict['ticket_id']
        ticket_queue_history = {
            ticket_id: {
                'times_bypassed': starvation_data.get(ticket_id, {}).get('times_bypassed', 0) if isinstance(starvation_data.get(ticket_id), dict) else starvation_data.get(ticket_id, 0),
                'last_position': None,
                'last_considered_at': None
            }
        }
        
        queue_result = queue_engine.calculate_final_score(
            ticket_dict,
            ml_priority,
            current_time,
            queue_history=ticket_queue_history
        )
        
        # Combine all data
        result = {
            **ticket_dict,
            'ml_priority': ml_priority,
            'ml_confidence': ml_confidence,
            'final_priority': queue_result['final_priority'],
            'final_score': queue_result['final_score'],
            'ticket_age_hours': queue_result.get('ticket_age_hours', 0),
            'sla_remaining_hours': queue_result.get('sla_remaining_hours', 0),
            'sla_status': queue_result.get('sla_status', 'OK'),
            'aging_status': queue_result.get('aging_status', 'NONE'),
            'aging_boost': queue_result.get('aging_boost', 0),
            'starvation_status': queue_result.get('starvation_status', 'NONE'),
            'starvation_boost': queue_result.get('starvation_boost', 0),
            'reasons': queue_result.get('reasons', []),
            'breakdown': queue_result.get('breakdown', {}),
            'status': 'ACTIVE'
        }
        
        results.append(result)
    
    # Create DataFrame and rank
    results_df = pd.DataFrame(results)
    
    if len(results_df) > 0:
        # Rank by final score
        results_df = results_df.sort_values('final_score', ascending=False).reset_index(drop=True)
        results_df['queue_position'] = range(1, len(results_df) + 1)
        
        # Update queue state with positions
        ranked_tickets = results_df.to_dict('records')
        queue_state.update_queue_positions(ranked_tickets)
    
    return results_df


def preprocess_ticket_for_prediction(ticket_data):
    processed = ticket_data.copy()
    
    # Convert Yes/No to 1/0
    boolean_columns = ["sla_breached", "security_related", "previous_escalation"]
    for col in boolean_columns:
        if col in processed:
            val = processed[col]
            processed[col] = 1 if (val == "Yes" or val == 1) else 0
    
    # Convert numerical columns
    numerical_cols = [
        "sla_target_hours", "sla_remaining_hours", "reopen_count",
        "customer_contact_count", "affected_users_estimate", "waiting_time_hours"
    ]
    for col in numerical_cols:
        if col in processed:
            try:
                processed[col] = float(processed[col]) if processed[col] is not None else 0.0
            except:
                processed[col] = 0.0
    
    # Convert categorical columns
    categorical_cols = [
        "customer_tier", "product", "product_category", "product_criticality",
        "issue_type", "channel", "current_severity", "production_impact",
        "business_impact", "customer_sentiment", "urgency_keywords",
        "status", "assigned_team"
    ]
    for col in categorical_cols:
        if col in processed:
            processed[col] = str(processed[col]) if processed[col] is not None else "Unknown"
    
    return processed


def generate_explanation(ticket_data, predicted_priority):
    reasons = []
    
    if ticket_data.get('production_impact', '') in ['Major', 'Critical', 'Severe']:
        reasons.append(f"High production impact: {ticket_data.get('production_impact')}")
    
    if ticket_data.get('business_impact', '') in ['High', 'Critical']:
        reasons.append(f"High business impact: {ticket_data.get('business_impact')}")
    
    sla_remaining = ticket_data.get('sla_remaining_hours', 999)
    if ticket_data.get('sla_breached') in [1, 'Yes']:
        reasons.append("SLA has been breached")
    elif sla_remaining < 2:
        reasons.append(f"SLA at risk: only {sla_remaining:.1f} hours remaining")
    
    affected_users = ticket_data.get('affected_users_estimate', 0)
    if affected_users >= 1000:
        reasons.append(f"Large user impact: {affected_users:,} users affected")
    
    if ticket_data.get('customer_tier', '') in ['Platinum', 'Enterprise', 'Premium']:
        reasons.append(f"{ticket_data.get('customer_tier')} tier customer")
    
    if ticket_data.get('security_related') in [1, 'Yes']:
        reasons.append("Security-related issue")
    
    if ticket_data.get('current_severity', '') in ['Critical', 'Urgent', 'High', 'Sev-4']:
        reasons.append(f"High severity: {ticket_data.get('current_severity')}")
    
    if not reasons:
        reasons.append("Standard priority indicators")
    
    return reasons[:5]


def predict_priority(model, ticket):
    try:
        processed_ticket = preprocess_ticket_for_prediction(ticket)
        df = pd.DataFrame([processed_ticket])
        
        predicted_priority = model.predict(df)[0]
        
        confidence = None
        try:
            proba = model.predict_proba(df)[0]
            class_labels = model.named_steps['classifier'].classes_
            priority_idx = list(class_labels).index(predicted_priority)
            confidence = float(proba[priority_idx])
        except:
            pass
        
        reasons = generate_explanation(ticket, predicted_priority)
        
        return {
            'predicted_priority': predicted_priority,
            'confidence': confidence,
            'reasons': reasons
        }
    except Exception as e:
        return {
            'error': str(e),
            'predicted_priority': 'Error',
            'confidence': None,
            'reasons': [f"Prediction failed: {str(e)}"]
        }


def main():
    # Header
    st.title("🎯 CustomerPulse AI - Dynamic Queue")
    st.markdown("**Time-Aware AI Ticket Prioritization with Aging & Starvation Detection**")
    st.divider()
    
    # Load resources
    priority_model = load_priority_model()
    queue_engine = init_queue_engine()
    file_uploader = init_file_uploader()
    
    # Sidebar
    with st.sidebar:
        st.header("📂 Upload Tickets")
        
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file with ticket data"
        )
        
        if uploaded_file:
            if st.button("Process File", type="primary"):
                try:
                    with st.spinner("Processing file..."):
                        # Process file
                        df, info = file_uploader.process_uploaded_file(uploaded_file)
                        
                        st.success(f"✓ Processed {info['processed_rows']} tickets")
                        
                        if info['has_duplicates']:
                            st.warning(f"⚠ Found {len(info['duplicate_ids'])} duplicate ticket IDs")
                        
                        # Process through pipeline
                        if priority_model:
                            ranked_df = process_tickets_through_pipeline(
                                df, priority_model, queue_engine, st.session_state.queue_state
                            )
                            st.session_state.uploaded_tickets = df
                            st.session_state.ranked_queue = ranked_df
                            st.session_state.last_recalculation = datetime.now()
                            st.rerun()
                        else:
                            st.error("ML model not loaded. Train model first.")
                except FileUploadError as e:
                    st.error(f"Upload Error:\n{str(e)}")
                except Exception as e:
                    st.error(f"Processing Error: {str(e)}")
        
        st.divider()
        
        # Download template
        if st.button("📥 Download Template"):
            template = file_uploader.get_column_template()
            csv = template.to_csv(index=False)
            st.download_button(
                "Download CSV Template",
                csv,
                "ticket_template.csv",
                "text/csv"
            )
        
        st.divider()
        
        # Stats
        stats = st.session_state.queue_state.get_statistics()
        st.metric("Active Tickets", stats['total_active'])
        st.metric("Solved Tickets", stats['total_solved'])
        
        if st.session_state.last_recalculation:
            st.caption(f"Last updated: {st.session_state.last_recalculation.strftime('%H:%M:%S')}")
        
        # Reset button
        if st.button("🔄 Reset Queue"):
            st.session_state.queue_state.reset()
            st.session_state.uploaded_tickets = None
            st.session_state.ranked_queue = None
            st.rerun()
    
    # Main content
    if st.session_state.ranked_queue is None or len(st.session_state.ranked_queue) == 0:
        st.info("👆 Upload a CSV or Excel file to start prioritizing tickets")
        
        # Show example or load from Supabase
        st.subheader("Or view historical data from Supabase")
        if st.button("Load Historical Tickets"):
            df = load_tickets_data()
            if not df.empty:
                st.session_state.uploaded_tickets = df
                if priority_model:
                    ranked_df = process_tickets_through_pipeline(
                        df.head(100), priority_model, queue_engine, st.session_state.queue_state
                    )
                    st.session_state.ranked_queue = ranked_df
                    st.session_state.last_recalculation = datetime.now()
                    st.rerun()
        return
    
    # Active queue
    queue_df = st.session_state.ranked_queue
    
    # Filter active only
    active_df = queue_df[queue_df['status'] == 'ACTIVE'].copy()
    
    # NEXT TICKET TO SOLVE - Prominent display
    if len(active_df) > 0:
        next_ticket = active_df.iloc[0]
        
        st.markdown("## 🎯 NEXT TICKET TO SOLVE")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            priority_color = {'Critical': '#e74c3c', 'High': '#f39c12', 'Medium': '#f1c40f', 'Low': '#27ae60'}
            color = priority_color.get(next_ticket['final_priority'], '#95a5a6')
            
            st.markdown(f"""
            <div style='background-color: {color}; padding: 20px; border-radius: 10px; color: white;'>
                <h2 style='margin:0; color: white;'>{next_ticket['ticket_id']}</h2>
                <h3 style='margin:0; color: white;'>{next_ticket['final_priority']} Priority</h3>
                <p style='margin:5px 0; color: white;'>Score: {next_ticket['final_score']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Key Metrics:**")
            st.write(f"🕐 Age: {next_ticket['ticket_age_hours']:.1f} hours")
            st.write(f"⏰ SLA: {next_ticket['sla_remaining_hours']:.1f}h ({next_ticket['sla_status']})")
            st.write(f"👤 {next_ticket['customer_tier']} | {next_ticket['product']}")
            st.write(f"📊 ML: {next_ticket['ml_priority']} → Final: {next_ticket['final_priority']}")
        
        with col3:
            st.markdown("**Status:**")
            if next_ticket['aging_status'] != 'NONE':
                st.write(f"⏳ Aging: {next_ticket['aging_status']}")
            if next_ticket['starvation_status'] != 'NONE':
                st.write(f"🚨 Starvation: {next_ticket['starvation_status']}")
            
            if st.button("✅ SOLVE THIS TICKET", type="primary", key="solve_next"):
                st.session_state.queue_state.solve_ticket(
                    next_ticket['ticket_id'],
                    solved_by="Engineer",
                    queue_position=1
                )
                # Recalculate queue
                remaining_df = active_df[active_df['ticket_id'] != next_ticket['ticket_id']]
                if len(remaining_df) > 0:
                    st.session_state.ranked_queue = process_tickets_through_pipeline(
                        remaining_df, priority_model, queue_engine, st.session_state.queue_state
                    )
                st.session_state.last_recalculation = datetime.now()
                st.success(f"✓ Solved {next_ticket['ticket_id']}")
                st.rerun()
        
        # Reasons
        st.markdown("**Why this ticket is #1:**")
        for reason in next_ticket['reasons'][:5]:
            st.write(f"• {reason}")
        
        st.divider()
    
    # Metrics
    st.subheader("Queue Overview")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    col1.metric("Total", len(active_df))
    col2.metric("🔴 Critical", len(active_df[active_df['final_priority'] == 'Critical']))
    col3.metric("🟠 High", len(active_df[active_df['final_priority'] == 'High']))
    col4.metric("🟡 Medium", len(active_df[active_df['final_priority'] == 'Medium']))
    col5.metric("🟢 Low", len(active_df[active_df['final_priority'] == 'Low']))
    col6.metric("⚠️ SLA Risk", len(active_df[active_df['sla_status'].isin(['BREACHED', 'CRITICAL_RISK'])]))
    
    st.divider()
    
    # Queue Table
    st.subheader("Active Queue")
    
    # Display controls
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_priority = st.multiselect("Filter Priority", ['Critical', 'High', 'Medium', 'Low'], default=['Critical', 'High', 'Medium', 'Low'])
    with col2:
        filter_sla = st.multiselect("Filter SLA Status", ['BREACHED', 'CRITICAL_RISK', 'HIGH_RISK', 'OK'], default=['BREACHED', 'CRITICAL_RISK', 'HIGH_RISK', 'OK'])
    with col3:
        show_top_n = st.slider("Show top N tickets", 5, 100, 20)
    
    # Apply filters
    display_df = active_df[
        (active_df['final_priority'].isin(filter_priority)) &
        (active_df['sla_status'].isin(filter_sla))
    ].head(show_top_n)
    
    # Display queue
    for idx, ticket in display_df.iterrows():
        with st.expander(f"#{ticket['queue_position']} | {ticket['ticket_id']} | {ticket['final_priority']} | Score: {ticket['final_score']:.2f}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown("**Ticket Info:**")
                st.write(f"Customer: {ticket['customer_tier']}")
                st.write(f"Product: {ticket['product']}")
                st.write(f"Issue: {ticket['issue_type']}")
                st.write(f"Severity: {ticket['current_severity']}")
                st.write(f"Impact: {ticket['production_impact']} / {ticket['business_impact']}")
            
            with col2:
                st.markdown("**Time & Priority:**")
                st.write(f"Age: {ticket['ticket_age_hours']:.1f} hours")
                st.write(f"SLA Remaining: {ticket['sla_remaining_hours']:.1f}h")
                st.write(f"SLA Status: {ticket['sla_status']}")
                st.write(f"ML Priority: {ticket['ml_priority']}")
                st.write(f"Final Priority: {ticket['final_priority']}")
                st.write(f"Aging: {ticket['aging_status']}")
                st.write(f"Starvation: {ticket['starvation_status']}")
            
            with col3:
                st.markdown("**Actions:**")
                if st.button(f"✅ Solve", key=f"solve_{ticket['ticket_id']}"):
                    st.session_state.queue_state.solve_ticket(
                        ticket['ticket_id'],
                        solved_by="Engineer",
                        queue_position=ticket['queue_position']
                    )
                    remaining_df = active_df[active_df['ticket_id'] != ticket['ticket_id']]
                    if len(remaining_df) > 0:
                        st.session_state.ranked_queue = process_tickets_through_pipeline(
                            remaining_df, priority_model, queue_engine, st.session_state.queue_state
                        )
                    st.session_state.last_recalculation = datetime.now()
                    st.rerun()
            
            st.markdown("**Reasons:**")
            for reason in ticket['reasons'][:5]:
                st.write(f"• {reason}")
    
    st.divider()
    
    # Export
    st.subheader("📤 Export Queue")
    if st.button("Download Queue as CSV"):
        csv = active_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv"
        )
    
    # Footer
    st.divider()
    st.caption("CustomerPulse AI - Dynamic Time-Aware Queue System")
    st.caption("Human-in-the-loop: AI recommends, humans decide")


if __name__ == "__main__":
    main()

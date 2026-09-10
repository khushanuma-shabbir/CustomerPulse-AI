"""
Streamlit Dashboard for CustomerPulse AI
Enterprise-grade support ticket analytics and priority visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.supabase_client import supabase
from app.priority_engine import PriorityEngine

# Page configuration
st.set_page_config(
    page_title="CustomerPulse AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
    }
    .priority-critical {
        color: #dc2626;
        font-weight: 600;
    }
    .priority-high {
        color: #ea580c;
        font-weight: 600;
    }
    .priority-medium {
        color: #ca8a04;
        font-weight: 600;
    }
    .priority-low {
        color: #16a34a;
        font-weight: 600;
    }
    .ticket-card {
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    .reason-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background: #f3f4f6;
        border-radius: 0.25rem;
        border-left: 3px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_tickets_data():
    """Load tickets from Supabase with caching"""
    try:
        response = supabase.table("tickets").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading tickets: {e}")
        return pd.DataFrame()


@st.cache_resource
def load_priority_engine():
    """Load priority prediction engine"""
    try:
        engine = PriorityEngine()
        return engine
    except Exception as e:
        st.warning(f"Priority engine not available: {e}")
        return None


def display_metric_card(label, value, delta=None, delta_color="normal"):
    """Display a metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def get_priority_color(priority):
    """Get color for priority level"""
    colors = {
        "Critical": "#dc2626",
        "High": "#ea580c",
        "Medium": "#ca8a04",
        "Low": "#16a34a"
    }
    return colors.get(priority, "#6b7280")


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<div class="main-header">🎯 CustomerPulse AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Customer Support Ticket Prioritization & Analysis</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Load data
    df = load_tickets_data()
    
    if df.empty:
        st.error("No ticket data available. Please check database connection.")
        return
    
    # Load priority engine
    priority_engine = load_priority_engine()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Filters")
        
        # Priority filter
        priorities = ["All"] + sorted(df["ground_truth_priority"].unique().tolist())
        selected_priority = st.selectbox("Priority", priorities)
        
        # Status filter
        if "status" in df.columns:
            statuses = ["All"] + sorted(df["status"].unique().tolist())
            selected_status = st.selectbox("Status", statuses)
        else:
            selected_status = "All"
        
        # Customer tier filter
        if "customer_tier" in df.columns:
            tiers = ["All"] + sorted(df["customer_tier"].unique().tolist())
            selected_tier = st.selectbox("Customer Tier", tiers)
        else:
            selected_tier = "All"
        
        # SLA filter
        show_sla_breach = st.checkbox("Show only SLA breached", False)
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Tickets", len(df))
        
        if priority_engine:
            st.success("✓ AI Model Active")
        else:
            st.warning("⚠ AI Model Not Loaded")
    
    # Apply filters
    filtered_df = df.copy()
    if selected_priority != "All":
        filtered_df = filtered_df[filtered_df["ground_truth_priority"] == selected_priority]
    if selected_status != "All" and "status" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
    if selected_tier != "All" and "customer_tier" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["customer_tier"] == selected_tier]
    if show_sla_breach and "sla_breached" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["sla_breached"] == "Yes"]
    
    # Main metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📋 Total Tickets",
            value=len(filtered_df),
            delta=None
        )
    
    with col2:
        critical_count = len(filtered_df[filtered_df["ground_truth_priority"] == "Critical"])
        st.metric(
            label="🔴 Critical",
            value=critical_count,
            delta=f"{critical_count/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%"
        )
    
    with col3:
        high_count = len(filtered_df[filtered_df["ground_truth_priority"] == "High"])
        st.metric(
            label="🟠 High",
            value=high_count,
            delta=f"{high_count/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%"
        )
    
    with col4:
        medium_count = len(filtered_df[filtered_df["ground_truth_priority"] == "Medium"])
        st.metric(
            label="🟡 Medium",
            value=medium_count,
            delta=f"{medium_count/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%"
        )
    
    with col5:
        low_count = len(filtered_df[filtered_df["ground_truth_priority"] == "Low"])
        st.metric(
            label="🟢 Low",
            value=low_count,
            delta=f"{low_count/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%"
        )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Priority Distribution")
        priority_counts = filtered_df["ground_truth_priority"].value_counts()
        fig_priority = go.Figure(data=[go.Pie(
            labels=priority_counts.index,
            values=priority_counts.values,
            hole=0.4,
            marker=dict(colors=[
                get_priority_color(p) for p in priority_counts.index
            ])
        )])
        fig_priority.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        st.subheader("📈 Production Impact Analysis")
        if "production_impact" in filtered_df.columns:
            impact_counts = filtered_df["production_impact"].value_counts()
            fig_impact = px.bar(
                x=impact_counts.index,
                y=impact_counts.values,
                labels={"x": "Production Impact", "y": "Count"},
                color=impact_counts.values,
                color_continuous_scale="Reds"
            )
            fig_impact.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_impact, use_container_width=True)
        else:
            st.info("Production impact data not available")
    
    st.markdown("---")
    
    # Additional insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("⏰ SLA Status")
        if "sla_breached" in filtered_df.columns:
            sla_breached = len(filtered_df[filtered_df["sla_breached"] == "Yes"])
            sla_ok = len(filtered_df[filtered_df["sla_breached"] == "No"])
            
            fig_sla = go.Figure(data=[go.Bar(
                x=["SLA OK", "SLA Breached"],
                y=[sla_ok, sla_breached],
                marker_color=["#16a34a", "#dc2626"]
            )])
            fig_sla.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig_sla, use_container_width=True)
    
    with col2:
        st.subheader("👥 Customer Tiers")
        if "customer_tier" in filtered_df.columns:
            tier_counts = filtered_df["customer_tier"].value_counts()
            fig_tier = px.pie(
                names=tier_counts.index,
                values=tier_counts.values,
                hole=0.3
            )
            fig_tier.update_layout(height=250)
            st.plotly_chart(fig_tier, use_container_width=True)
    
    with col3:
        st.subheader("🔒 Security Issues")
        if "security_related" in filtered_df.columns:
            security_yes = len(filtered_df[filtered_df["security_related"] == "Yes"])
            security_no = len(filtered_df[filtered_df["security_related"] == "No"])
            
            fig_security = go.Figure(data=[go.Bar(
                x=["Non-Security", "Security"],
                y=[security_no, security_yes],
                marker_color=["#3b82f6", "#dc2626"]
            )])
            fig_security.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig_security, use_container_width=True)
    
    st.markdown("---")
    
    # Ticket list and AI prediction section
    st.subheader("🎫 Ticket Details & AI Predictions")
    
    # Search
    search_query = st.text_input("🔍 Search tickets by ID or description", "")
    
    # Filter by search
    display_df = filtered_df.copy()
    if search_query:
        display_df = display_df[
            display_df["ticket_id"].str.contains(search_query, case=False, na=False) |
            display_df["issue_description"].str.contains(search_query, case=False, na=False)
        ]
    
    # Sort by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    display_df["priority_rank"] = display_df["ground_truth_priority"].map(priority_order)
    display_df = display_df.sort_values("priority_rank").head(20)
    
    # Display tickets
    if len(display_df) == 0:
        st.info("No tickets match your search criteria")
    else:
        for idx, ticket in display_df.iterrows():
            with st.expander(
                f"🎫 {ticket['ticket_id']} | Priority: {ticket['ground_truth_priority']} | "
                f"Customer: {ticket.get('customer_tier', 'N/A')}"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Issue Description:**")
                    st.write(ticket.get('issue_description', 'No description')[:500])
                    
                    st.markdown("**Ticket Details:**")
                    st.write(f"• Product: {ticket.get('product', 'N/A')}")
                    st.write(f"• Issue Type: {ticket.get('issue_type', 'N/A')}")
                    st.write(f"• Current Severity: {ticket.get('current_severity', 'N/A')}")
                    st.write(f"• Production Impact: {ticket.get('production_impact', 'N/A')}")
                    st.write(f"• Affected Users: {ticket.get('affected_users_estimate', 0)}")
                    st.write(f"• SLA Remaining: {ticket.get('sla_remaining_hours', 0):.1f} hours")
                
                with col2:
                    st.markdown("**Ground Truth Priority:**")
                    priority = ticket['ground_truth_priority']
                    st.markdown(
                        f'<div style="background-color: {get_priority_color(priority)}; '
                        f'color: white; padding: 10px; border-radius: 5px; text-align: center; '
                        f'font-size: 1.2rem; font-weight: 600;">{priority}</div>',
                        unsafe_allow_html=True
                    )
                    
                    # AI Prediction
                    if priority_engine:
                        st.markdown("---")
                        st.markdown("**🤖 AI Prediction:**")
                        
                        if st.button(f"Generate AI Prediction", key=f"predict_{ticket['ticket_id']}"):
                            with st.spinner("Analyzing ticket..."):
                                try:
                                    prediction = priority_engine.predict_priority(ticket.to_dict())
                                    
                                    pred_priority = prediction['predicted_priority']
                                    st.markdown(
                                        f'<div style="background-color: {get_priority_color(pred_priority)}; '
                                        f'color: white; padding: 8px; border-radius: 5px; text-align: center; '
                                        f'font-weight: 600;">{pred_priority}</div>',
                                        unsafe_allow_html=True
                                    )
                                    
                                    if prediction['confidence']:
                                        st.progress(prediction['confidence'])
                                        st.caption(f"Confidence: {prediction['confidence']:.1%}")
                                    
                                    st.markdown("**Reasons:**")
                                    for reason in prediction['reasons']:
                                        st.markdown(f"• {reason}")
                                    
                                    # Match indicator
                                    if pred_priority == priority:
                                        st.success("✓ AI prediction matches ground truth")
                                    else:
                                        st.warning(f"⚠ AI predicted {pred_priority}, actual is {priority}")
                                    
                                except Exception as e:
                                    st.error(f"Prediction failed: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #6b7280; padding: 2rem;">'
        '<p><strong>CustomerPulse AI</strong> - AI-Assisted Support Ticket Prioritization</p>'
        '<p style="font-size: 0.9rem;">Human-in-the-loop approach: AI assists, humans decide</p>'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

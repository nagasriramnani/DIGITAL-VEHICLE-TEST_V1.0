"""
Streamlit Dashboard for Virtual Testing Assistant.
Interactive UI for test recommendations, ROI analysis, and governance reporting.
"""
import streamlit as st
import json
import requests
import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Virtual Testing Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration - use environment variable or secrets, with fallback
API_BASE_URL = os.getenv("API_BASE_URL", None)

# Try to get from Streamlit secrets if not in environment variable
if API_BASE_URL is None:
    try:
        # Try to access secrets - this may raise StreamlitSecretNotFoundError
        # if secrets.toml doesn't exist
        from streamlit.errors import StreamlitSecretNotFoundError
        try:
            API_BASE_URL = st.secrets.get("API_BASE_URL", None)
        except StreamlitSecretNotFoundError:
            # Secrets file not found, will use default
            API_BASE_URL = None
    except (ImportError, AttributeError, Exception):
        # If secrets not available or can't import, use default
        API_BASE_URL = None

# Final fallback to default
if API_BASE_URL is None:
    API_BASE_URL = "http://localhost:8000"

# Custom CSS - ChatGPT Theme (External CSS)
# Load ChatGPT-style CSS from external file
css_file = Path(__file__).parent / "chatgpt_theme.css"
if css_file.exists():
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
else:
    # Fallback inline CSS if file not found
    st.markdown("""
    <style>
        .stApp { background: #343541 !important; color: #ececf1 !important; }
        [data-testid="stSidebar"] { background: #202123 !important; }
        h1, h2, h3 { color: #ececf1 !important; }
        .stButton > button { background: #10a37f !important; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# Helper Functions
# ============================================================================

# ChatGPT-style color palette for charts
CHATGPT_COLORS = {
    'primary': '#10a37f',      # ChatGPT green
    'secondary': '#3b82f6',    # Blue
    'accent': '#8b5cf6',       # Purple
    'accent2': '#06b6d4',      # Cyan
    'accent3': '#f59e0b',      # Amber
    'accent4': '#ef4444',      # Red
    'palette': ['#10a37f', '#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444']
}

def apply_chatgpt_theme(fig):
    """Apply ChatGPT dark theme to Plotly figure."""
    fig.update_layout(
        plot_bgcolor='#40414f',
        paper_bgcolor='#40414f',
        font=dict(color='#ececf1', family='sans-serif', size=12),
        title_font=dict(color='#ececf1', size=18, family='sans-serif'),
        xaxis=dict(
            gridcolor='rgba(142, 142, 160, 0.2)',
            linecolor='rgba(142, 142, 160, 0.3)',
            title_font=dict(color='#ececf1', size=13),
            tickfont=dict(color='#8e8ea0')
        ),
        yaxis=dict(
            gridcolor='rgba(142, 142, 160, 0.2)',
            linecolor='rgba(142, 142, 160, 0.3)',
            title_font=dict(color='#ececf1', size=13),
            tickfont=dict(color='#8e8ea0')
        ),
        legend=dict(
            bgcolor='rgba(64, 65, 79, 0.8)',
            bordercolor='rgba(142, 142, 160, 0.3)',
            borderwidth=1,
            font=dict(color='#ececf1', size=11)
        )
    )
    return fig

# Alias for backward compatibility
FUTURE_COLORS = CHATGPT_COLORS
apply_futuristic_theme = apply_chatgpt_theme

@st.cache_data(ttl=300)
def load_scenarios():
    """Load test scenarios from file."""
    try:
        scenarios_file = Path("src/data/test_scenarios.json")
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('scenarios', [])
    except Exception as e:
        st.error(f"Error loading scenarios: {e}")
        return []


def get_api_health():
    """Check API health."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    # Logo/Image - removed placeholder URL to avoid loading issues
    # You can add a local image file here if needed:
    # st.image("assets/logo.png", use_container_width=True)
    st.title("🚗 Virtual Testing Assistant")
    
    # API Status
    health = get_api_health()
    if health:
        st.success("✅ API Connected")
    else:
        st.warning("⚠️ API Offline (Using local mode)")
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🎯 Recommendations",
            "💰 ROI Analysis",
            "📊 Metrics",
            "🏢 Governance",
            "🚀 Simulation Export",
            "📋 Scenarios"
        ]
    )
    
    st.divider()
    
    # Quick Stats
    scenarios = load_scenarios()
    if scenarios:
        st.metric("Total Scenarios", len(scenarios))
        st.metric("Avg Cost", f"£{sum(s.get('estimated_cost_gbp', 0) for s in scenarios) / len(scenarios):,.0f}")
        st.metric("Avg Duration", f"{sum(s.get('estimated_duration_hours', 0) for s in scenarios) / len(scenarios):.1f}h")


# ============================================================================
# Main Content
# ============================================================================

if "🏠 Dashboard" in page:
    st.markdown('<div class="main-header">Virtual Testing Assistant Dashboard</div>', unsafe_allow_html=True)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    scenarios = load_scenarios()
    
    with col1:
        st.metric("Total Test Scenarios", len(scenarios))
    
    with col2:
        total_cost = sum(s.get('estimated_cost_gbp', 0) for s in scenarios)
        st.metric("Total Cost", f"£{total_cost/1000:.0f}K")
    
    with col3:
        ev_scenarios = [s for s in scenarios if 'EV' in s.get('applicable_platforms', [])]
        st.metric("EV Scenarios", len(ev_scenarios))
    
    with col4:
        cert_scenarios = [s for s in scenarios if s.get('certification_required', False)]
        st.metric("Certification Tests", len(cert_scenarios))
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Test Distribution by Type")
        
        test_types = {}
        for s in scenarios:
            t = s.get('test_type', 'unknown')
            test_types[t] = test_types.get(t, 0) + 1
        
        fig = px.pie(
            values=list(test_types.values()),
            names=list(test_types.keys()),
            title="Test Types",
            color_discrete_sequence=FUTURE_COLORS['palette']
        )
        fig = apply_futuristic_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚗 Platform Distribution")
        
        platforms = {'EV': 0, 'HEV': 0, 'ICE': 0}
        for s in scenarios:
            for p in s.get('applicable_platforms', []):
                if p in platforms:
                    platforms[p] += 1
        
        fig = px.bar(
            x=list(platforms.keys()),
            y=list(platforms.values()),
            title="Scenarios by Platform",
            labels={'x': 'Platform', 'y': 'Count'},
            color=list(platforms.keys()),
            color_discrete_sequence=FUTURE_COLORS['palette'][:3]
        )
        fig = apply_futuristic_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost analysis
    st.subheader("💰 Cost Analysis")
    
    cost_by_type = {}
    for s in scenarios:
        t = s.get('test_type', 'unknown')
        cost_by_type[t] = cost_by_type.get(t, 0) + s.get('estimated_cost_gbp', 0)
    
    df = pd.DataFrame({
        'Test Type': list(cost_by_type.keys()),
        'Total Cost (£)': list(cost_by_type.values())
    })
    
    fig = px.bar(
        df, 
        x='Test Type', 
        y='Total Cost (£)', 
        title="Total Cost by Test Type",
        color='Test Type',
        color_discrete_sequence=FUTURE_COLORS['palette']
    )
    fig = apply_futuristic_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


elif "🎯 Recommendations" in page:
    st.header("🎯 Test Recommendations")
    
    # Tabs: Chat Interface and Traditional Form
    tab1, tab2 = st.tabs(["💬 Ask the VTA", "📋 Traditional Form"])
    
    with tab1:
        st.markdown("""
        <div style='padding: 1rem; background: #40414f; border-radius: 8px; margin-bottom: 1rem;'>
            <h3 style='color: #ececf1; margin: 0 0 0.5rem 0;'>Ask the VTA - Conversational Agent</h3>
            <p style='color: #8e8ea0; margin: 0; font-size: 0.875rem;'>
                Built with LangChain + Local Hugging Face LLM (7B) | Private, offline agent (no data leak)<br>
                <strong>Tools:</strong> Recommender, Duplicate Detector, ROI Calculator
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            if not st.session_state.chat_history:
                st.markdown("""
                <div style='text-align: center; padding: 2rem; color: #8e8ea0;'>
                    <h3 style='color: #ececf1;'>💬 Start a conversation with VTA</h3>
                    <p>Ask me anything about test recommendations, ROI analysis, or metrics!</p>
                </div>
                """, unsafe_allow_html=True)
            
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="chat-avatar user">U</div>
                        <div class="chat-content user">
                            <p class="chat-text">{message["content"]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="chat-avatar assistant">VTA</div>
                        <div class="chat-content assistant">
                            <p class="chat-text">{message["content"]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display recommendations if available
                    if message.get("recommendations"):
                        st.markdown("### 📊 Recommendations")
                        for i, rec in enumerate(message["recommendations"][:5], 1):
                            with st.expander(f"#{i} - {rec.get('test_name', 'Unknown')} (Score: {rec.get('score', 0):.3f})", expanded=(i==1)):
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.write(f"**Test Type**: {rec.get('test_type', 'N/A')}")
                                    st.write(f"**Description**: {rec.get('description', 'N/A')}")
                                with col2:
                                    st.metric("Duration", f"{rec.get('metadata', {}).get('estimated_duration_hours', 0):.1f}h")
                                    st.metric("Cost", f"£{rec.get('metadata', {}).get('estimated_cost_gbp', 0):,.0f}")
                                
                                # Show standards if available
                                if rec.get('metadata', {}).get('applicable_standards'):
                                    st.write("**Standards**: " + ", ".join(rec['metadata']['applicable_standards']))
        
        # Chat input
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask VTA anything...",
                key="chat_input",
                placeholder="Example: Which tests validate Ariya battery safety for UNECE R100?",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send", type="primary", use_container_width=True)
        
        # Process message
        if send_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get response from API
            with st.spinner("VTA is thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/chat",
                        json={"message": user_input},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Add assistant response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": data.get("response", "I apologize, but I couldn't generate a response."),
                            "recommendations": data.get("recommendations"),
                            "tool_used": data.get("tool_used")
                        })
                    else:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Error: {response.status_code} - {response.text}"
                        })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Error connecting to API: {str(e)}"
                    })
            
            # Rerun to show new messages
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        example_queries = [
            "Which tests validate Ariya battery safety for UNECE R100?",
            "Recommend tests for Leaf EV powertrain and battery systems",
            "What's the ROI for optimizing 100 test scenarios?",
            "Show me metrics for our current test suite",
            "Find performance tests for EV platform"
        ]
        
        for query in example_queries:
            if st.button(f"💬 {query}", key=f"example_{hash(query)}", use_container_width=True):
                # Process the example query directly
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": query
                })
                
                # Get response from API
                with st.spinner("VTA is thinking..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/v1/chat",
                            json={"message": query},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Add assistant response to history
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": data.get("response", "I apologize, but I couldn't generate a response."),
                                "recommendations": data.get("recommendations"),
                                "tool_used": data.get("tool_used")
                            })
                        else:
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": f"Error: {response.status_code} - {response.text}"
                            })
                    except Exception as e:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Error connecting to API: {str(e)}"
                        })
                
                # Rerun to show new messages
                st.rerun()
    
    with tab2:
        st.write("Get AI-powered test recommendations using the traditional form.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            vehicle_model = st.selectbox(
                "Vehicle Model",
                ["Ariya", "Leaf", "Qashqai", "X-Trail", "Juke", "Micra"]
            )
            
            platform = st.selectbox(
                "Platform",
                ["EV", "HEV", "ICE"]
            )
        
        with col2:
            systems = st.multiselect(
                "Target Systems",
                ["Powertrain", "Battery", "ADAS", "Chassis", "Thermal", "HVAC"],
                default=["Powertrain", "Battery"]
            )
            
            components = st.multiselect(
                "Target Components",
                ["High_Voltage_Battery", "Electric_Motor", "Battery_Management_System", "Inverter"],
                default=["High_Voltage_Battery"]
            )
        
        top_k = st.slider("Number of Recommendations", 1, 20, 10)
        
        if st.button("🚀 Get Recommendations", type="primary"):
            with st.spinner("Generating recommendations..."):
                # Load scenarios
                scenarios = load_scenarios()
                
                # Create recommender
                from src.ai.recommender import create_recommender
                recommender = create_recommender()
                
                # Get recommendations
                recommendations = recommender.recommend_for_vehicle(
                    vehicle_model=vehicle_model,
                    platform=platform,
                    systems=systems,
                    components=components,
                    candidates=scenarios,
                    top_k=top_k
                )
                
                st.success(f"✅ Found {len(recommendations)} recommendations")
                
                # Display recommendations
                for i, rec in enumerate(recommendations, 1):
                    with st.expander(f"#{i} - {rec['test_name']} (Score: {rec['score']:.3f})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Test Type**: {rec['test_type']}")
                            st.write(f"**Complexity**: {rec['metadata'].get('complexity_score', 'N/A')}")
                            st.write(f"**Risk Level**: {rec['metadata'].get('risk_level', 'N/A')}")
                        
                        with col2:
                            st.metric("Duration", f"{rec['metadata'].get('estimated_duration_hours', 0):.1f}h")
                            st.metric("Cost", f"£{rec['metadata'].get('estimated_cost_gbp', 0):,.0f}")
                        
                        # Explanation
                        explain = rec.get('explain', {})
                        scores = explain.get('scores', {})
                        
                        st.write("**Score Breakdown:**")
                        st.write(f"- Semantic: {scores.get('semantic', 0):.3f}")
                        st.write(f"- Graph: {scores.get('graph', 0):.3f}")
                        st.write(f"- Rules: {scores.get('rules', 0):.3f}")
                        st.write(f"- Historical: {scores.get('historical', 0):.3f}")
                        
                        if explain.get('rules_fired'):
                            st.write("**Rules Fired:**")
                            for rule in explain['rules_fired']:
                                st.write(f"- {rule}")


elif "💰 ROI Analysis" in page:
    st.header("💰 ROI Analysis")
    
    st.write("Calculate return on investment for test optimization.")
    
    scenarios = load_scenarios()
    
    col1, col2 = st.columns(2)
    
    with col1:
        baseline_count = st.number_input("Baseline Test Count", 10, 500, 100)
        implementation_cost = st.number_input("Implementation Cost (£)", 10000, 200000, 50000, step=10000)
    
    with col2:
        optimization_rate = st.slider("Optimization Rate (%)", 10, 50, 25)
        analysis_years = st.slider("Analysis Period (years)", 1, 10, 3)
    
    if st.button("📊 Calculate ROI", type="primary"):
        with st.spinner("Calculating ROI..."):
            # Create calculator
            from src.business.roi_calculator import create_roi_calculator
            calculator = create_roi_calculator()
            
            # Create sample scenarios
            baseline = scenarios[:baseline_count]
            optimized_count = int(baseline_count * (1 - optimization_rate / 100))
            optimized = scenarios[:optimized_count]
            
            # Calculate ROI
            roi_analysis = calculator.calculate_roi(
                baseline_scenarios=baseline,
                optimized_scenarios=optimized,
                duplicates_eliminated=[],
                implementation_cost_gbp=implementation_cost,
                analysis_period_years=analysis_years
            )
            
            # Display results
            st.success("✅ ROI Analysis Complete")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("ROI", f"{roi_analysis.roi_percent:.1f}%")
            
            with col2:
                st.metric("Payback", f"{roi_analysis.payback_period_months:.1f} months")
            
            with col3:
                st.metric("Annual Savings", f"£{roi_analysis.cost_savings_gbp:,.0f}")
            
            with col4:
                st.metric("Tests Eliminated", roi_analysis.tests_eliminated)
            
            # Detailed breakdown
            st.subheader("📊 Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Baseline**")
                st.write(f"- Tests: {roi_analysis.baseline_num_tests}")
                st.write(f"- Cost: £{roi_analysis.baseline_total_cost_gbp:,.0f}")
                st.write(f"- Time: {roi_analysis.baseline_total_time_hours:,.0f} hours")
            
            with col2:
                st.write("**Optimized**")
                st.write(f"- Tests: {roi_analysis.optimized_num_tests}")
                st.write(f"- Cost: £{roi_analysis.optimized_total_cost_gbp:,.0f}")
                st.write(f"- Time: {roi_analysis.optimized_total_time_hours:,.0f} hours")
            
            # Visualizations
            st.subheader("📈 Cost Comparison")
            
            df = pd.DataFrame({
                'Scenario': ['Baseline', 'Optimized'],
                'Cost (£)': [roi_analysis.baseline_total_cost_gbp, roi_analysis.optimized_total_cost_gbp],
                'Tests': [roi_analysis.baseline_num_tests, roi_analysis.optimized_num_tests]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Tests', 
                x=df['Scenario'], 
                y=df['Tests'], 
                yaxis='y', 
                offsetgroup=1,
                marker_color=FUTURE_COLORS['primary']
            ))
            fig.add_trace(go.Bar(
                name='Cost (£)', 
                x=df['Scenario'], 
                y=df['Cost (£)'], 
                yaxis='y2', 
                offsetgroup=2,
                marker_color=FUTURE_COLORS['secondary']
            ))
            
            fig.update_layout(
                title='Baseline vs. Optimized Comparison',
                yaxis=dict(title='Number of Tests'),
                yaxis2=dict(title='Cost (£)', overlaying='y', side='right')
            )
            fig = apply_futuristic_theme(fig)
            st.plotly_chart(fig, use_container_width=True)


elif "📊 Metrics" in page:
    st.header("📊 Test Optimization Metrics")
    
    st.write("Comprehensive metrics tracking for test coverage, efficiency, quality, and compliance.")
    
    scenarios = load_scenarios()
    
    if st.button("🔄 Calculate Metrics", type="primary"):
        with st.spinner("Calculating metrics..."):
            # Create tracker
            from src.business.metrics import create_metrics_tracker
            tracker = create_metrics_tracker()
            
            # Define reference data
            all_components = ['Battery', 'Motor', 'Inverter', 'BMS', 'Charger', 'Thermal']
            all_systems = ['Powertrain', 'Battery', 'ADAS', 'Chassis', 'Thermal']
            all_platforms = ['EV', 'HEV', 'ICE']
            required_standards = ['UNECE_R100', 'ISO_6469', 'SAE_J2929', 'ISO_26262']
            
            # Calculate metrics
            summary = tracker.calculate_all_metrics(
                scenarios=scenarios[:100],  # Use subset for demo
                all_components=all_components,
                all_systems=all_systems,
                all_platforms=all_platforms,
                required_standards=required_standards,
                num_duplicates=5,
                optimization_rate=0.25
            )
            
            st.success("✅ Metrics Calculated")
            
            # Overall score - Enhanced display with custom styling
            score_value = summary.overall_score
            score_percentage = min(100, max(0, score_value))  # Clamp between 0-100 for percentage
            
            # Determine score status and color
            if score_value >= 90:
                score_status = "Excellent"
                score_color = "#10B981"  # Green
                score_gradient = "linear-gradient(135deg, #10B981 0%, #059669 100%)"
            elif score_value >= 75:
                score_status = "Good"
                score_color = "#3B82F6"  # Blue
                score_gradient = "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)"
            elif score_value >= 60:
                score_status = "Fair"
                score_color = "#F59E0B"  # Amber
                score_gradient = "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
            else:
                score_status = "Needs Improvement"
                score_color = "#EF4444"  # Red
                score_gradient = "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)"
            
            # Custom styled overall score card
            st.markdown(f"""
            <div style="
                background: {score_gradient};
                border-radius: 20px;
                padding: 2.5rem;
                margin: 2rem 0;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                text-align: center;
                color: white;
            ">
                <div style="
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    opacity: 0.9;
                    margin-bottom: 1rem;
                ">OVERALL SCORE</div>
                <div style="
                    font-size: 4.5rem;
                    font-weight: 900;
                    line-height: 1;
                    margin: 1rem 0;
                    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                ">{score_value:.1f}</div>
                <div style="
                    font-size: 1.5rem;
                    font-weight: 600;
                    opacity: 0.9;
                    margin-bottom: 1rem;
                ">/ 100</div>
                <div style="
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.2);
                    backdrop-filter: blur(10px);
                    padding: 0.5rem 1.5rem;
                    border-radius: 25px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-top: 1rem;
                ">{score_status}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Metrics breakdown
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Coverage", f"{summary.coverage.overall_coverage_percent:.1f}%")
            
            with col2:
                st.metric("Efficiency", f"{summary.efficiency.efficiency_score:.1f}/100")
            
            with col3:
                st.metric("Quality", f"{summary.quality.pass_rate_percent:.1f}%")
            
            with col4:
                st.metric("Compliance", f"{summary.compliance.compliance_score:.1f}/100")
            
            # Detailed metrics
            st.subheader("🎯 Coverage Metrics")
            
            coverage_df = pd.DataFrame({
                'Dimension': ['Components', 'Systems', 'Platforms', 'Regulatory'],
                'Coverage (%)': [
                    summary.coverage.component_coverage_percent,
                    summary.coverage.system_coverage_percent,
                    summary.coverage.platform_coverage_percent,
                    summary.coverage.regulatory_coverage_percent
                ]
            })
            
            fig = px.bar(
                coverage_df, 
                x='Dimension', 
                y='Coverage (%)', 
                title="Coverage by Dimension",
                color='Dimension',
                color_discrete_sequence=FUTURE_COLORS['palette']
            )
            fig = apply_futuristic_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            
            # Compliance gaps
            if summary.compliance.compliance_gaps:
                st.warning(f"⚠️ Compliance Gaps: {', '.join(summary.compliance.compliance_gaps)}")


elif "🏢 Governance" in page:
    st.header("🏢 KTP Governance")
    
    st.write("Project progress tracking and LMC reporting.")
    
    # Create reporter
    from src.business.governance import create_governance_reporter
    reporter = create_governance_reporter()
    
    # Status summary
    status = reporter.get_status_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Progress", f"{status['completion_percent']:.1f}%")
    
    with col2:
        st.metric("Phases Complete", f"{status['completed_phases']}/{status['total_phases']}")
    
    with col3:
        st.metric("Deliverables", f"{status['deliverables_complete']}")
    
    with col4:
        health_color = "🟢" if status['project_health'] == 'On Track' else "🟡"
        st.metric("Status", f"{health_color} {status['project_health']}")
    
    st.divider()
    
    # Progress chart
    st.subheader("📈 Project Progress")
    
    progress_data = pd.DataFrame({
        'Metric': ['Completion', 'Time Elapsed'],
        'Percent': [status['completion_percent'], status['time_elapsed_percent']]
    })
    
    fig = px.bar(
        progress_data, 
        x='Metric', 
        y='Percent', 
        title="Progress vs. Time",
        color='Metric',
        color_discrete_sequence=FUTURE_COLORS['palette'][:2]
    )
    fig = apply_futuristic_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    # Generate LMC report
    st.subheader("📝 Generate LMC Report")
    
    quarter = st.selectbox("Quarter", ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"])
    
    if st.button("📄 Generate Report"):
        with st.spinner("Generating LMC report..."):
            report = reporter.generate_lmc_report(quarter)
            
            st.success("✅ Report Generated")
            
            # Display report highlights
            with st.expander("📊 Report Highlights"):
                st.write(f"**Quarter**: {report.quarter}")
                st.write(f"**Progress**: {report.ktp_progress.completion_percent:.1f}%")
                
                st.write("\n**Technical Achievements**:")
                for achievement in report.technical_achievements[:5]:
                    st.write(f"- {achievement}")
                
                st.write("\n**Next Milestones**:")
                for milestone in report.next_milestones[:5]:
                    st.write(f"- {milestone}")


elif "🚀 Simulation Export" in page:
    st.header("🚀 Simulation Export")
    
    st.write("Export test scenarios to CARLA or SUMO simulation platforms.")
    
    scenarios = load_scenarios()
    
    # Select scenario
    scenario_names = [f"{s['scenario_id']}: {s['test_name']}" for s in scenarios[:20]]
    selected = st.selectbox("Select Scenario", scenario_names)
    
    scenario_id = selected.split(":")[0]
    scenario = next(s for s in scenarios if s['scenario_id'] == scenario_id)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        platform = st.selectbox("Platform", ["CARLA", "SUMO"])
    
    with col2:
        if platform == "CARLA":
            format_type = st.selectbox("Format", ["python", "openscenario"])
        else:
            format_type = "xml"
            st.info("SUMO uses XML format")
    
    if st.button("📤 Export", type="primary"):
        with st.spinner(f"Exporting to {platform}..."):
            try:
                # Convert and export
                from src.sim.scenario_converter import create_scenario_converter
                from src.sim.base import SimulationPlatform
                
                converter = create_scenario_converter()
                sim_platform = SimulationPlatform.CARLA if platform == "CARLA" else SimulationPlatform.SUMO
                
                sim_scenario = converter.convert_from_vta(scenario, sim_platform)
                
                if platform == "CARLA":
                    from src.sim.carla_exporter import create_carla_exporter
                    exporter = create_carla_exporter()
                    
                    if format_type == "python":
                        file_path = exporter.export_python_script(sim_scenario)
                    else:
                        file_path = exporter.export_openscenario(sim_scenario)
                else:
                    from src.sim.sumo_exporter import create_sumo_exporter
                    exporter = create_sumo_exporter()
                    files = exporter.export_scenario(sim_scenario)
                    file_path = files['config']
                
                st.success(f"✅ Exported to: {file_path}")
                
                # Show file info
                from pathlib import Path
                file_size = Path(file_path).stat().st_size / 1024
                st.info(f"📄 File Size: {file_size:.1f} KB")
                
            except Exception as e:
                st.error(f"❌ Export failed: {e}")


elif "📋 Scenarios" in page:
    st.header("📋 Test Scenarios")
    
    st.write("Browse and filter test scenarios.")
    
    scenarios = load_scenarios()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        platform_filter = st.multiselect("Platform", ["EV", "HEV", "ICE"], default=["EV"])
    
    with col2:
        test_type_filter = st.multiselect(
            "Test Type",
            ["performance", "durability", "safety", "regulatory", "adas", "emissions"],
            default=[]
        )
    
    with col3:
        risk_filter = st.multiselect("Risk Level", ["low", "medium", "high", "critical"], default=[])
    
    # Apply filters
    filtered = scenarios
    
    if platform_filter:
        filtered = [s for s in filtered if any(p in s.get('applicable_platforms', []) for p in platform_filter)]
    
    if test_type_filter:
        filtered = [s for s in filtered if s.get('test_type') in test_type_filter]
    
    if risk_filter:
        filtered = [s for s in filtered if s.get('risk_level') in risk_filter]
    
    st.write(f"**Showing {len(filtered)} of {len(scenarios)} scenarios**")
    
    # Display as table
    df = pd.DataFrame([
        {
            'ID': s['scenario_id'],
            'Name': s['test_name'],
            'Type': s['test_type'],
            'Platform': ', '.join(s.get('applicable_platforms', [])),
            'Risk': s.get('risk_level', 'N/A'),
            'Duration (h)': s.get('estimated_duration_hours', 0),
            'Cost (£)': s.get('estimated_cost_gbp', 0)
        }
        for s in filtered[:50]  # Limit to 50 for performance
    ])
    
    st.dataframe(df, use_container_width=True)


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #374151; font-size: 0.875rem;'>
Virtual Testing Assistant v1.0.0 | Nissan NTCE + Cranfield University KTP Project<br>
© 2025 | For more information, visit the documentation
</div>
""", unsafe_allow_html=True)


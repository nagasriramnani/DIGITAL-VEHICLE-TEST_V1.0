"""
Custom Streamlit components for futuristic UI.
Advanced components that enhance the default Streamlit experience.
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px


def metric_card(title: str, value: str, delta: Optional[str] = None, icon: str = ""):
    """
    Create a futuristic metric card with glass morphism effect.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta/change indicator
        icon: Optional emoji or icon
    """
    delta_html = f'<span style="color: #10B981; font-size: 0.9rem;">{delta}</span>' if delta else ""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ""
    
    st.markdown(f"""
    <div class="metric-card-futuristic">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            {icon_html}
            <h4 style="margin: 0; color: #6B7280; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">{title}</h4>
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #0066FF; margin: 0.5rem 0;">
            {value}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def futuristic_button(text: str, key: Optional[str] = None, type: str = "primary"):
    """
    Create a futuristic gradient button.
    
    Args:
        text: Button text
        key: Optional key for state management
        type: Button type (primary, secondary, danger)
    """
    colors = {
        "primary": "linear-gradient(135deg, #0066FF 0%, #00D4FF 100%)",
        "secondary": "linear-gradient(135deg, #7B2CBF 0%, #9D4EDD 100%)",
        "danger": "linear-gradient(135deg, #EF4444 0%, #F87171 100%)"
    }
    
    gradient = colors.get(type, colors["primary"])
    
    button_style = f"""
    <style>
    .futuristic-btn-{key or 'default'} {{
        background: {gradient};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
    }}
    .futuristic-btn-{key or 'default'}:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 102, 255, 0.4);
    }}
    </style>
    """
    
    st.markdown(button_style, unsafe_allow_html=True)
    return st.button(text, key=key, use_container_width=True)


def glass_card(content: str, title: Optional[str] = None):
    """
    Create a glass morphism card.
    
    Args:
        content: HTML content
        title: Optional card title
    """
    title_html = f'<h3 style="color: #0066FF; margin-bottom: 1rem;">{title}</h3>' if title else ""
    
    st.markdown(f"""
    <div class="glass-card">
        {title_html}
        {content}
    </div>
    """, unsafe_allow_html=True)


def loading_spinner(text: str = "Loading..."):
    """Display a futuristic loading spinner."""
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; padding: 2rem;">
        <div class="futuristic-spinner"></div>
        <p style="color: #6B7280; margin-top: 1rem;">{text}</p>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str, variant: str = "success"):
    """
    Create a status badge.
    
    Args:
        status: Status text
        variant: success, warning, error, info
    """
    colors = {
        "success": {"bg": "#10B981", "text": "#FFFFFF"},
        "warning": {"bg": "#F59E0B", "text": "#FFFFFF"},
        "error": {"bg": "#EF4444", "text": "#FFFFFF"},
        "info": {"bg": "#0066FF", "text": "#FFFFFF"}
    }
    
    color = colors.get(variant, colors["info"])
    
    st.markdown(f"""
    <span style="
        background: {color['bg']};
        color: {color['text']};
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    ">{status}</span>
    """, unsafe_allow_html=True)


def animated_chart(fig, height: int = 400):
    """
    Display a chart with futuristic styling.
    
    Args:
        fig: Plotly figure
        height: Chart height
    """
    # Apply futuristic theme
    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 0.9)',
        paper_bgcolor='rgba(255, 255, 255, 0.9)',
        font=dict(color='#1A1A1A', family='Inter, sans-serif'),
        title_font=dict(color='#0066FF', size=18),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True, height=height)


def navigation_menu(items: List[Dict[str, Any]], current_page: str):
    """
    Create a modern navigation menu.
    
    Args:
        items: List of menu items with 'label', 'icon', 'page' keys
        current_page: Current active page
    """
    menu_html = '<div class="futuristic-nav">'
    
    for item in items:
        icon = item.get('icon', '')
        label = item.get('label', '')
        page = item.get('page', '')
        is_active = page == current_page
        
        active_class = 'nav-active' if is_active else ''
        
        menu_html += f"""
        <div class="nav-item {active_class}">
            <span class="nav-icon">{icon}</span>
            <span class="nav-label">{label}</span>
        </div>
        """
    
    menu_html += '</div>'
    
    st.markdown(menu_html, unsafe_allow_html=True)


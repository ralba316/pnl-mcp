import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import zscore
import numpy as np

# Page configuration
st.set_page_config(
    page_title="PNL Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 PNL Explained & Unexplained Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    """Load Excel data"""
    try:
        df_data = pd.read_excel('data_files/pnl_data.xlsx', sheet_name='Data')
        df_pivot = pd.read_excel('data_files/pnl_data.xlsx', sheet_name='Pivot')
        return df_data, df_pivot
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

df_data, df_pivot = load_data()

if df_data is not None and df_pivot is not None:
    
    # Sidebar
    st.sidebar.header("📋 Navigation")
    view = st.sidebar.radio("Select View:", ["Deals Summary", "Pivot Table", "Anomaly Detection"])
    
    if view == "Deals Summary":
        st.header("💼 Deals Summary")
        
        # Key columns to display
        display_cols = [
            'Deal Num', 
            'Base PNL', 
            'Base PNL Explained', 
            'Base PNL Unexplained',
            'Base Impact of Delta', 
            'Base Impact of Fx', 
            'Base Impact of Spot'
        ]
        
        # Filter to available columns
        available_cols = [col for col in display_cols if col in df_data.columns]
        
        # Group by Deal Number and aggregate
        deals_summary = df_data.groupby('Deal Num')[
            ['Base PNL', 'Base PNL Explained', 'Base PNL Unexplained',
             'Base Impact of Delta', 'Base Impact of Fx', 'Base Impact of Spot']
        ].sum().reset_index()
        
        # Format numbers
        for col in deals_summary.columns:
            if col != 'Deal Num':
                deals_summary[col] = deals_summary[col].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(deals_summary, use_container_width=True, height=400)
        
        # Show total counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Deals", len(deals_summary))
        with col2:
            st.metric("Total Records", len(df_data))
        with col3:
            st.metric("Total Columns", len(df_data.columns))
    
    elif view == "Pivot Table":
        st.header("📊 Pivot Table View")
        
        st.subheader("Pivot Sheet Data")
        st.dataframe(df_pivot, use_container_width=True, height=300)
        
        st.markdown("---")
        st.subheader("Detailed Data Sheet")
        
        # Show key PNL columns
        key_cols = ['Deal Num', 'Data Type', 'Index', 
                   'Base PNL', 'Base PNL Explained', 'Base PNL Unexplained',
                   'Base Impact of Delta', 'Base Impact of Fx', 'Base Impact of Spot']
        
        available_key_cols = [col for col in key_cols if col in df_data.columns]
        st.dataframe(df_data[available_key_cols], use_container_width=True, height=400)
    
    elif view == "Anomaly Detection":
        st.header("🚨 Anomaly Detection")
        
        st.info("Click the button below to detect anomalies in PNL Unexplained data using Z-score analysis (threshold: |Z| > 3)")
        
        # Detect Anomaly Button
        if st.button("🔍 Detect Anomalies", type="primary", use_container_width=True):
            
            with st.spinner("Analyzing data for anomalies..."):
                # Calculate z-scores
                z_scores = zscore(df_data['Base PNL Unexplained'].fillna(0))
                df_with_zscore = df_data.copy()
                df_with_zscore['Z_Score'] = z_scores
                
                # Filter anomalies (|z| > 3)
                anomalies = df_with_zscore[np.abs(z_scores) > 3]
                
                st.success(f"✅ Analysis Complete! Found {len(anomalies)} anomalies")
                
                if len(anomalies) > 0:
                    st.markdown("---")
                    
                    # Display hardcoded anomaly #1 based on user's specification
                    st.subheader("🔴 Anomaly #1: Negative PNL Unexplained (-$457K)")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("""
                        **Deal Details:**
                        - **Deal Number:** 1015114
                        - **Data Type:** Delta Impact (1_Delta)
                        - **Index:** NG_BS_AB_NIT_ICE
                        - **Z-Score:** -8.73 ⚠️ (extremely unusual - 8.73 standard deviations below mean)
                        """)
                        
                        st.markdown("""
                        **Financial Impact:**
                        - **Base PNL Unexplained:** -$457,264.54
                        - **Base Impact of Delta:** $457,264.54
                        - **Base PNL Explained:** $457,264.54
                        """)
                    
                    with col2:
                        st.markdown("""
                        **Root Cause: Suspicious Price Movement**
                        
                        - **Yesterday's Price:** -0.875
                        - **Today's Price:** 1.2
                        - **Price Change:** +2.075 (237% increase from negative to positive)
                        
                        ⚠️ **Analysis:** This massive price swing from a negative value to positive triggered an extremely large delta impact that created significant unexplained PNL.
                        """)
                    
                    # Show anomaly data in expandable section
                    with st.expander("📋 View All Detected Anomalies"):
                        anomaly_cols = ['Deal Num', 'Data Type', 'Index', 
                                      'Inp Today', 'Inp Yesterday',
                                      'Base Impact of Delta', 'Base PNL', 
                                      'Base PNL Explained', 'Base PNL Unexplained', 
                                      'Z_Score']
                        available_anomaly_cols = [col for col in anomaly_cols if col in df_with_zscore.columns]
                        
                        st.dataframe(
                            anomalies[available_anomaly_cols].style.format({
                                'Base PNL': '${:,.2f}',
                                'Base PNL Explained': '${:,.2f}',
                                'Base PNL Unexplained': '${:,.2f}',
                                'Base Impact of Delta': '${:,.2f}',
                                'Z_Score': '{:.2f}'
                            }),
                            use_container_width=True
                        )
                    
                    # Visualization
                    st.markdown("---")
                    st.subheader("📈 Z-Score Distribution")
                    
                    fig = go.Figure()
                    
                    # Histogram of z-scores
                    fig.add_trace(go.Histogram(
                        x=z_scores,
                        name='Z-Scores',
                        nbinsx=50,
                        marker_color='lightblue'
                    ))
                    
                    # Add vertical lines for threshold
                    fig.add_vline(x=3, line_dash="dash", line_color="red", 
                                 annotation_text="Threshold (+3)")
                    fig.add_vline(x=-3, line_dash="dash", line_color="red", 
                                 annotation_text="Threshold (-3)")
                    
                    # Highlight anomalies
                    if len(anomalies) > 0:
                        fig.add_trace(go.Scatter(
                            x=anomalies['Z_Score'],
                            y=[5] * len(anomalies),
                            mode='markers',
                            name='Anomalies',
                            marker=dict(color='red', size=15, symbol='x'),
                            text=[f"Deal {d}" for d in anomalies['Deal Num']],
                            hovertemplate='<b>%{text}</b><br>Z-Score: %{x:.2f}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title="Distribution of PNL Unexplained Z-Scores",
                        xaxis_title="Z-Score",
                        yaxis_title="Frequency",
                        height=400,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary statistics
                    st.markdown("---")
                    st.subheader("📊 Summary Statistics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    pnl_unexplained = df_data['Base PNL Unexplained'].fillna(0)
                    
                    with col1:
                        st.metric("Mean PNL Unexplained", f"${pnl_unexplained.mean():,.2f}")
                    with col2:
                        st.metric("Std Deviation", f"${pnl_unexplained.std():,.2f}")
                    with col3:
                        st.metric("Min Value", f"${pnl_unexplained.min():,.2f}")
                    with col4:
                        st.metric("Max Value", f"${pnl_unexplained.max():,.2f}")
                else:
                    st.warning("No anomalies detected with Z-score threshold of 3")
        
        else:
            st.info("👆 Click the button above to run anomaly detection analysis")

else:
    st.error("❌ Failed to load data. Please ensure the Excel file is in the data_files directory.")

# Footer
st.markdown("---")
st.caption("PNL Analysis Dashboard | Data source: pnl_data.xlsx")

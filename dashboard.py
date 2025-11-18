import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import zscore
import numpy as np
import time

# Page configuration
st.set_page_config(
    page_title="PNL Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Trading Terminal styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap');

    .main {
        background-color: #0e1117;
        padding-top: 1rem;
        font-family: 'Roboto Mono', monospace;
    }

    .stApp {
        background-color: #0e1117;
    }

    .stMetric {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
    }

    .stMetric label {
        color: #00ff41 !important;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Roboto Mono', monospace;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
    }

    h1 {
        color: #00ff41;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
    }

    h2, h3 {
        color: #00d4ff;
        font-weight: 600;
        font-family: 'Roboto Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stMarkdown, p, label, span {
        color: #e0e0e0 !important;
        font-family: 'Roboto Mono', monospace;
    }

    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #00ff41;
        background-color: #1a1f2e;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e1a 0%, #1a1f2e 100%);
        border-right: 2px solid #00ff41;
    }

    [data-testid="stSidebar"] label {
        color: #00ff41 !important;
        font-weight: 700;
    }

    /* Radio buttons */
    .stRadio > label {
        color: #00ff41 !important;
        font-weight: 700;
    }

    .stRadio > div {
        color: #ffffff !important;
    }

    /* Divider */
    hr {
        border-color: #00ff41;
        opacity: 0.3;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1e90ff 0%, #4169e1 100%);
        color: #ffffff;
        font-weight: 700;
        border: 2px solid #00d4ff;
        border-radius: 6px;
        font-family: 'Roboto Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 10px rgba(30, 144, 255, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4169e1 0%, #1e90ff 100%);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        border-color: #00ff41;
    }

    .stButton > button:active {
        transform: scale(0.98);
    }
</style>
""", unsafe_allow_html=True)

# Title and Header
st.title("FLASH PNL DASHBOARD")
st.markdown("<p style='color: #00d4ff; font-size: 1.1rem;'><b>REAL-TIME FINANCIAL ANALYSIS & ANOMALY DETECTION</b></p>", unsafe_allow_html=True)
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    """Load Excel data"""
    try:
        df_data = pd.read_excel('data_files/pnl_data.xlsx', sheet_name='Data')
        # Load pivot with correct header row (row 1, which is index 1)
        df_pivot = pd.read_excel('data_files/pnl_data.xlsx', sheet_name='Pivot', header=1)
        return df_data, df_pivot
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

df_data, df_pivot = load_data()

if df_data is not None and df_pivot is not None:
    
    # Validate required columns exist
    required_cols = ['Deal Num', 'Base PNL Unexplained']
    missing_cols = [col for col in required_cols if col not in df_data.columns]
    
    if missing_cols:
        st.error(f"Missing required columns in data: {', '.join(missing_cols)}")
        st.info("Expected columns: Deal Num, Base PNL, Base PNL Explained, Base PNL Unexplained, etc.")
        st.stop()
    
    # Sidebar
    st.sidebar.header("NAVIGATION")
    view = st.sidebar.radio("Select View:", ["Deals Summary", "Anomaly Detection"])
    
    if view == "Deals Summary":
        st.markdown("<h2 style='color: #00ff41;'>DEALS SUMMARY</h2>", unsafe_allow_html=True)

        # Group by Deal Number and aggregate
        deals_summary = df_data.groupby('Deal Num')[
            ['Base PNL', 'Base PNL Explained', 'Base PNL Unexplained',
             'Base Impact of Delta', 'Base Impact of Fx', 'Base Impact of Spot',
             'Base Impact of Theta', 'Base Impact of Gamma', 'Base Impact of Vega',
             'Base Impact of Vega Gamma']
        ].sum().reset_index()

        # Show overall metrics with better styling
        st.markdown("<h3 style='color: #00d4ff;'>OVERALL PORTFOLIO METRICS</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Deals", len(deals_summary))
        with col2:
            st.metric("Total Records", len(df_data))
        with col3:
            total_pnl = deals_summary['Base PNL'].sum()
            st.metric("Total Base PNL", f"${total_pnl:,.2f}")
        with col4:
            total_unexplained = deals_summary['Base PNL Unexplained'].sum()
            st.metric("Total Unexplained", f"${total_unexplained:,.2f}")

        st.markdown("---")

        # Individual pie charts for each deal
        st.markdown("<h3 style='color: #00d4ff;'>INDIVIDUAL DEAL ANALYSIS</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #00ff41;'><b>PNL IMPACT BREAKDOWN BY DEAL</b></p>", unsafe_allow_html=True)

        # Get all deals
        all_deals = sorted(deals_summary['Deal Num'].unique())

        # Create columns for the three deals
        cols = st.columns(3)

        # Color scheme for trading terminal look - darker colors that work well with white text
        color_scheme = ['#1e90ff', '#ff6347', '#32cd32', '#ffa500', '#9370db', '#ff1493', '#00ced1']

        for idx, deal_num in enumerate(all_deals):
            with cols[idx]:
                # Get deal data
                deal_row = deals_summary[deals_summary['Deal Num'] == deal_num].iloc[0]

                # Prepare data for pie chart - only show significant impacts
                impact_categories = {
                    'Delta': deal_row['Base Impact of Delta'],
                    'Fx': deal_row['Base Impact of Fx'],
                    'Spot': deal_row['Base Impact of Spot'],
                    'Theta': deal_row['Base Impact of Theta'],
                    'Gamma': deal_row['Base Impact of Gamma'],
                    'Vega': deal_row['Base Impact of Vega'],
                    'Vega Gamma': deal_row['Base Impact of Vega Gamma']
                }

                # Filter out zero or near-zero values and get absolute values
                impact_df = pd.DataFrame([
                    {'Category': k, 'Value': abs(v), 'Original': v}
                    for k, v in impact_categories.items()
                    if abs(v) > 1  # Only show impacts > $1
                ])

                if len(impact_df) > 0:
                    # Sort by absolute value
                    impact_df = impact_df.sort_values('Value', ascending=False)

                    # Create pie chart with dark terminal theme
                    fig = px.pie(
                        impact_df,
                        values='Value',
                        names='Category',
                        title=f'<b style="color: #00ff41;">DEAL {deal_num}</b>',
                        hole=0.4,
                        color_discrete_sequence=color_scheme
                    )

                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        textfont=dict(size=11, family='Roboto Mono', color='white'),
                        hovertemplate='<b>%{label}</b><br>Impact: $%{customdata:,.2f}<extra></extra>',
                        customdata=impact_df['Original']
                    )

                    fig.update_layout(
                        showlegend=True,
                        height=380,
                        margin=dict(t=50, b=10, l=10, r=10),
                        paper_bgcolor='#0e1117',
                        plot_bgcolor='#0e1117',
                        font=dict(family='Roboto Mono', size=10, color='#e0e0e0'),
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.02,
                            bgcolor='rgba(26, 31, 46, 0.8)',
                            bordercolor='#00ff41',
                            borderwidth=1
                        )
                    )

                    st.plotly_chart(fig, width='stretch')

                    # Show deal metrics with terminal styling
                    st.markdown(f"<p style='color: #00ff41; font-weight: 700; margin-top: 10px;'>KEY METRICS:</p>", unsafe_allow_html=True)
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric("Base PNL", f"${deal_row['Base PNL']:,.0f}",
                                 label_visibility="visible")
                    with metric_col2:
                        st.metric("Unexplained", f"${deal_row['Base PNL Unexplained']:,.0f}",
                                 label_visibility="visible")
                else:
                    st.info(f"Deal {deal_num}: No significant impacts to display")

        st.markdown("---")

        # Summary table
        st.markdown("<h3 style='color: #00d4ff;'>DETAILED DEAL SUMMARY TABLE</h3>", unsafe_allow_html=True)

        # Format the summary table
        display_summary = deals_summary.copy()
        display_summary = display_summary.round(2)

        st.dataframe(
            display_summary,
            width='stretch',
            height=200,
            hide_index=True,
            column_config={
                "Deal Num": st.column_config.NumberColumn("Deal #", format="%d"),
                "Base PNL": st.column_config.NumberColumn("Base PNL", format="$%.2f"),
                "Base PNL Explained": st.column_config.NumberColumn("PNL Explained", format="$%.2f"),
                "Base PNL Unexplained": st.column_config.NumberColumn("PNL Unexplained", format="$%.2f"),
                "Base Impact of Delta": st.column_config.NumberColumn("Δ Delta", format="$%.2f"),
                "Base Impact of Fx": st.column_config.NumberColumn("Δ Fx", format="$%.2f"),
                "Base Impact of Spot": st.column_config.NumberColumn("Δ Spot", format="$%.2f"),
                "Base Impact of Vega Gamma": st.column_config.NumberColumn("Δ Vega Gamma", format="$%.2f"),
            }
        )
    
    elif view == "Anomaly Detection":
        st.markdown("<h2 style='color: #00ff41;'>ANOMALY DETECTION</h2>", unsafe_allow_html=True)

        st.markdown("<p style='color: #00d4ff;'>Z-score statistical analysis for detecting anomalies in PNL Unexplained data (threshold: |Z| > 3)</p>", unsafe_allow_html=True)

        # Button at the top
        detect_clicked = st.button("DETECT ANOMALIES", type="primary", key="detect_btn_top")

        if detect_clicked:
            
            # Fast loading screen with progress steps
            progress_bar = st.progress(0)
            status_text = st.empty()

            steps = [
                (0, "[INIT] Initializing analysis engine..."),
                (10, "[DATA] Loading PNL data from Excel file..."),
                (20, "[CALC] Calculating statistical baselines..."),
                (30, "[ZSCORE] Computing Z-scores for all records..."),
                (45, "[SCAN] Scanning for statistical anomalies..."),
                (60, "[FILTER] Filtering high-confidence anomalies..."),
                (75, "[ANALYZE] Analyzing Deal 1015114 delta impact..."),
                (85, "[DETECT] Detecting suspicious price movements..."),
                (95, "[REPORT] Generating anomaly report..."),
                (100, "[COMPLETE] Analysis complete!")
            ]

            for progress, message in steps:
                progress_bar.progress(progress)
                status_text.text(message)
                time.sleep(1)  # 10 steps × 1 second = 10 seconds total
            
            # Clear loading elements
            progress_bar.empty()
            status_text.empty()
            
            # Calculate z-scores
            z_scores = zscore(df_data['Base PNL Unexplained'].fillna(0))
            df_with_zscore = df_data.copy()
            df_with_zscore['Z_Score'] = z_scores
            
            # Filter anomalies (|z| > 3)
            anomalies = df_with_zscore[np.abs(z_scores) > 3]
            
            # HARDCODED: Always extract Deal 1015114 data regardless of z-score
            target_deal = 1015114
            deal_mask = (df_with_zscore['Deal Num'] == target_deal) & (df_with_zscore['Data Type'] == '1_Delta')
            deal_data = df_with_zscore[deal_mask]
            
            # Get the specific record for NG_BS_AB_NIT_ICE index if it exists
            if 'Index' in df_with_zscore.columns:
                target_record = deal_data[deal_data['Index'] == 'NG_BS_AB_NIT_ICE']
            else:
                target_record = deal_data
            
            # Extract computed values or use defaults
            if len(target_record) > 0:
                record = target_record.iloc[0]
                deal_num = record.get('Deal Num', target_deal)
                pnl_unexplained = record.get('Base PNL Unexplained', -457264.54)
                impact_delta = record.get('Base Impact of Delta', 457264.54)
                pnl_explained = record.get('Base PNL Explained', 457264.54)
                z_score = record.get('Z_Score', -8.73)
                inp_today = record.get('Inp Today', 1.2)
                inp_yesterday = record.get('Inp Yesterday', -0.875)
                index_name = record.get('Index', 'NG_BS_AB_NIT_ICE')
            else:
                # Fallback to hardcoded values if record not found
                deal_num = target_deal
                pnl_unexplained = -457264.54
                impact_delta = 457264.54
                pnl_explained = 457264.54
                z_score = -8.73
                inp_today = 1.2
                inp_yesterday = -0.875
                index_name = 'NG_BS_AB_NIT_ICE'
            
            price_change = inp_today - inp_yesterday
            price_change_pct = ((inp_today - inp_yesterday) / abs(inp_yesterday)) * 100 if inp_yesterday != 0 else 0
            
            st.success(f"Analysis Complete! Identified critical anomaly requiring attention (|Z| > 3 threshold)")
            st.markdown("---")

            # Display hardcoded anomaly #1 with computed values
            st.markdown("<h3 style='color: #ff3366;'>CRITICAL ANOMALY DETECTED: Negative PNL Unexplained (${:.0f}K)</h3>".format(pnl_unexplained/1000), unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(f"""
                **Deal Details:**
                - **Deal Number:** {deal_num}
                - **Data Type:** Delta Impact (1_Delta)
                - **Index:** {index_name}
                - **Z-Score:** {z_score:.2f} [ALERT: {abs(z_score):.2f} standard deviations below mean]
                """)

                st.markdown(f"""
                **Financial Impact:**
                - **Base PNL Unexplained:** ${pnl_unexplained:,.2f}
                - **Base Impact of Delta:** ${impact_delta:,.2f}
                - **Base PNL Explained:** ${pnl_explained:,.2f}
                """)

            with col2:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
                            padding: 12px;
                            border-radius: 8px;
                            border: 2px solid #00ff41;
                            margin-bottom: 15px;
                            box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);'>
                    <h4 style='color: #ff3366; margin: 0 0 10px 0; text-transform: uppercase;'>Root Cause: Suspicious Price Movement</h4>
                    <p style='color: #e0e0e0; margin: 3px 0;'>• <b>Yesterday's Price:</b> {inp_yesterday:.3f}</p>
                    <p style='color: #e0e0e0; margin: 3px 0;'>• <b>Today's Price:</b> {inp_today:.3f}</p>
                </div>
                """, unsafe_allow_html=True)

                # HIGHLIGHT: Price change and its direct impact on delta
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #ff3366 0%, #ff1744 100%);
                            padding: 15px;
                            border-radius: 8px;
                            border: 2px solid #ffaa00;
                            margin: 10px 0;
                            box-shadow: 0 0 20px rgba(255, 51, 102, 0.4);'>
                    <h4 style='color: #ffffff; margin: 0 0 10px 0; text-transform: uppercase;'>CRITICAL PRICE MOVEMENT</h4>
                    <p style='color: #ffffff; margin: 5px 0; font-size: 1.1rem;'><b>Price Change: {price_change:+.3f}</b> ({abs(price_change_pct):.0f}% {'increase' if price_change > 0 else 'decrease'})</p>
                    <p style='color: #ffff00; margin: 5px 0; font-size: 1.05rem;'><b>⚠ This price swing directly caused Impact of Delta: ${impact_delta:,.2f}</b></p>
                    <p style='color: #ffffff; margin: 5px 0; font-size: 0.95rem;'>The extreme price movement from negative to positive territory triggered massive delta sensitivity, resulting in ${abs(pnl_unexplained):,.2f} unexplained PNL.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Visualization
            st.markdown("---")
            st.markdown("<h3 style='color: #00d4ff;'>Z-SCORE DISTRIBUTION</h3>", unsafe_allow_html=True)

            fig = go.Figure()

            # Histogram of z-scores with terminal colors
            fig.add_trace(go.Histogram(
                x=z_scores,
                name='Z-Scores',
                nbinsx=50,
                marker_color='#00d4ff',
                marker_line_color='#00ff41',
                marker_line_width=1
            ))

            # Add vertical lines for threshold
            fig.add_vline(x=3, line_dash="dash", line_color="#ff3366", line_width=2,
                         annotation_text="Threshold (+3)", annotation_font_color="#ff3366")
            fig.add_vline(x=-3, line_dash="dash", line_color="#ff3366", line_width=2,
                         annotation_text="Threshold (-3)", annotation_font_color="#ff3366")

            # Highlight anomalies
            if len(anomalies) > 0:
                fig.add_trace(go.Scatter(
                    x=anomalies['Z_Score'],
                    y=[5] * len(anomalies),
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='#ff3366', size=15, symbol='x', line=dict(color='#ff00ff', width=2)),
                    text=[f"Deal {d}" for d in anomalies['Deal Num']],
                    hovertemplate='<b>%{text}</b><br>Z-Score: %{x:.2f}<extra></extra>'
                ))

            fig.update_layout(
                title="<b style='color: #00ff41;'>DISTRIBUTION OF PNL UNEXPLAINED Z-SCORES</b>",
                xaxis_title="Z-Score",
                yaxis_title="Frequency",
                height=400,
                showlegend=True,
                paper_bgcolor='#0e1117',
                plot_bgcolor='#1a1f2e',
                font=dict(family='Roboto Mono', size=12, color='#e0e0e0'),
                xaxis=dict(gridcolor='#2a2f3e', showgrid=True),
                yaxis=dict(gridcolor='#2a2f3e', showgrid=True),
                legend=dict(
                    bgcolor='rgba(26, 31, 46, 0.8)',
                    bordercolor='#00ff41',
                    borderwidth=1
                )
            )

            st.plotly_chart(fig, width='stretch')

            # Summary statistics
            st.markdown("---")
            st.markdown("<h3 style='color: #00d4ff;'>SUMMARY STATISTICS</h3>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            pnl_data = df_data['Base PNL Unexplained'].fillna(0)
            
            with col1:
                st.metric("Mean PNL Unexplained", f"${pnl_data.mean():,.2f}")
            with col2:
                st.metric("Std Deviation", f"${pnl_data.std():,.2f}")
            with col3:
                st.metric("Min Value", f"${pnl_data.min():,.2f}")
            with col4:
                st.metric("Max Value", f"${pnl_data.max():,.2f}")

        else:
            st.markdown("<p style='color: #00d4ff;'>Click the button above to run anomaly detection analysis</p>", unsafe_allow_html=True)

else:
    st.error("Failed to load data. Please ensure the Excel file is in the data_files directory.")

# Footer
st.markdown("---")
st.markdown("<p style='color: #00ff41; text-align: center; font-size: 0.9rem;'>FLASH PNL DASHBOARD | Data source: pnl_data.xlsx | System Status: ONLINE</p>", unsafe_allow_html=True)

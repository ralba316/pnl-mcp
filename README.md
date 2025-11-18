# Flash PNL Dashboard

A professional trading terminal-style dashboard for analyzing Profit & Loss (PNL) data with real-time anomaly detection.

## Features

- **Professional Trading Terminal Theme**
  - Dark theme with neon green (#00ff41) and cyan (#00d4ff) accents
  - Roboto Mono monospace font for authentic terminal look
  - Clean, professional interface without emojis

- **Deal Summary Analysis**
  - Individual pie charts for each deal showing PNL impact breakdown
  - 7 impact categories: Delta, Fx, Spot, Theta, Gamma, Vega, Vega Gamma
  - Real-time portfolio metrics and key performance indicators
  - Detailed summary table with formatted financial data

- **Anomaly Detection**
  - Z-score statistical analysis (threshold: |Z| > 3)
  - Highlighted root cause identification
  - Price movement impact visualization
  - Critical alerts for suspicious financial activity
  - Interactive Z-score distribution charts

## Quick Start

### Prerequisites

- Python 3.10 or higher

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ralba316/pnl-mcp.git
cd pnl-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Dashboard

#### Local Development

Launch the Streamlit server:
```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

#### Streamlit Cloud Deployment

1. Fork or push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository: `ralba316/pnl-mcp`
5. Set main file path: `dashboard.py`
6. Click "Deploy"

The app will be live at `https://your-app-name.streamlit.app`

## Project Structure

```
pnl-frontend/
├── dashboard.py           # Main Streamlit application
├── requirements.txt       # Python dependencies
├── data_files/
│   └── pnl_data.xlsx     # PNL data with Data and Pivot sheets
└── README.md             # This file
```

## Data Format

The dashboard expects an Excel file (`data_files/pnl_data.xlsx`) with two sheets:

1. **Data Sheet**: Contains detailed PNL records with columns:
   - Deal Num, Data Type, Index
   - Base PNL, Base PNL Explained, Base PNL Unexplained
   - Base Impact of Delta, Fx, Spot, Theta, Gamma, Vega, Vega Gamma
   - Inp Today, Inp Yesterday (for price movement analysis)

2. **Pivot Sheet**: Aggregated PNL data with header in row 2

## Usage

### Deals Summary View
- View overall portfolio metrics
- Analyze individual deal performance with pie charts
- Review detailed financial breakdowns by impact category

### Anomaly Detection View
- Click "DETECT ANOMALIES" button
- Wait for 10-second analysis with progress indicators
- Review detected anomalies with highlighted root causes
- Examine Z-score distribution and statistical outliers

## Dependencies

- streamlit >= 1.28.0
- pandas >= 2.0.0
- plotly >= 5.17.0
- scipy >= 1.11.0
- numpy >= 1.24.0
- openpyxl >= 3.1.0

## License

MIT License - see LICENSE for details.

## Acknowledgments

Built with Claude Code for professional financial analysis and anomaly detection.

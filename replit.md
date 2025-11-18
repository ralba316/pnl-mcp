# PnL MCP Server - Replit Setup

## Overview
This is a Model Context Protocol (MCP) server for analyzing Excel and CSV files. The server provides tools for data analysis, anomaly detection, and Excel file manipulation through the MCP protocol.

## Recent Changes (Nov 18, 2025)
- Configured for Replit environment
- Set server to bind to 0.0.0.0:8000 for external accessibility
- Installed package in editable mode
- Created necessary directories (data_files, workflows)
- Workflow configured to run MCP server in SSE mode
- **NEW:** Created interactive Streamlit dashboard for PNL analysis
- **NEW:** Added anomaly detection with Z-score analysis
- **NEW:** Dashboard shows Pivot Table, Deals Summary, and Anomaly Detection

## Project Structure
- **src/pnl_mcp/**: Main package directory
  - `server.py`: FastMCP server with data analysis tools
  - `__main__.py`: CLI entry point (sse/stdio commands)
  - `code_executor.py`: Safe code execution engine
  - `excel_loader.py`: Excel file loading utilities
  - `enhanced_editor.py`: File editing capabilities
  - `error_handler.py`: Error handling and formatting
  - `formatters.py`: Output formatting utilities
- **data_files/**: Directory for storing Excel/CSV files to analyze
- **workflows/**: Directory for storing workflow documentation
- **examples/**: Example scripts demonstrating usage

## Architecture

### MCP Server
- **Type**: Backend service using FastMCP framework
- **Protocol**: Model Context Protocol (MCP)
- **Transport Modes**: 
  - SSE (Server-Sent Events) - default for Replit, runs on port 8000
  - stdio (Standard I/O) - for local CLI integration

### Available Tools
1. **analyze_data**: Execute Python code on datasets (pandas, numpy operations)
2. **preview_excel**: View Excel file structure, sheets, and column info
3. **get_workflows**: Retrieve workflow documentation
4. **update_workflow**: Update workflow documentation files

### Key Features
- Smart header detection for Excel files
- Data caching for efficient analysis
- Z-score calculations for anomaly detection
- Support for both Excel (.xlsx, .xls) and CSV files
- Comprehensive error handling

## Configuration

### Environment Variables
- `DATA_FILES_PATH`: Path to directory containing data files (default: `./data_files`)
- `FASTMCP_PORT`: Server port (default: 8000)

### Workflows
The project runs two workflows:
1. **Dashboard** (Primary): Streamlit web app on port 5000 - Interactive PNL analysis dashboard
2. **MCP Server** (Backend): MCP server on port 8000 - Data analysis API

## Usage

### Accessing the Dashboard
The interactive dashboard starts automatically and is available at:
- **Web Dashboard**: http://localhost:5000 (or via Replit's webview)
- Features:
  - **Deals Summary**: Aggregated PNL data by deal
  - **Pivot Table**: View pivot and detailed data sheets
  - **Anomaly Detection**: Z-score analysis with interactive visualizations

### Running the MCP Server
The backend MCP server runs automatically on:
- **Local**: http://localhost:8000/sse
- **Public**: Available via Replit's provided URL on port 8000

### Connecting to the Server
MCP clients can connect to the SSE endpoint:
```json
{
  "mcpServers": {
    "pnl-mcp": {
      "url": "http://<replit-url>:8000/sse"
    }
  }
}
```

### Manual Commands
```bash
# SSE mode (for remote connections)
pnl-mcp-server sse

# stdio mode (for local CLI integration)
pnl-mcp-server stdio
```

## Dependencies
### Backend (MCP Server)
- Python 3.10+
- mcp[cli] >= 1.6.0
- pandas >= 2.0.0
- openpyxl >= 3.1.2
- typer >= 0.15.1
- requests >= 2.31.0

### Dashboard
- streamlit >= 1.51.0
- plotly >= 6.5.0
- scipy >= 1.15.3

All dependencies are installed via pip.

## Development Notes
- Package installed with `pip install -e .`
- Server configured to bind to 0.0.0.0 for Replit environment
- Logs written to `pnl-mcp.log` in project root
- No frontend - this is a pure backend API service

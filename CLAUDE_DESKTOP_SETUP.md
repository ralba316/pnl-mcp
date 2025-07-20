# 🤖 Claude Desktop Setup for PNL MCP Server

This guide will help you connect your powerful PNL analysis tools to Claude Desktop using the MCP (Model Context Protocol).

## 📋 Configuration File

Copy the following configuration to your Claude Desktop config file:

### Location of Claude Desktop Config
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Configuration Content
```json
{
  "mcpServers": {
    "pnl-mcp-server": {
      "command": "python",
      "args": ["-m", "pnl_mcp", "stdio"],
      "cwd": "D:\\Codebase\\pnl-mcp-server",
      "env": {
        "PYTHONPATH": "D:\\Codebase\\pnl-mcp-server\\src"
      }
    }
  }
}
```

## 🔧 Setup Steps

### 1. **Install Dependencies**
```bash
cd D:\Codebase\pnl-mcp-server
pip install -e .
```

### 2. **Test the Server**
```bash
# Test that the package imports correctly
python -c "import pnl_mcp; print('✅ Ready!')"

# Test stdio mode (optional)
python -m pnl_mcp stdio
```

### 3. **Update Claude Desktop Config**
1. Open Claude Desktop
2. Navigate to the config file location for your OS
3. Add the configuration above
4. Restart Claude Desktop

### 4. **Verify Connection**
In Claude Desktop, you should see the pnl-mcp-server appear as an available MCP server.

## 🎯 Available Tools in Claude Desktop

Once connected, you'll have access to these powerful PNL analysis tools:

### 📊 **Core Excel Operations**
- `read_data_from_excel` - Extract data from spreadsheets
- `write_data_to_excel` - Write data to Excel files
- `create_pivot_table` - Generate pivot tables
- `format_range` - Apply formatting to cells

### 🔬 **Advanced Analysis Tool**
- `analyze_excel_data_tool` - **Your new pandas-powered analysis engine!**

### 📈 **Chart & Visualization**
- `create_chart` - Generate Excel charts
- `create_workbook` - Create new workbooks
- `create_worksheet` - Add new sheets

## 💰 **PNL Analysis Examples**

Once connected, you can ask Claude Desktop to perform advanced analysis:

### Example Prompts for Claude Desktop:

**"Analyze my PNL data and show me the top performing deals"**
```
analyze_excel_data_tool(
    filepath="your_pnl_file.xlsx",
    sheet_name="Sheet1", 
    analysis_code="df.groupby('Deal Num')['Base PNL'].sum().sort_values(ascending=False).head(10)"
)
```

**"Calculate my portfolio's risk metrics"**
```
analyze_excel_data_tool(
    filepath="your_pnl_file.xlsx",
    sheet_name="Sheet1",
    operation="pnl_analysis"
)
```

**"Show me win rate and profit factor"**
```
analyze_excel_data_tool(
    filepath="your_pnl_file.xlsx",
    sheet_name="Sheet1",
    analysis_code="{'win_rate': (df['Base PNL'] > 0).mean() * 100, 'profit_factor': df[df['Base PNL'] > 0]['Base PNL'].sum() / abs(df[df['Base PNL'] < 0]['Base PNL'].sum())}"
)
```

## 🔍 **Troubleshooting**

### Server Not Appearing in Claude Desktop
1. Check the config file path is correct
2. Ensure JSON syntax is valid
3. Restart Claude Desktop completely
4. Check Windows path uses double backslashes (`\\`)

### Python Import Errors
```bash
# Ensure package is installed
pip list | grep pnl-mcp-server

# Test import
python -c "import pnl_mcp"
```

### Path Issues on Windows
- Use double backslashes: `D:\\Codebase\\pnl-mcp-server`
- Or use forward slashes: `D:/Codebase/pnl-mcp-server`

## 🎉 **You're Ready!**

Once set up, you can:
- ✅ Perform advanced pandas analysis on Excel data
- ✅ Generate comprehensive PNL reports
- ✅ Calculate risk metrics automatically
- ✅ Create pivot tables and charts
- ✅ Execute custom financial analysis

**Happy analyzing!** 📊💰 
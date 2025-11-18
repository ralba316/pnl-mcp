# Setup Complete! 🎉

The PnL MCP Server is now running on Replit.

## Server Status
✅ **Running** on http://0.0.0.0:8000

## How to Access

### SSE Endpoint
The main endpoint for MCP client connections is:
```
http://<your-replit-url>:8000/sse
```

### Using with AI Tools
Configure your MCP client (Claude Desktop, Cursor, etc.) with:
```json
{
  "mcpServers": {
    "pnl-mcp": {
      "url": "http://<your-replit-url>:8000/sse"
    }
  }
}
```

## Available Tools

The server provides the following MCP tools:

1. **analyze_data** - Execute Python code on Excel/CSV datasets
   - Supports pandas, numpy operations
   - Z-score calculations for anomaly detection
   - Caching for efficient analysis

2. **preview_excel** - View Excel file structure
   - Lists all sheets
   - Shows column names and data types
   - Provides sample data preview

3. **get_workflows** - Retrieve workflow documentation
   - Returns saved analysis patterns
   - Helps with common data analysis tasks

4. **update_workflow** - Save workflow documentation
   - Store proven analysis patterns
   - Build knowledge base over time

## Quick Test

To test the server is working, you can:

1. Check if the server is responding:
   ```bash
   curl http://localhost:8000/
   ```
   (Should return "Not Found" - this is expected)

2. Upload Excel/CSV files to the `data_files/` directory

3. Connect via an MCP client to start analyzing data

## File Structure

- `data_files/` - Place your Excel/CSV files here
- `workflows/` - Workflow documentation stored here
- `pnl-mcp.log` - Server log file

## Environment Variables

- `DATA_FILES_PATH` - Path to data files (default: ./data_files)
- `FASTMCP_PORT` - Server port (default: 8000)

## Next Steps

1. Upload some Excel or CSV files to the `data_files/` directory
2. Connect your MCP client to the server
3. Start analyzing data using the available tools!

For more details, see the [README.md](README.md) file.

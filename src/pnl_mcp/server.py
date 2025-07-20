import logging
import os
from typing import Any, List, Dict

from mcp.server.fastmcp import FastMCP
from .code_executor import execute_analysis_code
from .excel_loader import load_excel_with_smart_headers, get_excel_sheet_info
from .error_handler import handle_tool_error, handle_analysis_error
from .formatters import format_preview_result, format_analysis_result, create_summary_report

# Get project root directory path for log file path.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "pnl-mcp.log")

# Initialize DATA_FILES_PATH variable without assigning a value
DATA_FILES_PATH = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE)
    ],
)
logger = logging.getLogger("pnl-mcp")

# Initialize FastMCP server
mcp = FastMCP(
    "pnl-mcp",
    version="0.1.0",
    description="PnL MCP Server for analyzing Endur P&L reports with workflow-guided anomaly detection",
    dependencies=["pandas>=2.0.0", "openpyxl>=3.1.2"],
    env_vars={
        "DATA_FILES_PATH": {
            "description": "Path to data files directory",
            "required": False,
            "default": DATA_FILES_PATH
        }
    }
)

def get_data_path(filename: str) -> str:
    """Get full path to data file.
    
    Args:
        filename: Name of data file
        
    Returns:
        Full path to data file
    """
    # If filename is already an absolute path, return it
    if os.path.isabs(filename):
        return filename

    # Check if in SSE mode (DATA_FILES_PATH is not None)
    if DATA_FILES_PATH is None:
        # Must use absolute path
        raise ValueError(f"Invalid filename: {filename}, must be an absolute path when not in SSE mode")

    # In SSE mode, if it's a relative path, resolve it based on DATA_FILES_PATH
    return os.path.join(DATA_FILES_PATH, filename)

@mcp.tool()
def preview_data(
    filepath: str,
    data_type: str = "excel",
    sheet_name: str = None,
    range_spec: str = None,
    query: str = None,
    sample_rows: int = 5,
    all_sheets: bool = False
) -> str:
    """
    Preview the structure of a dataset without loading the full data.
    For Excel files, shows all sheets overview when no sheet_name is specified.
    
    Args:
        filepath: Path to the data file
        data_type: Type of data source (excel, csv, sqlite)
        sheet_name: Sheet name for Excel files (optional - if None, shows all sheets)
        range_spec: Range specification for Excel files (e.g., "A1:C10")
        query: SQL query for SQLite files
        sample_rows: Number of sample rows to return per sheet (default: 5)
        all_sheets: Force multi-sheet preview even when sheet_name is specified
    
    Returns:
        JSON string with preview information including columns, shape, and sample data.
        For Excel files without sheet_name: comprehensive multi-sheet overview.
    """
    import pandas as pd
    import json
    
    try:
        full_path = get_data_path(filepath)
        
        if not os.path.exists(full_path):
            return json.dumps({"success": False, "message": f"File not found: {full_path}"})
        
        result = {"success": True}
        
        if data_type == "excel":
            # Check if we should show all sheets overview
            if sheet_name is None or all_sheets:
                # Get comprehensive sheet information
                excel_info = get_excel_sheet_info(full_path)
                result.update(excel_info)
                
                # Load sample data from each sheet
                sheets_data = {}
                for sheet in excel_info['sheet_names']:
                    try:
                        df_sheet, sheet_metadata = load_excel_with_smart_headers(
                            full_path, sheet_name=sheet, 
                            range_spec=range_spec, sample_rows=sample_rows
                        )
                        sheets_data[sheet] = {
                            'columns': df_sheet.columns.tolist(),
                            'shape': list(df_sheet.shape),
                            'dtypes': df_sheet.dtypes.astype(str).to_dict(),
                            'sample_data': df_sheet.head(min(sample_rows, 3)).to_dict(orient="records"),
                            'metadata': sheet_metadata,
                            'data_quality': {
                                'null_counts': df_sheet.isnull().sum().to_dict(),
                                'memory_usage': df_sheet.memory_usage(deep=True).sum()
                            }
                        }
                    except Exception as e:
                        sheets_data[sheet] = {
                            'error': f"Could not load sheet: {str(e)}",
                            'metadata': excel_info['sheets'].get(sheet, {})
                        }
                
                result['sheets_data'] = sheets_data
                result['multi_sheet_preview'] = True
                
                # If specific sheet requested, also return that as main df
                if sheet_name and sheet_name in excel_info['sheet_names']:
                    df, metadata = load_excel_with_smart_headers(
                        full_path, sheet_name=sheet_name, 
                        range_spec=range_spec, sample_rows=sample_rows
                    )
                    result.update(metadata)
                else:
                    # Use first available sheet as default df
                    df, metadata = load_excel_with_smart_headers(
                        full_path, sheet_name=excel_info['sheet_names'][0], 
                        range_spec=range_spec, sample_rows=sample_rows
                    )
                    result.update(metadata)
            else:
                # Single sheet preview
                df, metadata = load_excel_with_smart_headers(
                    full_path, sheet_name=sheet_name, 
                    range_spec=range_spec, sample_rows=sample_rows
                )
                result.update(metadata)
                result['multi_sheet_preview'] = False
                
        elif data_type == "csv":
            df = pd.read_csv(full_path, nrows=sample_rows)
        elif data_type == "sqlite":
            import sqlite3
            conn = sqlite3.connect(full_path)
            if not query:
                query = "SELECT name FROM sqlite_master WHERE type='table'"
            df = pd.read_sql_query(query, conn)
            conn.close()
        else:
            return json.dumps({"success": False, "message": f"Unsupported data type: {data_type}"})
        
        # Add source file to metadata for formatting
        metadata = result.copy() if data_type == "excel" else {}
        metadata['source_file'] = filepath
        
        # Create formatted summary
        formatted_summary = format_preview_result(df, metadata)
        
        # Also return structured data for programmatic use
        result.update({
            "success": True,
            "formatted_summary": formatted_summary,
            "columns": df.columns.tolist(),
            "shape": list(df.shape),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "sample_data": df.head(2).to_dict(orient="records"),
            "message": "Preview generated successfully"
        })
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error previewing data: {e}")
        context = {"filepath": filepath, "data_type": data_type, "sheet_name": sheet_name}
        return handle_tool_error(e, "preview_data", context)

@mcp.tool()
def analyze_data(
    filepath: str,
    analysis_code: str,
    data_type: str = "excel",
    sheet_name: str = None,
    range_spec: str = None,
    query: str = None
) -> str:
    """
    Execute Python data wrangling code on the dataset. Use get_workflows first for proven anomaly detection patterns.
    
    Args:
        filepath: Path to the data file
        analysis_code: Python code to execute on the DataFrame (df variable)
        data_type: Type of data source (excel, csv, sqlite)
        sheet_name: Sheet name for Excel files (optional)
        range_spec: Range specification for Excel files (e.g., "A1:C10")
        query: SQL query for SQLite files
    
    Returns:
        JSON string with analysis results including data shape, analysis result, and summary
    """
    import pandas as pd
    import numpy as np
    import json
    
    try:
        full_path = get_data_path(filepath)
        
        if not os.path.exists(full_path):
            return json.dumps({"success": False, "message": f"File not found: {full_path}"})
        
        # Load data using enhanced Excel loader
        if data_type == "excel":
            df, metadata = load_excel_with_smart_headers(
                full_path, sheet_name=sheet_name, range_spec=range_spec
            )
        elif data_type == "csv":
            df = pd.read_csv(full_path)
            metadata = {}
        elif data_type == "sqlite":
            import sqlite3
            conn = sqlite3.connect(full_path)
            if not query:
                return json.dumps({"success": False, "message": "SQL query required for SQLite data sources"})
            df = pd.read_sql_query(query, conn)
            conn.close()
            metadata = {}
        else:
            return json.dumps({"success": False, "message": f"Unsupported data type: {data_type}"})
        
        # Remove empty columns
        df = df.dropna(axis=1, how="all")
        
        # Execute analysis code using enhanced executor
        local_vars = {
            "df": df, 
            "pd": pd, 
            "np": np
        }
        
        result, execution_output, success = execute_analysis_code(analysis_code, local_vars)
        
        if not success:
            # Return enhanced error with context
            data_context = {
                "available_columns": df.columns.tolist(),
                "data_shape": df.shape,
                "data_types": df.dtypes.astype(str).to_dict()
            }
            return handle_analysis_error(Exception(execution_output), analysis_code, data_context)
        
        # Process result
        if isinstance(result, pd.DataFrame):
            result = result.dropna(axis=1, how="all")  # Remove empty columns from result
            result_dict = {
                "type": "DataFrame",
                "shape": list(result.shape),
                "data": result.to_dict(orient="records"),
                "summary": result.describe().to_dict() if result.select_dtypes(include=[np.number]).shape[1] > 0 else {}
            }
        elif isinstance(result, pd.Series):
            result_dict = {
                "type": "Series",
                "shape": list(result.shape),
                "data": result.to_dict(),
                "summary": result.describe().to_dict() if pd.api.types.is_numeric_dtype(result) else {}
            }
        elif isinstance(result, np.ndarray):
            result_dict = {
                "type": "ndarray",
                "shape": list(result.shape),
                "value": result.tolist(),
                "raw": str(result)
            }
        else:
            result_dict = {
                "type": type(result).__name__,
                "value": str(result)
            }
        
        # Create formatted analysis result
        formatted_result = format_analysis_result(result, df, analysis_code, execution_output)
        
        response = {
            "success": True,
            "formatted_result": formatted_result,
            "data_shape": list(df.shape),
            "columns": df.columns.tolist(),
            "analysis_result": result_dict,
            "execution_output": execution_output,
            "session_info": {
                "cache_used": False,
                "analysis_count": 1,
                "source_files": [filepath]
            },
            "message": "Analysis completed successfully"
        }
        
        return json.dumps(response, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        context = {"filepath": filepath, "data_type": data_type, "analysis_code": analysis_code}
        return handle_tool_error(e, "analyze_data", context)

@mcp.tool()
def get_workflows(category: str = None) -> str:
    """
    Retrieve anomaly detection workflows from workflow.md.
    
    Args:
        category: Optional category to filter workflows (anomaly, analysis, summary, dashboard)
    
    Returns:
        JSON string with workflow documentation
    """
    import json
    
    try:
        workflow_path = os.path.join(ROOT_DIR, "workflow.md")
        
        if not os.path.exists(workflow_path):
            return json.dumps({
                "success": False, 
                "message": "workflow.md not found. Create it first with anomaly detection patterns."
            })
        
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse sections if category specified
        if category:
            lines = content.split('\n')
            in_section = False
            section_content = []
            
            for line in lines:
                if line.startswith('##') and category.lower() in line.lower():
                    in_section = True
                    section_content.append(line)
                elif line.startswith('##') and in_section:
                    break
                elif in_section:
                    section_content.append(line)
            
            if section_content:
                content = '\n'.join(section_content)
            else:
                return json.dumps({
                    "success": False,
                    "message": f"Category '{category}' not found in workflow.md"
                })
        
        return json.dumps({
            "success": True,
            "content": content,
            "message": f"Retrieved workflow documentation{' for category: ' + category if category else ''}"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error retrieving workflows: {e}")
        return json.dumps({"success": False, "message": f"Error reading workflow.md: {str(e)}"})

@mcp.tool()
def update_workflow(content: str, section: str = None, append: bool = True) -> str:
    """
    Update or append to workflow.md with new anomaly detection patterns.
    
    Args:
        content: Markdown content to add to workflow.md
        section: Optional section name to add content under
        append: If True, append to existing content. If False, replace entire file
    
    Returns:
        JSON string with update status
    """
    import json
    
    try:
        workflow_path = os.path.join(ROOT_DIR, "workflow.md")
        
        if append and os.path.exists(workflow_path):
            with open(workflow_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            if section:
                new_content = f"{existing_content}\n\n## {section}\n\n{content}"
            else:
                new_content = f"{existing_content}\n\n{content}"
        else:
            new_content = content
        
        with open(workflow_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return json.dumps({
            "success": True,
            "message": f"Successfully {'appended to' if append else 'updated'} workflow.md"
        })
        
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        return json.dumps({"success": False, "message": f"Error updating workflow.md: {str(e)}"})

@mcp.tool()
def load_data(
    filepath: str,
    data_type: str = "excel",
    sheet_name: str = None,
    range_spec: str = None,
    query: str = None
) -> str:
    """
    Load data from various sources and return basic information.
    
    Args:
        filepath: Path to the data file
        data_type: Type of data source (excel, csv, sqlite)
        sheet_name: Sheet name for Excel files (optional)
        range_spec: Range specification for Excel files (e.g., "A1:C10")
        query: SQL query for SQLite files
    
    Returns:
        JSON string with data loading information
    """
    import pandas as pd
    import json
    
    try:
        full_path = get_data_path(filepath)
        
        if not os.path.exists(full_path):
            return json.dumps({"success": False, "message": f"File not found: {full_path}"})
        
        # Load data using enhanced Excel loader
        if data_type == "excel":
            df, excel_metadata = load_excel_with_smart_headers(
                full_path, sheet_name=sheet_name, range_spec=range_spec
            )
        elif data_type == "csv":
            df = pd.read_csv(full_path)
            excel_metadata = {}
        elif data_type == "sqlite":
            import sqlite3
            conn = sqlite3.connect(full_path)
            if not query:
                return json.dumps({"success": False, "message": "SQL query required for SQLite data sources"})
            df = pd.read_sql_query(query, conn)
            conn.close()
            excel_metadata = {}
        else:
            return json.dumps({"success": False, "message": f"Unsupported data type: {data_type}"})
        
        # Remove empty columns
        df = df.dropna(axis=1, how="all")
        
        # Create comprehensive summary report
        metadata = {'source_file': filepath}
        if data_type == "excel":
            metadata.update(excel_metadata)
        
        summary_report = create_summary_report(df, metadata)
        
        result = {
            "success": True,
            "summary_report": summary_report,
            "data_shape": list(df.shape),
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "null_counts": df.isnull().sum().to_dict(),
            "message": f"Successfully loaded data from {filepath}"
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        context = {"filepath": filepath, "data_type": data_type, "sheet_name": sheet_name}
        return handle_tool_error(e, "load_data", context)

async def run_sse():
    """Run PnL MCP server in SSE mode."""
    # Assign value to DATA_FILES_PATH in SSE mode
    global DATA_FILES_PATH
    DATA_FILES_PATH = os.environ.get("DATA_FILES_PATH", "./data_files")
    # Create directory if it doesn't exist
    os.makedirs(DATA_FILES_PATH, exist_ok=True)
    
    try:
        logger.info(f"Starting PnL MCP server with SSE transport (files directory: {DATA_FILES_PATH})")
        await mcp.run_sse_async()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        await mcp.shutdown()
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")

def run_stdio():
    """Run PnL MCP server in stdio mode."""
    # No need to assign DATA_FILES_PATH in stdio mode
    
    try:
        logger.info("Starting PnL MCP server with stdio transport")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")
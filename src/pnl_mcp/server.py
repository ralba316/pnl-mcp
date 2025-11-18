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
    name="pnl-mcp",
    dependencies=["pandas>=2.0.0", "openpyxl>=3.1.2"]
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

# Global data cache for code executor
_loaded_dataframes = {}

@mcp.tool()
def analyze_data(
    filepath: str,
    analysis_code: str,
    sheet_name: str = None,
    range_spec: str = None,
    preview_mode: bool = False,
    sample_rows: int = None
) -> str:
    """
    Execute Python code on datasets. Use get_workflows('anomaly') for proven patterns.
    
    🚨 KEEP CODE SIMPLE: Single expressions or assignments only
    
    Available functions: zscore(series) - Calculate z-scores for any expression
    
    Basic usage:
    - "df.columns.tolist()" - See columns
    - "df.head()" - Preview data
    - "zscore(df['columnA'] - df['columnB'])" - Calculate z-scores
    - "df[zscore(df['columnA']).abs() > 3]" - Find outliers
    
    Args:
        filepath: Path to Excel or CSV file
        analysis_code: Python code to execute (single line)
        sheet_name: Sheet name for Excel files (optional)
        range_spec: Range specification for Excel files (e.g., "A1:C10")
        preview_mode: If True, loads only sample rows (default: False)
        sample_rows: Number of rows to sample in preview mode (default: 5)
    
    Returns:
        JSON string with analysis results
    """
    import pandas as pd
    import numpy as np
    import json
    
    try:
        full_path = get_data_path(filepath)
        
        if not os.path.exists(full_path):
            return json.dumps({"success": False, "message": f"File not found: {full_path}"})
        
        # Try to get cached DataFrame first
        cache_key = f"{filepath}_{sheet_name or 'default'}"
        if cache_key in _loaded_dataframes:
            df = _loaded_dataframes[cache_key]
            metadata = {}
            logger.info(f"Using cached DataFrame: {cache_key}")
        else:
            # Determine file type and load data
            if filepath.lower().endswith('.xlsx') or filepath.lower().endswith('.xls'):
                # Excel file
                if preview_mode and sample_rows:
                    df, metadata = load_excel_with_smart_headers(
                        full_path, sheet_name=sheet_name, range_spec=range_spec, sample_rows=sample_rows
                    )
                else:
                    df, metadata = load_excel_with_smart_headers(
                        full_path, sheet_name=sheet_name, range_spec=range_spec
                    )
            elif filepath.lower().endswith('.csv'):
                # CSV file
                if preview_mode and sample_rows:
                    df = pd.read_csv(full_path, nrows=sample_rows)
                else:
                    df = pd.read_csv(full_path)
                metadata = {}
            else:
                return json.dumps({"success": False, "message": f"Unsupported file type. Only Excel (.xlsx, .xls) and CSV files are supported."})
            
            # Cache the loaded DataFrame
            _loaded_dataframes[cache_key] = df
            logger.info(f"Loaded and cached DataFrame: {cache_key}, shape: {df.shape}")
        
        # Remove empty columns
        df = df.dropna(axis=1, how="all")
        
        # Define workflow functions for analysis
        def zscore(series):
            """Calculate z-scores for any pandas Series or expression"""
            return (series - series.mean()) / series.std()

        # Execute analysis code using enhanced executor
        local_vars = {
            "df": df, 
            "pd": pd, 
            "np": np,
            "zscore": zscore
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
        
        # Determine which columns to show in response
        if isinstance(result, pd.DataFrame):
            # If result is a DataFrame, show only its columns
            response_columns = result.columns.tolist()
            response_shape = list(result.shape)
        elif isinstance(result, pd.Series) and hasattr(result, 'index'):
            # If result is a Series, show the index as "columns"
            response_columns = [result.name] if result.name else ["series_result"]
            response_shape = [len(result), 1]
        else:
            # For scalar results, don't show all columns - just indicate result type
            response_columns = []
            response_shape = []
        
        response = {
            "success": True,
            "formatted_result": formatted_result,
            "data_shape": response_shape,
            "columns": response_columns,
            "analysis_result": result_dict,
            "execution_output": execution_output,
            "session_info": {
                "cache_used": cache_key in _loaded_dataframes,
                "analysis_count": 1,
                "source_files": [filepath]
            },
            "metadata": {
                "original_data_shape": list(df.shape),
                "total_columns_available": len(df.columns),
                "result_type": type(result).__name__
            },
            "message": "Analysis completed successfully"
        }
        
        return json.dumps(response, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        context = {"filepath": filepath, "sheet_name": sheet_name, "analysis_code": analysis_code}
        return handle_tool_error(e, "analyze_data", context)

@mcp.tool()
def preview_excel(filepath: str) -> str:
    """
    Preview all sheets and columns in an Excel file with their data types.
    
    Shows:
    - All sheet names in the workbook
    - Column names and data types for each sheet
    - Basic shape information (rows x columns)
    - Sample data preview (first few rows)
    
    Args:
        filepath: Path to Excel file (.xlsx or .xls)
        
    Returns:
        JSON string with sheet information, columns, and data types
    """
    import pandas as pd
    import json
    
    try:
        full_path = get_data_path(filepath)
        
        if not os.path.exists(full_path):
            return json.dumps({"success": False, "message": f"File not found: {full_path}"})
        
        if not (filepath.lower().endswith('.xlsx') or filepath.lower().endswith('.xls')):
            return json.dumps({"success": False, "message": "Only Excel files (.xlsx, .xls) are supported for preview"})
        
        # Read all sheet names
        excel_file = pd.ExcelFile(full_path)
        sheet_names = excel_file.sheet_names
        
        sheets_info = {}
        
        for sheet_name in sheet_names:
            # Load each sheet with minimal rows for preview
            df = pd.read_excel(full_path, sheet_name=sheet_name, nrows=5)
            
            # Get column info
            column_info = {}
            for col in df.columns:
                dtype_str = str(df[col].dtype)
                # Add sample values if available
                non_null_values = df[col].dropna()
                sample_values = non_null_values.head(3).tolist() if len(non_null_values) > 0 else []
                
                column_info[col] = {
                    "dtype": dtype_str,
                    "sample_values": sample_values,
                    "null_count": df[col].isna().sum()
                }
            
            # Get full shape by reading just the index
            full_df_shape = pd.read_excel(full_path, sheet_name=sheet_name, usecols=[0]).shape
            
            sheets_info[sheet_name] = {
                "shape": [full_df_shape[0], len(df.columns)],
                "columns": list(df.columns),
                "column_info": column_info,
                "preview_data": df.head().to_dict(orient="records")
            }
        
        response = {
            "success": True,
            "file": filepath,
            "total_sheets": len(sheet_names),
            "sheet_names": sheet_names,
            "sheets": sheets_info,
            "message": f"Successfully previewed {len(sheet_names)} sheet(s)"
        }
        
        return json.dumps(response, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error previewing Excel file: {e}")
        return json.dumps({
            "success": False, 
            "message": f"Error previewing file: {str(e)}",
            "file": filepath
        })

@mcp.tool()
def get_workflows(category: str = None) -> str:
    """
    Retrieve workflow documentation from markdown files in workflows folder.
    
    Args:
        category: Optional category to retrieve (anomaly, analysis, dashboard). 
                 If None, lists all available workflows.
    
    Returns:
        JSON string with workflow documentation
    """
    import json
    
    try:
        workflows_dir = os.path.join(ROOT_DIR, "workflows")
        
        # Create workflows directory if it doesn't exist
        if not os.path.exists(workflows_dir):
            os.makedirs(workflows_dir, exist_ok=True)
            return json.dumps({
                "success": False, 
                "message": "Workflows directory created. Please add workflow markdown files."
            })
        
        # If no category specified, list available workflows
        if category is None:
            workflow_files = [f.replace('.md', '') for f in os.listdir(workflows_dir) 
                            if f.endswith('.md')]
            
            if not workflow_files:
                return json.dumps({
                    "success": False,
                    "message": "No workflow files found in workflows directory."
                })
            
            # Read all workflows and return summary
            all_workflows = {}
            for workflow_name in workflow_files:
                file_path = os.path.join(workflows_dir, f"{workflow_name}.md")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Get first few lines as preview
                    preview_lines = content.split('\n')[:10]
                    all_workflows[workflow_name] = {
                        "preview": '\n'.join(preview_lines),
                        "full_content": content
                    }
            
            return json.dumps({
                "success": True,
                "available_workflows": workflow_files,
                "workflows": all_workflows,
                "message": f"Found {len(workflow_files)} workflow(s)"
            }, indent=2)
        
        # Load specific category workflow
        workflow_file = os.path.join(workflows_dir, f"{category.lower()}.md")
        
        if not os.path.exists(workflow_file):
            # List available workflows
            available = [f.replace('.md', '') for f in os.listdir(workflows_dir) 
                        if f.endswith('.md')]
            return json.dumps({
                "success": False,
                "message": f"Workflow '{category}' not found. Available workflows: {', '.join(available)}"
            })
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return json.dumps({
            "success": True,
            "category": category,
            "content": content,
            "message": f"Retrieved {category} workflow documentation"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error retrieving workflows: {e}")
        return json.dumps({"success": False, "message": f"Error reading workflows: {str(e)}"})

@mcp.tool()
def update_workflow(category: str, content: str, section: str = None, append: bool = True) -> str:
    """
    Update or append to workflow markdown files in workflows folder.
    
    Args:
        category: Workflow category to update (anomaly, analysis, dashboard)
        content: Markdown content to add to the workflow file
        section: Optional section name to add content under
        append: If True, append to existing content. If False, replace entire file
    
    Returns:
        JSON string with update status
    """
    import json
    
    try:
        workflows_dir = os.path.join(ROOT_DIR, "workflows")
        
        # Create workflows directory if it doesn't exist
        os.makedirs(workflows_dir, exist_ok=True)
        
        # Determine workflow file path
        workflow_file = os.path.join(workflows_dir, f"{category.lower()}.md")
        
        if append and os.path.exists(workflow_file):
            with open(workflow_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            if section:
                new_content = f"{existing_content}\n\n## {section}\n\n{content}"
            else:
                new_content = f"{existing_content}\n\n{content}"
        else:
            # If creating new file, add a title
            if not os.path.exists(workflow_file):
                title_map = {
                    'anomaly': '# 🚨 Anomaly Detection Workflows',
                    'analysis': '# 📊 Data Analysis Workflows',
                    'dashboard': '# 📈 Dashboard & Reporting Workflows'
                }
                title = title_map.get(category.lower(), f'# {category.title()} Workflows')
                new_content = f"{title}\n\n{content}"
            else:
                new_content = content
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return json.dumps({
            "success": True,
            "category": category,
            "file": workflow_file,
            "message": f"Successfully {'appended to' if append else 'updated'} {category} workflow"
        })
        
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        return json.dumps({"success": False, "message": f"Error updating {category} workflow: {str(e)}"})


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
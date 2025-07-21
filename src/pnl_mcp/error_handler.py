"""
Enhanced error handling with contextual messages and suggestions.
"""

import traceback
import sys
from typing import Dict, Any, List, Optional, Tuple
import logging
import json

logger = logging.getLogger(__name__)


class ErrorSuggestionEngine:
    """Provides contextual error suggestions and recovery mechanisms."""
    
    def __init__(self):
        self.error_patterns = {
            'file_not_found': {
                'patterns': ['no such file', 'file not found', 'does not exist'],
                'suggestions': [
                    "Verify the file path is correct and the file exists",
                    "Check that you're using the full absolute path",
                    "Ensure the file isn't locked by another application"
                ]
            },
            'permission_denied': {
                'patterns': ['permission denied', 'access denied'],
                'suggestions': [
                    "Check file permissions - you may need read access",
                    "Ensure the file isn't locked by another application",
                    "Try running with appropriate permissions"
                ]
            },
            'syntax_error': {
                'patterns': ['invalid syntax', 'unexpected token', 'unexpected indent'],
                'suggestions': [
                    "Check for missing quotes, parentheses, or brackets",
                    "Verify indentation is consistent (use spaces or tabs, not both)",
                    "Make sure all strings are properly quoted"
                ]
            },
            'name_error': {
                'patterns': ['name .* is not defined', 'undefined variable'],
                'suggestions': [
                    "Check variable names for typos",
                    "Make sure variables are defined before use",
                    "Verify you're using the correct variable name"
                ]
            },
            'attribute_error': {
                'patterns': ['has no attribute', 'object has no attribute'],
                'suggestions': [
                    "Check the method/attribute name for typos",
                    "Verify the object type supports this operation",
                    "Use dir(object) to see available attributes"
                ]
            },
            'key_error': {
                'patterns': ['keyerror', 'key .* not found'],
                'suggestions': [
                    "Check column names in your data - they might be different than expected",
                    "Use df.columns to see available column names",
                    "Check for extra spaces or special characters in column names"
                ]
            },
            'type_error': {
                'patterns': ['unsupported operand', 'cannot concatenate', 'unhashable type'],
                'suggestions': [
                    "Check data types - you might be mixing numbers and text",
                    "Use str() or int() to convert between types",
                    "Verify all operands are the correct type for the operation"
                ]
            },
            'value_error': {
                'patterns': ['invalid literal', 'cannot convert', 'malformed'],
                'suggestions': [
                    "Check data format - values might not be in expected format",
                    "Clean data first to remove invalid characters",
                    "Use error handling for data conversion operations"
                ]
            },
            'pandas_error': {
                'patterns': ['empty dataframe', 'no columns to parse', 'parser error'],
                'suggestions': [
                    "Check if your data file has the expected structure",
                    "Verify the sheet name exists in Excel files",
                    "Try specifying header row explicitly"
                ]
            },
            'excel_error': {
                'patterns': ['worksheet .* does not exist', 'excel file', 'openpyxl'],
                'suggestions': [
                    "Check that the sheet name exists in the Excel file",
                    "Verify the Excel file isn't corrupted",
                    "Use get_sheet_info() to see available sheets"
                ]
            }
        }
    
    def categorize_error(self, error: Exception, error_message: str) -> str:
        """Categorize error type based on error message."""
        error_msg_lower = error_message.lower()
        
        # Check exception type first
        if isinstance(error, FileNotFoundError) or isinstance(error, OSError):
            if 'permission' in error_msg_lower or 'access' in error_msg_lower:
                return 'permission_denied'
            else:
                return 'file_not_found'
        elif isinstance(error, SyntaxError):
            return 'syntax_error'
        elif isinstance(error, NameError):
            return 'name_error'
        elif isinstance(error, AttributeError):
            return 'attribute_error'
        elif isinstance(error, KeyError):
            return 'key_error'
        elif isinstance(error, TypeError):
            return 'type_error'
        elif isinstance(error, ValueError):
            return 'value_error'
        
        # Check patterns in error message
        for category, info in self.error_patterns.items():
            for pattern in info['patterns']:
                if pattern in error_msg_lower:
                    return category
        
        return 'unknown'
    
    def get_suggestions(self, error_category: str, context: Dict[str, Any] = None) -> List[str]:
        """Get suggestions for error category."""
        if error_category in self.error_patterns:
            suggestions = self.error_patterns[error_category]['suggestions'].copy()
            
            # Add context-specific suggestions
            if context:
                if error_category == 'key_error' and 'available_columns' in context:
                    suggestions.append(f"Available columns: {', '.join(context['available_columns'])}")
                elif error_category == 'excel_error' and 'available_sheets' in context:
                    suggestions.append(f"Available sheets: {', '.join(context['available_sheets'])}")
            
            return suggestions
        
        return ["Try breaking the operation into smaller steps", "Check the documentation for correct usage"]
    
    def format_error_response(self, error: Exception, context: Dict[str, Any] = None, 
                            operation: str = None) -> Dict[str, Any]:
        """Format a comprehensive error response."""
        error_message = str(error)
        error_category = self.categorize_error(error, error_message)
        suggestions = self.get_suggestions(error_category, context)
        
        # Get traceback info
        tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
        
        # Extract line number if available
        line_number = None
        if hasattr(error, 'lineno'):
            line_number = error.lineno
        elif tb_lines:
            # Try to extract line number from traceback
            for line in tb_lines:
                if 'line' in line and ', in' in line:
                    try:
                        line_number = int(line.split('line ')[1].split(',')[0])
                        break
                    except (IndexError, ValueError):
                        pass
        
        response = {
            "success": False,
            "error": {
                "type": type(error).__name__,
                "message": error_message,
                "category": error_category,
                "line_number": line_number,
                "operation": operation or "unknown"
            },
            "suggestions": suggestions,
            "context": context or {},
            "troubleshooting": {
                "quick_fixes": self._get_quick_fixes(error_category),
                "next_steps": self._get_next_steps(error_category)
            }
        }
        
        # Add debug info if needed
        if logger.isEnabledFor(logging.DEBUG):
            response["debug"] = {
                "traceback": tb_lines,
                "full_context": context
            }
        
        return response
    
    def _get_quick_fixes(self, error_category: str) -> List[str]:
        """Get quick fixes for common errors."""
        quick_fixes = {
            'file_not_found': ["Check file path", "Verify file exists"],
            'syntax_error': ["Check quotes and brackets", "Fix indentation"],
            'name_error': ["Check variable spelling", "Define variable first"],
            'key_error': ["Check column names", "Use df.columns to list"],
            'type_error': ["Convert data types", "Check operand types"],
            'excel_error': ["Check sheet name", "Verify file format"]
        }
        return quick_fixes.get(error_category, ["Review code syntax", "Check data format"])
    
    def _get_next_steps(self, error_category: str) -> List[str]:
        """Get next steps for error recovery."""
        next_steps = {
            'file_not_found': ["Use absolute paths", "Check file permissions"],
            'syntax_error': ["Use an IDE with syntax highlighting", "Test code in smaller pieces"],
            'name_error': ["Use descriptive variable names", "Initialize variables"],
            'key_error': ["Preview data structure first", "Handle missing keys gracefully"],
            'type_error': ["Add type checking", "Use pandas methods for data operations"],
            'excel_error': ["Use preview_data to explore structure", "Check Excel file manually"]
        }
        return next_steps.get(error_category, ["Read documentation", "Seek help from community"])


class ContextualErrorHandler:
    """Main error handler with context awareness."""
    
    def __init__(self):
        self.suggestion_engine = ErrorSuggestionEngine()
    
    def handle_tool_error(self, error: Exception, tool_name: str, 
                         parameters: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Handle errors from MCP tools with context.
        
        Args:
            error: The exception that occurred
            tool_name: Name of the tool that failed
            parameters: Parameters passed to the tool
            context: Additional context information
            
        Returns:
            JSON string with error details and suggestions
        """
        # Build context
        full_context = {
            "tool": tool_name,
            "parameters": parameters
        }
        if context:
            full_context.update(context)
        
        # Format error response
        error_response = self.suggestion_engine.format_error_response(
            error, full_context, tool_name
        )
        
        # Log the error
        logger.error(f"Tool {tool_name} failed: {str(error)}", exc_info=True)
        
        return json.dumps(error_response, indent=2, default=str)
    
    def handle_analysis_error(self, error: Exception, code: str, 
                            data_context: Dict[str, Any] = None) -> str:
        """
        Handle errors from data analysis code execution.
        
        Args:
            error: The exception that occurred
            code: The analysis code that failed
            data_context: Information about the data being analyzed
            
        Returns:
            JSON string with error details and suggestions
        """
        context = {
            "operation": "analysis",
            "code_snippet": code[:200] + "..." if len(code) > 200 else code
        }
        
        if data_context:
            context.update(data_context)
        
        error_response = self.suggestion_engine.format_error_response(
            error, context, "analyze_data"
        )
        
        # Detect code complexity and add simplicity suggestions
        code_lines = code.strip().split('\n')
        is_complex = (
            len(code_lines) > 2 or  # Multi-line code
            'print(' in code or      # Print statements
            ' = ' in code and len([line for line in code_lines if ' = ' in line]) > 1 or  # Multiple assignments
            'import ' in code or     # Import statements
            'def ' in code or        # Function definitions
            'for ' in code or        # Loops
            'if ' in code or         # Conditionals
            'try:' in code           # Error handling
        )
        
        # Add simplicity-focused suggestions at the top
        simplicity_suggestions = []
        
        if isinstance(error, KeyError):
            if data_context and 'available_columns' in data_context:
                column_names = data_context['available_columns']
                error_msg = str(error).strip("'\"")
                # Find similar column names
                similar_cols = [col for col in column_names if error_msg.lower() in col.lower()]
                if similar_cols:
                    simplicity_suggestions.append(f"Column '{error_msg}' not found. Try: {similar_cols[:3]}")
                else:
                    simplicity_suggestions.append(f"Column '{error_msg}' doesn't exist. First try: df.columns.tolist()")
            simplicity_suggestions.append("SIMPLE FIX: Start with df.columns.tolist() to see available columns")
        
        if isinstance(error, SyntaxError):
            simplicity_suggestions.append("🚨 CODE TOO COMPLEX: Use single operations like df.head() or df['column'].describe()")
            simplicity_suggestions.append("Break your analysis into multiple simple steps")
        
        if is_complex:
            simplicity_suggestions.extend([
                "⚠️ Your code is too complex for analyze_data tool",
                "Use ONE simple operation per call: df.head(), df['column'].max(), etc.",
                "For complex analysis, make multiple separate tool calls"
            ])
        
        # Add column-specific help if available
        if data_context and 'available_columns' in data_context:
            key_columns = [col for col in data_context['available_columns'] 
                          if any(keyword in col for keyword in ['Impact', 'Inp', 'PNL', 'Delta'])]
            if key_columns:
                simplicity_suggestions.append(f"KEY COLUMNS: {', '.join(key_columns[:5])}")
        
        # Insert simplicity suggestions at the beginning
        error_response["suggestions"] = simplicity_suggestions + error_response["suggestions"]
        
        # Add simple example suggestions
        error_response["simple_examples"] = [
            "df.columns.tolist()",
            "df.head()",
            "df['Base Impact of Delta'].describe()",
            "df[df['Inp Today'] > 0]",
            "df['Inp Today'] - df['Inp Yesterday']"
        ]
        
        logger.error(f"Analysis code failed: {str(error)}", exc_info=True)
        
        return json.dumps(error_response, indent=2, default=str)
    
    def wrap_tool_execution(self, tool_func, tool_name: str, *args, **kwargs):
        """
        Wrapper for tool execution with error handling.
        
        Args:
            tool_func: The tool function to execute
            tool_name: Name of the tool
            *args, **kwargs: Arguments for the tool function
            
        Returns:
            Tool result or error response
        """
        try:
            return tool_func(*args, **kwargs)
        except Exception as e:
            context = {
                "args": str(args)[:200],
                "kwargs": {k: str(v)[:100] for k, v in kwargs.items()}
            }
            return self.handle_tool_error(e, tool_name, kwargs, context)


# Global error handler instance
_error_handler = ContextualErrorHandler()

def handle_tool_error(error: Exception, tool_name: str, 
                     parameters: Dict[str, Any], context: Dict[str, Any] = None) -> str:
    """Handle tool errors with context and suggestions."""
    return _error_handler.handle_tool_error(error, tool_name, parameters, context)

def handle_analysis_error(error: Exception, code: str, 
                        data_context: Dict[str, Any] = None) -> str:
    """Handle analysis code errors with context and suggestions."""
    return _error_handler.handle_analysis_error(error, code, data_context)

def wrap_tool_execution(tool_func, tool_name: str):
    """Decorator for tool execution with error handling."""
    def wrapper(*args, **kwargs):
        return _error_handler.wrap_tool_execution(tool_func, tool_name, *args, **kwargs)
    return wrapper
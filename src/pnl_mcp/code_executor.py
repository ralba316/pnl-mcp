"""
Enhanced code execution engine for PnL MCP Server.
Supports multi-line code blocks, proper error handling, and safe execution.
"""

import sys
import traceback
from io import StringIO
from typing import Any, Dict, Tuple, List
import ast
import textwrap


class CodeExecutionError(Exception):
    """Custom exception for code execution errors."""
    def __init__(self, message: str, line_number: int = None, suggestion: str = None):
        self.message = message
        self.line_number = line_number
        self.suggestion = suggestion
        super().__init__(message)


class SafeCodeExecutor:
    """Safe execution environment for user analysis code."""
    
    def __init__(self):
        self.safe_builtins = {
            "__builtins__": {
                # Basic functions
                "len": len, "sum": sum, "min": min, "max": max, "round": round,
                "range": range, "enumerate": enumerate, "zip": zip, "sorted": sorted,
                "abs": abs, "str": str, "int": int, "float": float, "bool": bool,
                
                # Data structures
                "list": list, "dict": dict, "tuple": tuple, "set": set,
                
                # Output
                "print": print,
                
                # Type checking
                "type": type, "isinstance": isinstance,
                
                # Math
                "pow": pow, "divmod": divmod,
                
                # Iteration
                "map": map, "filter": filter, "any": any, "all": all,
            }
        }
    
    def _prepare_code(self, code: str) -> str:
        """Prepare code for execution by handling indentation and formatting."""
        # Remove common leading whitespace (dedent)
        code = textwrap.dedent(code).strip()
        
        # Split into lines for analysis
        lines = code.split('\n')
        
        # Check if it's a single expression or multiple statements
        try:
            # Try to parse as expression first
            ast.parse(code, mode='eval')
            return code  # It's a single expression
        except SyntaxError:
            # It's multiple statements, return as is
            return code
    
    def _is_expression(self, code: str) -> bool:
        """Check if code is a single expression."""
        try:
            ast.parse(code, mode='eval')
            return True
        except SyntaxError:
            return False
    
    def _get_error_suggestion(self, error: Exception, code: str) -> str:
        """Generate helpful suggestions based on error type."""
        error_msg = str(error).lower()
        
        if isinstance(error, SyntaxError):
            if "invalid syntax" in error_msg:
                return "Check for missing quotes, parentheses, or proper indentation"
            elif "unexpected indent" in error_msg:
                return "Remove extra indentation or ensure consistent spacing"
            elif "unmatched" in error_msg:
                return "Check for unmatched parentheses, brackets, or quotes"
        
        elif isinstance(error, NameError):
            if "not defined" in error_msg:
                return "Make sure variable names are spelled correctly and defined before use"
        
        elif isinstance(error, AttributeError):
            return "Check that the object has the method/attribute you're trying to access"
        
        elif isinstance(error, KeyError):
            return "Verify the column/key name exists in your data"
        
        elif isinstance(error, TypeError):
            if "unsupported operand" in error_msg:
                return "Check data types - you might be mixing numbers and text"
        
        return "Try breaking complex operations into smaller steps"
    
    def execute_code(self, code: str, local_vars: Dict[str, Any]) -> Tuple[Any, str, bool]:
        """
        Execute code safely and return result, output, and success status.
        
        Args:
            code: Python code to execute
            local_vars: Local variables available to the code
            
        Returns:
            Tuple of (result, output_text, success)
        """
        # Prepare code
        prepared_code = self._prepare_code(code)
        
        # Capture stdout
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Create execution environment
            exec_globals = self.safe_builtins.copy()
            exec_locals = local_vars.copy()
            
            # Check if it's an expression or statements
            if self._is_expression(prepared_code):
                # Single expression - use eval
                result = eval(prepared_code, exec_globals, exec_locals)
            else:
                # Multiple statements - use exec
                exec(prepared_code, exec_globals, exec_locals)
                
                # Try to get the result from the last expression if any
                lines = prepared_code.strip().split('\n')
                last_line = lines[-1].strip()
                
                # If last line looks like an expression, evaluate it
                if last_line and not last_line.startswith(('print', 'if', 'for', 'while', 'def', 'class', 'import', 'from')):
                    try:
                        if self._is_expression(last_line):
                            result = eval(last_line, exec_globals, exec_locals)
                        else:
                            result = None
                    except:
                        result = None
                else:
                    result = None
            
            # Get captured output
            output_text = captured_output.getvalue()
            
            return result, output_text, True
            
        except Exception as e:
            # Get line number if available
            line_number = None
            if hasattr(e, 'lineno'):
                line_number = e.lineno
            
            # Generate suggestion
            suggestion = self._get_error_suggestion(e, prepared_code)
            
            # Create detailed error message
            error_msg = f"Error: {str(e)}"
            if line_number:
                error_msg += f" (line {line_number})"
            if suggestion:
                error_msg += f"\nSuggestion: {suggestion}"
            
            return None, error_msg, False
            
        finally:
            # Restore stdout
            sys.stdout = old_stdout
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate code syntax without executing it.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            prepared_code = self._prepare_code(code)
            ast.parse(prepared_code)
            return True, ""
        except SyntaxError as e:
            suggestion = self._get_error_suggestion(e, code)
            error_msg = f"Syntax Error: {str(e)}"
            if suggestion:
                error_msg += f"\nSuggestion: {suggestion}"
            return False, error_msg
        except Exception as e:
            return False, f"Validation Error: {str(e)}"


# Global executor instance
_executor = SafeCodeExecutor()

def execute_analysis_code(code: str, local_vars: Dict[str, Any]) -> Tuple[Any, str, bool]:
    """
    Execute analysis code safely.
    
    Args:
        code: Python code to execute
        local_vars: Local variables (including df, pd, np, etc.)
        
    Returns:
        Tuple of (result, output_text, success)
    """
    return _executor.execute_code(code, local_vars)

def validate_analysis_code(code: str) -> Tuple[bool, str]:
    """
    Validate analysis code syntax.
    
    Args:
        code: Python code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    return _executor.validate_code(code)
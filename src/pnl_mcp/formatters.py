"""
Output formatters for enhanced user-friendly analysis results.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union, Optional
import json
from datetime import datetime
import re


class AnalysisFormatter:
    """Formats analysis results into user-friendly output."""
    
    def __init__(self):
        self.financial_columns = [
            'pnl', 'profit', 'loss', 'delta', 'gamma', 'vega', 'theta',
            'realized', 'unrealized', 'value', 'rate', 'price', 'amount',
            'cost', 'revenue', 'margin', 'impact'
        ]
    
    def _is_financial_column(self, col_name: str) -> bool:
        """Check if column appears to be financial data."""
        col_lower = col_name.lower()
        return any(term in col_lower for term in self.financial_columns)
    
    def _format_currency(self, value: Union[float, int], currency: str = '$') -> str:
        """Format numeric value as currency."""
        if pd.isna(value):
            return "N/A"
        
        try:
            value = float(value)
            if abs(value) >= 1e9:
                return f"{currency}{value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"{currency}{value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"{currency}{value/1e3:.2f}K"
            else:
                return f"{currency}{value:,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_percentage(self, value: Union[float, int]) -> str:
        """Format numeric value as percentage."""
        if pd.isna(value):
            return "N/A"
        
        try:
            return f"{float(value):.2%}"
        except (ValueError, TypeError):
            return str(value)
    
    def _create_ascii_bar_chart(self, data: Dict[str, float], title: str = "Chart", 
                               max_width: int = 40) -> str:
        """Create ASCII bar chart."""
        if not data:
            return "No data to display"
        
        # Find max value for scaling
        max_val = max(abs(v) for v in data.values() if pd.notna(v))
        if max_val == 0:
            max_val = 1
        
        chart_lines = [f"\n{title}", "=" * len(title)]
        
        for key, value in data.items():
            if pd.isna(value):
                bar = "N/A"
                value_str = "N/A"
            else:
                # Calculate bar length
                bar_length = int((abs(value) / max_val) * max_width)
                bar = "█" * bar_length
                
                # Format value
                if self._is_financial_column(key):
                    value_str = self._format_currency(value)
                else:
                    value_str = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
            
            # Truncate long keys
            display_key = key[:15] + "..." if len(key) > 18 else key
            chart_lines.append(f"{display_key:<20} {bar:<{max_width}} {value_str}")
        
        return "\n".join(chart_lines)
    
    def _summarize_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create summary statistics for DataFrame."""
        summary = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "missing_data": df.isnull().sum().to_dict(),
        }
        
        # Numeric summaries
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = {
                col: {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "count": df[col].count()
                }
                for col in numeric_cols
            }
        
        # Financial summaries for PnL data
        financial_cols = [col for col in df.columns if self._is_financial_column(col)]
        if financial_cols:
            summary["financial_summary"] = {}
            for col in financial_cols:
                if df[col].dtype in ['int64', 'float64']:
                    summary["financial_summary"][col] = {
                        "total": df[col].sum(),
                        "positive_count": (df[col] > 0).sum(),
                        "negative_count": (df[col] < 0).sum(),
                        "largest_gain": df[col].max(),
                        "largest_loss": df[col].min()
                    }
        
        return summary
    
    def format_preview_result(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
        """Format preview data result with enhanced summary."""
        # Basic info
        result_lines = [
            "📊 DATA PREVIEW SUMMARY",
            "=" * 30,
            f"📁 File: {metadata.get('source_file', 'Unknown')}",
            f"📋 Sheet: {metadata.get('sheet_name', 'Unknown')}",
            f"📏 Dimensions: {df.shape[0]} rows × {df.shape[1]} columns",
        ]
        
        # Available sheets
        if 'available_sheets' in metadata:
            sheets = metadata['available_sheets']
            result_lines.append(f"📑 Available sheets: {', '.join(sheets)}")
        
        # Data quality
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            result_lines.append(f"⚠️  Missing values: {null_counts.sum()} total")
        else:
            result_lines.append("✅ No missing values detected")
        
        result_lines.append("")
        
        # Column information
        result_lines.append("📋 COLUMN INFORMATION")
        result_lines.append("-" * 20)
        for i, (col, dtype) in enumerate(df.dtypes.items(), 1):
            null_count = df[col].isnull().sum()
            result_lines.append(f"{i:2d}. {col} ({dtype}) - {null_count} nulls")
        
        result_lines.append("")
        
        # Sample data
        result_lines.append("🔍 SAMPLE DATA")
        result_lines.append("-" * 15)
        
        # Show first few rows in a clean format
        sample_df = df.head(3)
        for idx, row in sample_df.iterrows():
            result_lines.append(f"Row {idx + 1}:")
            for col in sample_df.columns:
                value = row[col]
                if pd.notna(value):
                    if self._is_financial_column(col) and isinstance(value, (int, float)):
                        formatted_value = self._format_currency(value)
                    else:
                        formatted_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    result_lines.append(f"  {col}: {formatted_value}")
            result_lines.append("")
        
        # Financial summary if applicable
        financial_cols = [col for col in df.columns if self._is_financial_column(col)]
        if financial_cols:
            result_lines.append("💰 FINANCIAL SUMMARY")
            result_lines.append("-" * 20)
            
            for col in financial_cols[:5]:  # Show top 5 financial columns
                if df[col].dtype in ['int64', 'float64']:
                    total = df[col].sum()
                    result_lines.append(f"{col}: {self._format_currency(total)}")
        
        return "\n".join(result_lines)
    
    def format_analysis_result(self, result: Any, df: pd.DataFrame, code: str,
                             execution_output: str = None) -> str:
        """Format analysis result with context and insights."""
        result_lines = [
            "🧮 ANALYSIS RESULTS",
            "=" * 25,
            f"📊 Data: {df.shape[0]} rows × {df.shape[1]} columns",
        ]
        
        # Show code if it's not too long
        if len(code) <= 200:
            result_lines.extend([
                f"💻 Code: {code}",
                ""
            ])
        
        # Show execution output if any
        if execution_output and execution_output.strip():
            result_lines.extend([
                "📝 OUTPUT:",
                "-" * 10,
                execution_output.strip(),
                ""
            ])
        
        # Format the result based on type
        if isinstance(result, pd.DataFrame):
            result_lines.extend(self._format_dataframe_result(result))
        elif isinstance(result, pd.Series):
            result_lines.extend(self._format_series_result(result))
        elif isinstance(result, (int, float)):
            result_lines.extend(self._format_numeric_result(result, code))
        elif isinstance(result, dict):
            result_lines.extend(self._format_dict_result(result))
        else:
            result_lines.extend([
                "📋 RESULT:",
                f"Type: {type(result).__name__}",
                f"Value: {str(result)[:500]}" + ("..." if len(str(result)) > 500 else "")
            ])
        
        return "\n".join(result_lines)
    
    def _format_dataframe_result(self, df: pd.DataFrame) -> List[str]:
        """Format DataFrame result."""
        lines = [
            "📊 DATAFRAME RESULT:",
            f"Shape: {df.shape[0]} rows × {df.shape[1]} columns",
            ""
        ]
        
        # Show column info
        lines.append("Columns:")
        for col in df.columns:
            lines.append(f"  • {col} ({df[col].dtype})")
        lines.append("")
        
        # Show sample data
        lines.append("Sample data:")
        sample_size = min(3, len(df))
        for i in range(sample_size):
            lines.append(f"Row {i+1}:")
            for col in df.columns:
                value = df.iloc[i][col]
                if self._is_financial_column(col) and isinstance(value, (int, float)):
                    formatted_value = self._format_currency(value)
                else:
                    formatted_value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                lines.append(f"  {col}: {formatted_value}")
            lines.append("")
        
        # Financial summary if applicable
        financial_cols = [col for col in df.columns if self._is_financial_column(col)]
        if financial_cols:
            lines.append("💰 Financial Summary:")
            for col in financial_cols:
                if df[col].dtype in ['int64', 'float64']:
                    total = df[col].sum()
                    lines.append(f"  {col}: {self._format_currency(total)}")
        
        return lines
    
    def _format_series_result(self, series: pd.Series) -> List[str]:
        """Format Series result."""
        lines = [
            "📈 SERIES RESULT:",
            f"Length: {len(series)}",
            f"Name: {series.name or 'Unnamed'}",
            ""
        ]
        
        # Show top values
        lines.append("Top values:")
        top_values = series.head(5)
        for idx, value in top_values.items():
            if isinstance(value, (int, float)) and self._is_financial_column(str(series.name or "")):
                formatted_value = self._format_currency(value)
            else:
                formatted_value = str(value)
            lines.append(f"  {idx}: {formatted_value}")
        
        # Summary stats for numeric series
        if pd.api.types.is_numeric_dtype(series):
            lines.extend([
                "",
                "📊 Statistics:",
                f"  Mean: {series.mean():.2f}",
                f"  Median: {series.median():.2f}",
                f"  Std: {series.std():.2f}",
                f"  Min: {series.min():.2f}",
                f"  Max: {series.max():.2f}"
            ])
        
        return lines
    
    def _format_numeric_result(self, value: Union[int, float], code: str) -> List[str]:
        """Format numeric result with context."""
        lines = ["🔢 NUMERIC RESULT:"]
        
        # Format based on likely context
        if any(term in code.lower() for term in ['sum', 'total', 'pnl', 'profit', 'loss']):
            formatted_value = self._format_currency(value)
        elif any(term in code.lower() for term in ['percent', 'rate', '%']):
            formatted_value = self._format_percentage(value)
        else:
            formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        
        lines.append(f"Value: {formatted_value}")
        
        # Add context
        if isinstance(value, (int, float)):
            lines.extend([
                "",
                "Context:",
                f"  Raw value: {value}",
                f"  Type: {type(value).__name__}",
                f"  Scientific: {value:.2e}" if abs(value) > 1000 or abs(value) < 0.01 else ""
            ])
        
        return [line for line in lines if line]  # Remove empty lines
    
    def _format_dict_result(self, data: dict) -> List[str]:
        """Format dictionary result."""
        lines = [
            "📋 DICTIONARY RESULT:",
            f"Keys: {len(data)}",
            ""
        ]
        
        # Show key-value pairs
        for key, value in list(data.items())[:10]:  # Show first 10 items
            if isinstance(value, (int, float)) and self._is_financial_column(str(key)):
                formatted_value = self._format_currency(value)
            else:
                formatted_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            lines.append(f"  {key}: {formatted_value}")
        
        if len(data) > 10:
            lines.append(f"  ... and {len(data) - 10} more items")
        
        return lines
    
    def create_summary_report(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
        """Create comprehensive summary report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = [
            "📊 COMPREHENSIVE DATA ANALYSIS REPORT",
            "=" * 45,
            f"Generated: {timestamp}",
            f"File: {metadata.get('source_file', 'Unknown')}",
            "",
            "🔍 OVERVIEW",
            "-" * 12,
            f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns",
            f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            f"Data completeness: {((df.size - df.isnull().sum().sum()) / df.size * 100):.1f}%",
            ""
        ]
        
        # Column analysis
        lines.extend([
            "📋 COLUMN ANALYSIS",
            "-" * 18
        ])
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        text_cols = df.select_dtypes(include=['object']).columns
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        
        lines.extend([
            f"Numeric columns: {len(numeric_cols)}",
            f"Text columns: {len(text_cols)}",
            f"Date columns: {len(datetime_cols)}",
            ""
        ])
        
        # Financial analysis for PnL data
        financial_cols = [col for col in df.columns if self._is_financial_column(col)]
        if financial_cols:
            lines.extend([
                "💰 FINANCIAL ANALYSIS",
                "-" * 21
            ])
            
            total_pnl = 0
            for col in financial_cols:
                if df[col].dtype in ['int64', 'float64']:
                    col_sum = df[col].sum()
                    total_pnl += col_sum
                    lines.append(f"{col}: {self._format_currency(col_sum)}")
            
            lines.extend([
                f"Total Financial Impact: {self._format_currency(total_pnl)}",
                ""
            ])
            
            # Create chart for top financial columns
            if len(financial_cols) > 1:
                chart_data = {}
                for col in financial_cols[:5]:
                    if df[col].dtype in ['int64', 'float64']:
                        chart_data[col] = df[col].sum()
                
                if chart_data:
                    chart = self._create_ascii_bar_chart(chart_data, "Top Financial Columns")
                    lines.append(chart)
                    lines.append("")
        
        # Data quality issues
        quality_issues = []
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            quality_issues.append(f"Missing values: {null_counts.sum()} total")
        
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            quality_issues.append(f"Duplicate rows: {duplicates}")
        
        if quality_issues:
            lines.extend([
                "⚠️  DATA QUALITY ISSUES",
                "-" * 24
            ])
            lines.extend(f"• {issue}" for issue in quality_issues)
            lines.append("")
        
        # Recommendations
        lines.extend([
            "💡 RECOMMENDATIONS",
            "-" * 18,
            "• Use preview_data() to explore data structure",
            "• Check for missing values before analysis",
            "• Consider data type conversions for better performance"
        ])
        
        if financial_cols:
            lines.append("• Focus analysis on financial columns for P&L insights")
        
        return "\n".join(lines)


# Global formatter instance
_formatter = AnalysisFormatter()

def format_preview_result(df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
    """Format preview result with enhanced summary."""
    return _formatter.format_preview_result(df, metadata)

def format_analysis_result(result: Any, df: pd.DataFrame, code: str, execution_output: str = None) -> str:
    """Format analysis result with context and insights."""
    return _formatter.format_analysis_result(result, df, code, execution_output)

def create_summary_report(df: pd.DataFrame, metadata: Dict[str, Any]) -> str:
    """Create comprehensive summary report."""
    return _formatter.create_summary_report(df, metadata)
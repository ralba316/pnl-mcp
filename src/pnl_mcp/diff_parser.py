"""
Unified diff format parser for more intuitive edit operations.
Supports standard git diff format for file editing.
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DiffHunk:
    """Represents a single hunk in a unified diff."""
    start_line: int
    line_count: int
    new_start: int
    new_count: int
    changes: List[Tuple[str, str]]  # (operation, content)


class UnifiedDiffParser:
    """Parse and apply unified diff format changes to files."""
    
    HUNK_HEADER_PATTERN = re.compile(
        r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'
    )
    
    def __init__(self):
        self.hunks: List[DiffHunk] = []
    
    def parse_diff(self, diff_text: str) -> List[DiffHunk]:
        """
        Parse unified diff format into structured hunks.
        
        Args:
            diff_text: Unified diff format text
            
        Returns:
            List of DiffHunk objects
        """
        lines = diff_text.split('\n')
        hunks = []
        current_hunk = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for hunk header
            match = self.HUNK_HEADER_PATTERN.match(line)
            if match:
                # Save previous hunk if exists
                if current_hunk:
                    hunks.append(current_hunk)
                
                # Parse hunk header
                start_line = int(match.group(1))
                line_count = int(match.group(2)) if match.group(2) else 1
                new_start = int(match.group(3))
                new_count = int(match.group(4)) if match.group(4) else 1
                
                current_hunk = DiffHunk(
                    start_line=start_line,
                    line_count=line_count,
                    new_start=new_start,
                    new_count=new_count,
                    changes=[]
                )
            elif current_hunk:
                # Process diff content
                if line.startswith('+'):
                    # Addition
                    content = line[1:] if len(line) > 1 else ''
                    current_hunk.changes.append(('add', content))
                elif line.startswith('-'):
                    # Deletion
                    content = line[1:] if len(line) > 1 else ''
                    current_hunk.changes.append(('delete', content))
                elif line.startswith(' '):
                    # Context line (unchanged)
                    content = line[1:] if len(line) > 1 else ''
                    current_hunk.changes.append(('context', content))
                elif line.startswith('\\'):
                    # Special marker (e.g., "\ No newline at end of file")
                    pass
            
            i += 1
        
        # Add final hunk
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def apply_diff_to_content(self, original_content: str, diff_text: str) -> str:
        """
        Apply unified diff to original content.
        
        Args:
            original_content: Original file content
            diff_text: Unified diff format changes
            
        Returns:
            Modified content
        """
        lines = original_content.split('\n') if original_content else []
        hunks = self.parse_diff(diff_text)
        
        # Apply hunks in reverse order to maintain line numbers
        for hunk in reversed(hunks):
            lines = self._apply_hunk(lines, hunk)
        
        return '\n'.join(lines)
    
    def _apply_hunk(self, lines: List[str], hunk: DiffHunk) -> List[str]:
        """
        Apply a single hunk to the content lines.
        
        Unified diff line numbers are 1-based and indicate:
        - For insertions (@@ -L,0 +L,N @@): Insert N lines AFTER line L
        - For deletions (@@ -L,N +L,0 @@): Delete N lines STARTING at line L
        - For replacements (@@ -L,N +L,M @@): Replace N lines starting at L with M lines
        """
        result = []
        
        # Convert 1-based line number to 0-based index
        # Line 1 in diff = index 0 in array
        start_idx = hunk.start_line - 1
        
        if hunk.line_count == 0:
            # Pure insertion: Insert after the specified line
            # @@ -3,0 +3,2 @@ means: insert 2 lines after line 3
            
            # Special case: inserting at the beginning (line 0)
            if hunk.start_line == 0:
                # Insert at the very beginning
                for op, content in hunk.changes:
                    if op == 'add':
                        result.append(content)
                result.extend(lines)
            else:
                # Normal case: insert after a specific line
                # Include all lines up to and including the target line
                if start_idx >= 0 and start_idx < len(lines):
                    result.extend(lines[:start_idx + 1])
                elif start_idx >= len(lines):
                    # Inserting after the last line
                    result.extend(lines)
                
                # Add the new content
                for op, content in hunk.changes:
                    if op == 'add':
                        result.append(content)
                
                # Add remaining lines
                if start_idx + 1 < len(lines):
                    result.extend(lines[start_idx + 1:])
        else:
            # Operations involving existing lines (delete, replace, or context)
            
            # Add all lines before the hunk starts
            if start_idx > 0:
                result.extend(lines[:start_idx])
            
            # Process hunk changes
            original_idx = start_idx
            for op, content in hunk.changes:
                if op == 'add':
                    result.append(content)
                elif op == 'delete':
                    # Skip the deleted line (just advance the index)
                    if original_idx < len(lines):
                        original_idx += 1
                elif op == 'context':
                    # Keep unchanged line
                    if original_idx < len(lines):
                        result.append(lines[original_idx])
                        original_idx += 1
            
            # Add remaining lines after the hunk
            if original_idx < len(lines):
                result.extend(lines[original_idx:])
        
        return result
    
    def create_diff_from_edit(self, edit_request: Dict[str, Any]) -> str:
        """
        Convert a simple edit request to unified diff format.
        
        Args:
            edit_request: Dictionary with 'operation', 'line', 'content'
            
        Returns:
            Unified diff format string
        """
        operation = edit_request.get('operation', 'add')
        line = edit_request.get('line', 1)
        content = edit_request.get('content', '')
        
        if operation == 'add':
            # Adding content after specified line
            lines = content.split('\n')
            diff_lines = [
                f"@@ -{line},0 +{line},{len(lines)} @@"
            ]
            for content_line in lines:
                diff_lines.append(f"+{content_line}")
            return '\n'.join(diff_lines)
        
        elif operation == 'delete':
            # Deleting lines
            count = edit_request.get('count', 1)
            diff_lines = [
                f"@@ -{line},{count} +{line},0 @@"
            ]
            for i in range(count):
                diff_lines.append(f"-<line {line + i} content>")
            return '\n'.join(diff_lines)
        
        elif operation == 'replace':
            # Replacing lines
            old_count = edit_request.get('old_count', 1)
            new_lines = content.split('\n')
            diff_lines = [
                f"@@ -{line},{old_count} +{line},{len(new_lines)} @@"
            ]
            for i in range(old_count):
                diff_lines.append(f"-<old line {line + i} content>")
            for new_line in new_lines:
                diff_lines.append(f"+{new_line}")
            return '\n'.join(diff_lines)
        
        return ""


def insert_content_after_line(file_path: str, line_number: int, content: str) -> bool:
    """
    Helper function to insert content after a specific line using unified diff format.
    
    Args:
        file_path: Path to the file to modify
        line_number: Line number to insert after (1-based, 0 for beginning)
        content: Content to insert (can be multi-line)
        
    Returns:
        True if successful, False otherwise
    """
    lines = content.split('\n') if content else []
    diff_lines = [f"@@ -{line_number},0 +{line_number},{len(lines)} @@"]
    for line in lines:
        diff_lines.append(f"+{line}")
    diff_text = '\n'.join(diff_lines)
    
    return apply_unified_diff(file_path, diff_text)


def apply_unified_diff(file_path: str, diff_text: str) -> bool:
    """
    Apply unified diff format changes to a file.
    
    Args:
        file_path: Path to the file to modify
        diff_text: Unified diff format changes
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read original content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except FileNotFoundError:
            original_content = ""
        
        # Apply diff
        parser = UnifiedDiffParser()
        modified_content = parser.apply_diff_to_content(original_content, diff_text)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return True
    except Exception as e:
        print(f"Error applying diff: {e}")
        return False


# Example usage for the Omega Greek documentation
OMEGA_DIFF = """@@ -80,0 +80,82 @@
+
+## Omega Greek
+
+### Overview
+
+Omega, also known as elasticity or percentage delta, measures the percentage change in an option's value relative to the percentage change in the underlying asset's price. Unlike delta, which measures absolute price sensitivity, omega provides a leveraged measure of sensitivity that is particularly useful for comparing options with different strike prices and expirations.
+
+### Mathematical Definition
+
+Omega is calculated as:
+
+**Ω = (Δ × S) / V**
+
+Where:
+- **Ω** (Omega) = Elasticity of the option
+- **Δ** (Delta) = First-order price sensitivity
+- **S** = Current price of the underlying asset
+- **V** = Current value of the option
+
+**Alternative Formula**:
+
+**Ω = %ΔV / %ΔS**
+
+Where **%ΔV** is the percentage change in option value and **%ΔS** is the percentage change in underlying price.
+
+### Result ID
+
+350 (Proposed)
+
+### Result Enumeration
+
+OMEGA_BY_LEG_RESULT
+
+### Result Class
+
+Leg Result
+
+### Toolsets
+
+This result works for the following option-based toolsets:
+- ComOpt (Commodity Options)
+- ComOptFut (Commodity Futures Options)
+- MetalOpt (Metal Options)
+- EngyLTP (Energy Long Term Power)
+- DigOpt (Digital Options)
+- FinETO (Financial Exchange Traded Options)
+- Option (Generic Options)
+- Power Options (PO-CALL-D, PO-PUT-D)
+
+### Key Characteristics
+
+1. **Leverage Indicator**: Omega shows how much leverage an option provides compared to direct investment in the underlying asset
+2. **Dimensionless**: Unlike delta, omega is a ratio and has no units
+3. **Comparison Tool**: Allows comparison of sensitivity across different options regardless of their absolute prices
+4. **Risk Management**: Useful for portfolio managers to understand relative risk exposure
+
+### Practical Applications
+
+- **Option Selection**: Compare the leverage potential of different options
+- **Risk Assessment**: Understand the amplified effect of underlying price movements
+- **Portfolio Optimization**: Balance high and low omega positions
+- **Hedging Strategies**: Determine appropriate hedge ratios for leveraged positions
+
+### Relationship to Other Greeks
+
+Omega is directly related to delta and can be calculated from existing delta results:
+
+```
+Omega = (Delta × Underlying_Price) / Option_Value
+```
+
+### Example Calculation
+
+For a call option with:
+- Delta = 0.6
+- Underlying price = $100
+- Option value = $8
+
+Omega = (0.6 × $100) / $8 = 7.5
+
+This means a 1% increase in the underlying price would result in approximately a 7.5% increase in the option value.
+
+### Implementation Notes
+
+- Omega calculations require non-zero option values to avoid division by zero
+- For deep out-of-the-money options with very small values, omega can become extremely large
+- The result should be monitored for numerical stability, especially near expiration
+- Omega is most meaningful for options with significant time value remaining
+
+---
"""
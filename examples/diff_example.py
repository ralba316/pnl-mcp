"""
Example demonstrating the improved unified diff parser.
Shows how to use standard diff format for file editing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pnl_mcp.diff_parser import apply_unified_diff, insert_content_after_line
import tempfile


def demo_unified_diff():
    """Demonstrate using unified diff format for complex edits."""
    
    # Create a test file
    test_file = "test_document.md"
    with open(test_file, 'w') as f:
        f.write("""# Main Document

## Section 1
Content for section 1.

## Section 2  
Content for section 2.

## Section 3
Content for section 3.""")
    
    print("Original file created")
    print("-" * 50)
    
    # Example 1: Insert content after Section 2 (line 7) using unified diff format
    omega_diff = """@@ -7,0 +7,14 @@
+
+## Omega Greek
+
+### Overview
+Omega measures the percentage change in an option's value.
+
+### Formula
+Omega = (Delta × Underlying_Price) / Option_Value
+
+### Example
+With Delta = 0.6, Price = $100, Value = $8:
+Omega = 7.5
+
+This means a 1% increase in underlying price results in 7.5% increase in option value."""
    
    success = apply_unified_diff(test_file, omega_diff)
    print(f"Applied Omega documentation: {success}")
    
    # Read the file to get current line count
    with open(test_file, 'r') as f:
        current_lines = len(f.readlines())
    
    # Example 2: Use the helper function for simple insertions
    # Insert at the end of the file
    additional_content = """
### Additional Notes
- Omega is dimensionless
- Useful for comparing leverage across options
- Most meaningful for options with time value"""
    
    success = insert_content_after_line(test_file, current_lines, additional_content)
    print(f"Added additional notes: {success}")
    
    # Show the result
    print("\nFinal document:")
    print("-" * 50)
    with open(test_file, 'r') as f:
        print(f.read())
    
    # Cleanup
    os.remove(test_file)


if __name__ == "__main__":
    demo_unified_diff()
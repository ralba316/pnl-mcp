"""
Demonstration of the enhanced editor with consistent line numbering.
Shows how to solve edit inconsistency issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pnl_mcp.enhanced_editor import (
    EnhancedFileReader, 
    EnhancedEditor,
    MarkdownDocumentBuilder,
    DisplayMode,
    read_file_with_numbers,
    search_and_show_context,
    create_content_edit,
    create_markdown_document
)


def demo_line_numbering():
    """Demonstrate consistent line numbering for accurate editing."""
    print("=" * 60)
    print("DEMO: Consistent Line Numbering")
    print("=" * 60)
    
    # Create a test file
    test_file = "test_editing.md"
    content = """# Test Document

## Section 1
This is the first section with some content.
It has multiple lines to demonstrate editing.

## Section 2
This section contains omega references.
The omega value is important here.
We'll search for omega and edit it.

## Section 3
Final section with more content.
This helps demonstrate line numbering."""
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    # Step 1: Read with line numbers
    print("\n1. Reading file with line numbers:")
    print("-" * 40)
    reader = EnhancedFileReader()
    output, lines = reader.read_with_line_numbers(test_file, DisplayMode.NUMBERED)
    print(output)
    
    # Step 2: Search for specific content
    print("\n2. Searching for 'omega' with context:")
    print("-" * 40)
    search_output = search_and_show_context(test_file, "omega", context=1)
    print(search_output)
    
    # Step 3: Get exact line for editing
    print("\n3. Getting exact line content for line 8:")
    print("-" * 40)
    line_content = reader.get_line_for_edit(test_file, 8)
    print(f"Line 8 content: '{line_content}'")
    
    # Step 4: Content-based editing
    print("\n4. Editing by content match:")
    print("-" * 40)
    editor = EnhancedEditor()
    result = editor.target_by_content(test_file, "omega", "alpha", "all")
    if result['success']:
        print(f"Found {result['total_matches']} matches")
        print(f"Prepared {result['edited_count']} edits")
        for edit in result['edits']:
            print(f"  Line {edit['line_number']}: '{edit['old_content']}' -> '{edit['new_content']}'")
    
    # Clean up
    os.remove(test_file)


def demo_batch_editing():
    """Demonstrate batch editing with preview."""
    print("\n" + "=" * 60)
    print("DEMO: Batch Editing with Preview")
    print("=" * 60)
    
    # Create test file
    test_file = "batch_test.py"
    content = """def calculate_omega(delta, price, value):
    '''Calculate omega for options.'''
    omega = (delta * price) / value
    return omega

def get_omega_ratio(option1, option2):
    '''Compare omega values.'''
    omega1 = calculate_omega(option1.delta, option1.price, option1.value)
    omega2 = calculate_omega(option2.delta, option2.price, option2.value)
    return omega1 / omega2"""
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    # Read with line numbers
    print("\n1. Original file with line numbers:")
    print("-" * 40)
    print(read_file_with_numbers(test_file))
    
    # Create batch edits
    editor = EnhancedEditor()
    
    # Add multiple edits
    editor.add_batch_edit(test_file, 1, 
                         "def calculate_omega(delta, price, value):",
                         "def calculate_elasticity(delta, price, value):",
                         "replace")
    
    editor.add_batch_edit(test_file, 2,
                         "    '''Calculate omega for options.'''",
                         "    '''Calculate elasticity (omega) for options.'''",
                         "replace")
    
    editor.add_batch_edit(test_file, 3,
                         "    omega = (delta * price) / value",
                         "    elasticity = (delta * price) / value",
                         "replace")
    
    # Preview edits
    print("\n2. Preview of pending edits:")
    print("-" * 40)
    print(editor.preview_edits())
    
    # Apply edits
    print("\n3. Applying batch edits:")
    print("-" * 40)
    result = editor.apply_batch_edits()
    print(f"Success: {result['success']}")
    print(f"Edits applied: {result['edits_applied']}")
    print(f"Files modified: {result['files_modified']}")
    
    # Show result
    print("\n4. File after edits:")
    print("-" * 40)
    print(read_file_with_numbers(test_file))
    
    # Clean up
    os.remove(test_file)


def demo_markdown_builder():
    """Demonstrate markdown document creation."""
    print("\n" + "=" * 60)
    print("DEMO: Markdown Document Builder")
    print("=" * 60)
    
    # Method 1: Using the builder directly
    builder = MarkdownDocumentBuilder("Option Greeks Documentation")
    builder.set_metadata(
        author="Financial Engineering Team",
        date="2024-01-15",
        tags=["options", "greeks", "derivatives"]
    )
    builder.enable_toc()
    
    # Add content
    builder.add_section("Introduction", 
                       "This document covers the essential option Greeks used in derivatives pricing.")
    
    builder.add_section("Delta", 
                       "Delta measures the rate of change of option value with respect to changes in the underlying asset's price.")
    
    builder.add_section("Omega (Elasticity)",
                       "Omega, also known as elasticity or percentage delta, measures the percentage change in an option's value relative to the percentage change in the underlying asset's price.")
    
    builder.add_title("Formula", 3)
    builder.add_code_block("Omega = (Delta × Underlying_Price) / Option_Value", "python")
    
    builder.add_title("Key Characteristics", 3)
    builder.add_list([
        "Leverage indicator",
        "Dimensionless ratio",
        "Comparison tool across options",
        "Risk management metric"
    ])
    
    builder.add_horizontal_rule()
    
    builder.add_title("Example Calculation", 2)
    builder.add_table(
        headers=["Parameter", "Value"],
        rows=[
            ["Delta", "0.6"],
            ["Underlying Price", "$100"],
            ["Option Value", "$8"],
            ["Omega", "7.5"]
        ]
    )
    
    # Build and save
    doc_content = builder.build()
    output_file = "option_greeks.md"
    builder.save(output_file)
    
    print(f"\n1. Created markdown document: {output_file}")
    print("-" * 40)
    print("First 500 characters:")
    print(doc_content[:500] + "...")
    
    # Method 2: Using convenience function
    quick_doc = create_markdown_document(
        title="Quick Reference",
        sections=[
            {"title": "Overview", "content": "Quick reference for option Greeks."},
            {"code": "omega = (delta * price) / value", "language": "python"},
            {"list": ["Delta: Price sensitivity", "Omega: Elasticity"], "ordered": True}
        ],
        toc=True,
        file_path="quick_reference.md"
    )
    
    print(f"\n2. Created quick reference document")
    print("-" * 40)
    print("Content preview:")
    print(quick_doc[:300] + "...")
    
    # Clean up
    os.remove(output_file)
    os.remove("quick_reference.md")


if __name__ == "__main__":
    # Run all demos
    demo_line_numbering()
    demo_batch_editing()
    demo_markdown_builder()
    
    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)
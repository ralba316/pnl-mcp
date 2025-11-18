"""
Enhanced editor with consistent line numbering and improved targeting.
Solves the inconsistency between read/search and edit operations.
"""

import re
from typing import List, Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class DisplayMode(Enum):
    """Display modes for file content."""
    PLAIN = "plain"
    NUMBERED = "numbered"
    NUMBERED_VERBOSE = "numbered_verbose"
    SEARCH_CONTEXT = "search_context"


@dataclass
class LineInfo:
    """Information about a line in a file."""
    number: int  # 1-based line number
    content: str
    length: int
    has_match: bool = False
    match_positions: List[Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.match_positions is None:
            self.match_positions = []


class EnhancedFileReader:
    """Enhanced file reader with consistent line numbering."""
    
    def __init__(self):
        self.line_cache: Dict[str, List[LineInfo]] = {}
    
    def read_with_line_numbers(
        self, 
        file_path: str, 
        mode: DisplayMode = DisplayMode.NUMBERED,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        search_pattern: Optional[str] = None,
        context_lines: int = 2
    ) -> Tuple[str, List[LineInfo]]:
        """
        Read file with consistent line numbering.
        
        Args:
            file_path: Path to file
            mode: Display mode for output
            start_line: Starting line (1-based, inclusive)
            end_line: Ending line (1-based, inclusive)
            search_pattern: Optional pattern to highlight
            context_lines: Lines of context for search mode
            
        Returns:
            Tuple of (formatted output, line info list)
        """
        # Read file and create line info
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return "File not found", []
        
        # Create LineInfo objects
        line_infos = []
        for i, line in enumerate(lines, 1):
            # Remove newline for processing but keep for display
            content = line.rstrip('\n')
            info = LineInfo(
                number=i,
                content=content,
                length=len(content)
            )
            
            # Check for search pattern
            if search_pattern:
                try:
                    pattern = re.compile(search_pattern, re.IGNORECASE)
                    matches = list(pattern.finditer(content))
                    if matches:
                        info.has_match = True
                        info.match_positions = [(m.start(), m.end()) for m in matches]
                except re.error:
                    # Treat as literal string if regex fails
                    if search_pattern.lower() in content.lower():
                        info.has_match = True
                        idx = content.lower().index(search_pattern.lower())
                        info.match_positions = [(idx, idx + len(search_pattern))]
            
            line_infos.append(info)
        
        # Cache for later use
        self.line_cache[file_path] = line_infos
        
        # Apply line range filter
        if start_line or end_line:
            start = (start_line or 1) - 1
            end = end_line or len(line_infos)
            line_infos = line_infos[start:end]
        
        # Format output based on mode
        output = self._format_output(line_infos, mode, search_pattern, context_lines)
        
        return output, line_infos
    
    def _format_output(
        self, 
        lines: List[LineInfo], 
        mode: DisplayMode,
        search_pattern: Optional[str] = None,
        context_lines: int = 2
    ) -> str:
        """Format lines based on display mode."""
        
        if mode == DisplayMode.PLAIN:
            return '\n'.join(line.content for line in lines)
        
        elif mode == DisplayMode.NUMBERED:
            # Simple line numbers
            formatted = []
            for line in lines:
                formatted.append(f"{line.number:6d}: {line.content}")
            return '\n'.join(formatted)
        
        elif mode == DisplayMode.NUMBERED_VERBOSE:
            # Verbose format with additional info
            formatted = []
            for line in lines:
                length_info = f"[len:{line.length:4d}]"
                match_info = " [MATCH]" if line.has_match else ""
                formatted.append(f"{line.number:6d} {length_info}{match_info}: {line.content}")
            return '\n'.join(formatted)
        
        elif mode == DisplayMode.SEARCH_CONTEXT:
            # Show only matches with context
            if not search_pattern:
                return self._format_output(lines, DisplayMode.NUMBERED)
            
            formatted = []
            match_indices = [i for i, line in enumerate(lines) if line.has_match]
            
            shown_lines = set()
            for idx in match_indices:
                # Add context lines
                start = max(0, idx - context_lines)
                end = min(len(lines), idx + context_lines + 1)
                
                for i in range(start, end):
                    if i not in shown_lines:
                        shown_lines.add(i)
                        line = lines[i]
                        prefix = ">>> " if line.has_match else "    "
                        formatted.append(f"{prefix}{line.number:6d}: {line.content}")
                
                # Add separator if not last match
                if idx != match_indices[-1]:
                    formatted.append("    ...")
            
            return '\n'.join(formatted)
        
        return ""
    
    def get_line_for_edit(self, file_path: str, line_number: int) -> Optional[str]:
        """
        Get exact line content for editing.
        
        Args:
            file_path: Path to file
            line_number: 1-based line number
            
        Returns:
            Exact line content or None if not found
        """
        if file_path in self.line_cache:
            lines = self.line_cache[file_path]
            if 1 <= line_number <= len(lines):
                return lines[line_number - 1].content
        
        # Read file if not cached
        _, lines = self.read_with_line_numbers(file_path, DisplayMode.PLAIN)
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].content
        
        return None


class EnhancedEditor:
    """Enhanced editor with improved targeting and batch operations."""
    
    def __init__(self):
        self.reader = EnhancedFileReader()
        self.pending_edits: List[Dict[str, Any]] = []
    
    def target_by_content(
        self, 
        file_path: str,
        search_pattern: str,
        replacement: str,
        occurrence: Union[int, str] = "all"
    ) -> Dict[str, Any]:
        """
        Target edits by content rather than line number.
        
        Args:
            file_path: Path to file
            search_pattern: Pattern to search for
            replacement: Replacement text
            occurrence: Which occurrence to replace (1-based, "first", "last", or "all")
            
        Returns:
            Edit operation details
        """
        _, lines = self.reader.read_with_line_numbers(
            file_path, 
            DisplayMode.PLAIN,
            search_pattern=search_pattern
        )
        
        edits = []
        matches_found = []
        
        for line in lines:
            if line.has_match:
                matches_found.append({
                    'line_number': line.number,
                    'content': line.content,
                    'matches': line.match_positions
                })
        
        if not matches_found:
            return {'success': False, 'error': 'No matches found'}
        
        # Determine which matches to replace
        if occurrence == "all":
            targets = matches_found
        elif occurrence == "first":
            targets = [matches_found[0]]
        elif occurrence == "last":
            targets = [matches_found[-1]]
        elif isinstance(occurrence, int):
            if 1 <= occurrence <= len(matches_found):
                targets = [matches_found[occurrence - 1]]
            else:
                return {'success': False, 'error': f'Occurrence {occurrence} out of range'}
        else:
            return {'success': False, 'error': 'Invalid occurrence specification'}
        
        # Create edit operations
        for target in targets:
            edits.append({
                'line_number': target['line_number'],
                'old_content': target['content'],
                'new_content': target['content'].replace(search_pattern, replacement),
                'operation': 'replace'
            })
        
        return {
            'success': True,
            'edits': edits,
            'total_matches': len(matches_found),
            'edited_count': len(edits)
        }
    
    def add_batch_edit(
        self,
        file_path: str,
        line_number: int,
        old_content: str,
        new_content: str,
        operation: str = "replace"
    ):
        """Add an edit to the batch queue."""
        self.pending_edits.append({
            'file_path': file_path,
            'line_number': line_number,
            'old_content': old_content,
            'new_content': new_content,
            'operation': operation
        })
    
    def preview_edits(self) -> str:
        """Preview all pending edits."""
        if not self.pending_edits:
            return "No pending edits"
        
        preview = ["=== EDIT PREVIEW ===\n"]
        
        # Group by file
        by_file = {}
        for edit in self.pending_edits:
            file_path = edit['file_path']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(edit)
        
        for file_path, edits in by_file.items():
            preview.append(f"\nFile: {file_path}")
            preview.append("-" * 50)
            
            # Sort by line number
            edits.sort(key=lambda x: x['line_number'])
            
            for edit in edits:
                preview.append(f"\nLine {edit['line_number']} ({edit['operation']}):")
                if edit['old_content']:
                    preview.append(f"  - {edit['old_content']}")
                if edit['new_content']:
                    preview.append(f"  + {edit['new_content']}")
        
        preview.append("\n=== END PREVIEW ===")
        return '\n'.join(preview)
    
    def apply_batch_edits(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Apply all pending edits.
        
        Args:
            dry_run: If True, don't actually apply edits
            
        Returns:
            Results of the batch operation
        """
        if not self.pending_edits:
            return {'success': False, 'error': 'No pending edits'}
        
        results = {
            'success': True,
            'files_modified': [],
            'edits_applied': 0,
            'errors': []
        }
        
        # Group by file
        by_file = {}
        for edit in self.pending_edits:
            file_path = edit['file_path']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(edit)
        
        for file_path, edits in by_file.items():
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Sort edits by line number in reverse to maintain line numbers
                edits.sort(key=lambda x: x['line_number'], reverse=True)
                
                # Apply edits
                for edit in edits:
                    line_num = edit['line_number'] - 1  # Convert to 0-based
                    
                    if 0 <= line_num < len(lines):
                        if edit['operation'] == 'replace':
                            lines[line_num] = edit['new_content'] + '\n'
                        elif edit['operation'] == 'delete':
                            del lines[line_num]
                        elif edit['operation'] == 'insert':
                            lines.insert(line_num + 1, edit['new_content'] + '\n')
                        
                        results['edits_applied'] += 1
                    else:
                        results['errors'].append(f"Line {edit['line_number']} out of range in {file_path}")
                
                # Write file
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    results['files_modified'].append(file_path)
                
            except Exception as e:
                results['errors'].append(f"Error processing {file_path}: {str(e)}")
                results['success'] = False
        
        # Clear pending edits after applying
        if not dry_run:
            self.pending_edits = []
        
        return results
    
    def clear_pending_edits(self):
        """Clear all pending edits."""
        self.pending_edits = []
        return "Pending edits cleared"


# Convenience functions
def read_file_with_numbers(file_path: str, **kwargs) -> str:
    """Convenience function to read file with line numbers."""
    reader = EnhancedFileReader()
    output, _ = reader.read_with_line_numbers(file_path, DisplayMode.NUMBERED, **kwargs)
    return output


def search_and_show_context(file_path: str, pattern: str, context: int = 2) -> str:
    """Search file and show matches with context."""
    reader = EnhancedFileReader()
    output, _ = reader.read_with_line_numbers(
        file_path, 
        DisplayMode.SEARCH_CONTEXT,
        search_pattern=pattern,
        context_lines=context
    )
    return output


def create_content_edit(file_path: str, search: str, replace: str, occurrence="all") -> Dict[str, Any]:
    """Create edit based on content match."""
    editor = EnhancedEditor()
    return editor.target_by_content(file_path, search, replace, occurrence)


class MarkdownDocumentBuilder:
    """Builder for creating well-structured markdown documents."""
    
    def __init__(self, title: str = None):
        self.sections = []
        self.title = title
        self.toc_enabled = False
        self.metadata = {}
    
    def set_metadata(self, **kwargs):
        """Set document metadata (for front matter)."""
        self.metadata.update(kwargs)
        return self
    
    def enable_toc(self):
        """Enable table of contents generation."""
        self.toc_enabled = True
        return self
    
    def add_title(self, title: str, level: int = 1):
        """Add a title/heading."""
        self.sections.append({
            'type': 'heading',
            'level': level,
            'content': title
        })
        return self
    
    def add_paragraph(self, text: str):
        """Add a paragraph of text."""
        self.sections.append({
            'type': 'paragraph',
            'content': text
        })
        return self
    
    def add_code_block(self, code: str, language: str = ""):
        """Add a code block."""
        self.sections.append({
            'type': 'code',
            'language': language,
            'content': code
        })
        return self
    
    def add_list(self, items: List[str], ordered: bool = False):
        """Add a list (ordered or unordered)."""
        self.sections.append({
            'type': 'list',
            'ordered': ordered,
            'items': items
        })
        return self
    
    def add_table(self, headers: List[str], rows: List[List[str]]):
        """Add a table."""
        self.sections.append({
            'type': 'table',
            'headers': headers,
            'rows': rows
        })
        return self
    
    def add_blockquote(self, text: str):
        """Add a blockquote."""
        self.sections.append({
            'type': 'blockquote',
            'content': text
        })
        return self
    
    def add_horizontal_rule(self):
        """Add a horizontal rule."""
        self.sections.append({'type': 'hr'})
        return self
    
    def add_link(self, text: str, url: str, inline: bool = True):
        """Add a link."""
        self.sections.append({
            'type': 'link',
            'text': text,
            'url': url,
            'inline': inline
        })
        return self
    
    def add_image(self, alt_text: str, url: str, title: str = None):
        """Add an image."""
        self.sections.append({
            'type': 'image',
            'alt': alt_text,
            'url': url,
            'title': title
        })
        return self
    
    def add_raw_markdown(self, markdown: str):
        """Add raw markdown content."""
        self.sections.append({
            'type': 'raw',
            'content': markdown
        })
        return self
    
    def add_section(self, title: str, content: str, level: int = 2):
        """Add a complete section with title and content."""
        self.add_title(title, level)
        self.add_paragraph(content)
        return self
    
    def _generate_toc(self) -> str:
        """Generate table of contents."""
        toc = ["## Table of Contents\n"]
        
        for section in self.sections:
            if section['type'] == 'heading' and section['level'] <= 3:
                indent = "  " * (section['level'] - 1)
                anchor = section['content'].lower().replace(' ', '-').replace('.', '')
                toc.append(f"{indent}- [{section['content']}](#{anchor})")
        
        return '\n'.join(toc) + '\n'
    
    def _generate_front_matter(self) -> str:
        """Generate YAML front matter."""
        if not self.metadata:
            return ""
        
        lines = ["---"]
        for key, value in self.metadata.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---\n")
        
        return '\n'.join(lines)
    
    def build(self) -> str:
        """Build the complete markdown document."""
        parts = []
        
        # Add front matter if present
        if self.metadata:
            parts.append(self._generate_front_matter())
        
        # Add main title if set
        if self.title:
            parts.append(f"# {self.title}\n")
        
        # Add TOC if enabled
        if self.toc_enabled:
            parts.append(self._generate_toc())
        
        # Add all sections
        for section in self.sections:
            if section['type'] == 'heading':
                parts.append(f"{'#' * section['level']} {section['content']}\n")
            
            elif section['type'] == 'paragraph':
                parts.append(f"{section['content']}\n")
            
            elif section['type'] == 'code':
                lang = section.get('language', '')
                parts.append(f"```{lang}\n{section['content']}\n```\n")
            
            elif section['type'] == 'list':
                items = []
                for i, item in enumerate(section['items'], 1):
                    prefix = f"{i}." if section['ordered'] else "-"
                    items.append(f"{prefix} {item}")
                parts.append('\n'.join(items) + '\n')
            
            elif section['type'] == 'table':
                # Headers
                parts.append('| ' + ' | '.join(section['headers']) + ' |')
                parts.append('| ' + ' | '.join(['---'] * len(section['headers'])) + ' |')
                # Rows
                for row in section['rows']:
                    parts.append('| ' + ' | '.join(row) + ' |')
                parts.append('')
            
            elif section['type'] == 'blockquote':
                lines = section['content'].split('\n')
                quoted = '\n'.join(f"> {line}" for line in lines)
                parts.append(f"{quoted}\n")
            
            elif section['type'] == 'hr':
                parts.append("---\n")
            
            elif section['type'] == 'link':
                if section.get('inline'):
                    parts.append(f"[{section['text']}]({section['url']})\n")
                else:
                    parts.append(f"[{section['text']}]: {section['url']}\n")
            
            elif section['type'] == 'image':
                title = f' "{section["title"]}"' if section.get('title') else ''
                parts.append(f"![{section['alt']}]({section['url']}{title})\n")
            
            elif section['type'] == 'raw':
                parts.append(f"{section['content']}\n")
        
        return '\n'.join(parts)
    
    def save(self, file_path: str) -> bool:
        """Save the document to a file."""
        try:
            content = self.build()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False


def create_markdown_document(
    title: str,
    sections: List[Dict[str, Any]],
    file_path: Optional[str] = None,
    toc: bool = False,
    metadata: Optional[Dict] = None
) -> str:
    """
    Convenience function to create a markdown document.
    
    Args:
        title: Document title
        sections: List of section dictionaries with 'title' and 'content'
        file_path: Optional path to save the document
        toc: Whether to include table of contents
        metadata: Optional metadata for front matter
        
    Returns:
        Generated markdown content
    """
    builder = MarkdownDocumentBuilder(title)
    
    if metadata:
        builder.set_metadata(**metadata)
    
    if toc:
        builder.enable_toc()
    
    for section in sections:
        if 'title' in section:
            builder.add_section(
                section['title'],
                section.get('content', ''),
                section.get('level', 2)
            )
        elif 'code' in section:
            builder.add_code_block(
                section['code'],
                section.get('language', '')
            )
        elif 'list' in section:
            builder.add_list(
                section['list'],
                section.get('ordered', False)
            )
        elif 'table' in section:
            builder.add_table(
                section['table']['headers'],
                section['table']['rows']
            )
        elif 'raw' in section:
            builder.add_raw_markdown(section['raw'])
    
    content = builder.build()
    
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return content
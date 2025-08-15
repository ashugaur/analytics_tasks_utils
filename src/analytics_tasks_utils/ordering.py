# %% Operating system

## Dependencies
import re
from typing import List, Tuple, Optional
from pathlib import Path
from typing import List, Tuple, Optional, Union
import pyperclip

# %% Sort md

## sort_markdown_file
class MarkdownSorter:
    def __init__(self):
        self.code_block_pattern = re.compile(r'^```|^~~~')
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    
    def is_in_code_block(self, lines: List[str], line_index: int) -> bool:
        """Check if a line is inside a code block by counting block markers before it"""
        code_block_count = 0
        for i in range(line_index):
            if self.code_block_pattern.match(lines[i].strip()):
                code_block_count += 1
        return code_block_count % 2 == 1
    
    def find_heading_indices(self, lines: List[str]) -> List[Tuple[int, int, str]]:
        """Find all heading lines that are NOT in code blocks"""
        headings = []
        for i, line in enumerate(lines):
            if not self.is_in_code_block(lines, i):
                match = self.heading_pattern.match(line.strip())
                if match:
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    headings.append((i, level, title))
        return headings
    
    def extract_sort_key(self, title: str) -> str:
        """Extract clean text for sorting, removing markdown links and special characters"""
        # Remove markdown links [text](url) -> text
        title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
        # Remove markdown links [text]{target="_blank"} -> text  
        title = re.sub(r'\[([^\]]+)\]\{[^}]+\}', r'\1', title)
        # Remove other markdown formatting
        title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
        title = re.sub(r'\*([^*]+)\*', r'\1', title)
        title = re.sub(r'`([^`]+)`', r'\1', title)
        # Remove leading/trailing special characters for sorting
        title = re.sub(r'^[^\w\s]+', '', title)
        title = re.sub(r'[^\w\s]+$', '', title)
        return title.strip().lower()
    
    def extract_sections(self, lines: List[str]) -> List[dict]:
        """Extract sections with their complete content"""
        headings = self.find_heading_indices(lines)
        sections = []
        
        # Handle content before first heading
        if headings and headings[0][0] > 0:
            pre_content = lines[:headings[0][0]]
            if any(line.strip() for line in pre_content):  # Only if non-empty
                sections.append({
                    'level': 0,
                    'title': '',
                    'content': pre_content,
                    'line_start': 0,
                    'line_end': headings[0][0] - 1
                })
        
        # Process each heading and its content
        for i, (line_idx, level, title) in enumerate(headings):
            # Determine content end
            if i + 1 < len(headings):
                content_end = headings[i + 1][0]
            else:
                content_end = len(lines)
            
            # Extract content (including the heading line)
            section_content = lines[line_idx:content_end]
            
            sections.append({
                'level': level,
                'title': title,
                'content': section_content,
                'line_start': line_idx,
                'line_end': content_end - 1
            })
        
        return sections
    
    def build_hierarchy(self, sections: List[dict]) -> List[dict]:
        """Build hierarchical structure from flat sections"""
        root_sections = []
        section_stack = []
        
        for section in sections:
            level = section['level']
            
            # Handle pre-content (level 0)
            if level == 0:
                root_sections.append(section)
                continue
            
            # Remove deeper levels from stack
            while section_stack and section_stack[-1]['level'] >= level:
                section_stack.pop()
            
            # Add subsections list if not exists
            if 'subsections' not in section:
                section['subsections'] = []
            
            # Add to parent or root
            if section_stack:
                parent = section_stack[-1]
                if 'subsections' not in parent:
                    parent['subsections'] = []
                parent['subsections'].append(section)
            else:
                root_sections.append(section)
            
            section_stack.append(section)
        
        return root_sections
    
    def sort_sections_recursive(self, sections: List[dict]) -> List[dict]:
        """Sort sections recursively, keeping H1 at top"""
        # Separate by level
        h1_sections = [s for s in sections if s.get('level') == 1]
        other_sections = [s for s in sections if s.get('level', 0) != 1]
        
        # Sort non-H1 sections alphabetically by cleaned title
        other_sections.sort(key=lambda x: self.extract_sort_key(x.get('title', '')))
        
        # Recursively sort subsections
        for section in sections:
            if 'subsections' in section and section['subsections']:
                section['subsections'] = self.sort_sections_recursive(section['subsections'])
        
        return h1_sections + other_sections
    
    def sections_to_lines(self, sections: List[dict]) -> List[str]:
        """Convert sections back to lines"""
        result_lines = []
        
        for section in sections:
            # Add the section's content
            result_lines.extend(section['content'])
            
            # Add subsections
            if 'subsections' in section and section['subsections']:
                subsection_lines = self.sections_to_lines(section['subsections'])
                result_lines.extend(subsection_lines)
        
        return result_lines
    
    def sort_markdown_file(self, input_file: str, output_file: str = None) -> None:
        """
        Sort markdown headings in a file while preserving all content
        
        Args:
            input_file (str): Path to input markdown file
            output_file (str): Path to output file. If None, overwrites input file
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        print(f"Reading file: {input_file}")
        
        # Read the file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        print(f"Original file size: {original_size} characters")
        
        # Split into lines
        lines = content.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Extract sections
        sections = self.extract_sections(lines)
        print(f"Found {len(sections)} sections")
        
        # Build hierarchy
        hierarchical_sections = self.build_hierarchy(sections)
        print(f"Built hierarchy with {len(hierarchical_sections)} root sections")
        
        # Sort sections
        sorted_sections = self.sort_sections_recursive(hierarchical_sections)
        
        # Convert back to lines
        sorted_lines = self.sections_to_lines(sorted_sections)
        
        # Join lines back to content
        sorted_content = '\n'.join(sorted_lines)
        
        # Ensure file ends with newline
        if not sorted_content.endswith('\n'):
            sorted_content += '\n'
        
        new_size = len(sorted_content)
        print(f"New file size: {new_size} characters")
        
        if new_size < original_size * 0.9:  # If more than 10% content lost
            print("WARNING: Significant content loss detected!")
            print(f"Original: {original_size} chars, New: {new_size} chars")
            print("Aborting to prevent data loss. Please check the input file.")
            return
        
        # Write to output file
        output_path = Path(output_file) if output_file else input_path
        
        # Create backup if overwriting
        if output_path == input_path:
            backup_path = input_path.with_suffix(input_path.suffix + '.backup')
            print(f"Creating backup: {backup_path}")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sorted_content)
        
        print(f"Sorted markdown saved to: {output_path}")


def sort_markdown_file(input_file: str, output_file: str = None) -> None:
    """
    Convenience function to sort markdown file
    
    Args:
        input_file (str): Path to input markdown file  
        output_file (str): Path to output file. If None, overwrites input file
    """
    sorter = MarkdownSorter()
    sorter.sort_markdown_file(input_file, output_file)



# %% sort py

## sort_py

def sort_py(
    code: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    ascending: bool = True,
    exception: Optional[List[str]] = None,
) -> str:
    """
    Sort Python code blocks hierarchically while respecting exceptions.

    Args:
        code (Union[str, Path]): The Python code string to sort OR path to .py file
        output_file (Union[str, Path], optional): Output file path. If None and input is a file,
                                                overwrites the input file. If specified, saves to new file.
        ascending (bool): True for ascending order, False for descending
        exception (List[str], optional): List of block headers to exclude from sorting.
                                       Format: ["# %% Block Name", "## Sub-block Name"]

    Returns:
        str: Sorted code string (also writes to file if input was a file)
    """
    if exception is None:
        exception = []

    # Handle file input
    input_file_path = None
    if isinstance(code, (str, Path)) and (
        Path(code).exists() if isinstance(code, str) else code.exists()
    ):
        input_file_path = Path(code)
        try:
            with open(input_file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
        except Exception as e:
            raise ValueError(f"Error reading file {input_file_path}: {e}")
    else:
        # Assume it's a code string
        code_content = str(code)

    # Parse exception pairs
    exception_pairs = []
    for i in range(0, len(exception), 2):
        if i + 1 < len(exception):
            main_block = exception[i].strip()
            sub_block = exception[i + 1].strip()
            exception_pairs.append((main_block, sub_block))

    # Split code into lines
    lines = code_content.split("\n")

    # Find all main blocks (# %% or #%%)
    main_blocks = []
    current_block = None
    current_content = []

    for i, line in enumerate(lines):
        # Check if line is a main block header
        if re.match(r"^#\s*%%\s*", line.strip()):
            # Save previous block if exists
            if current_block is not None:
                main_blocks.append(
                    {
                        "header": current_block,
                        "content": current_content,
                        "original_index": len(main_blocks),
                    }
                )

            # Start new block
            current_block = line.strip()
            current_content = []
        else:
            # Add line to current block content
            if current_block is not None:
                current_content.append(line)
            else:
                # Lines before first block
                if not main_blocks:
                    main_blocks.append(
                        {"header": "", "content": [line], "original_index": 0}
                    )
                else:
                    main_blocks[0]["content"].insert(0, line)

    # Add the last block
    if current_block is not None:
        main_blocks.append(
            {
                "header": current_block,
                "content": current_content,
                "original_index": len(main_blocks),
            }
        )

    # Process each main block to sort its sub-blocks
    for block in main_blocks:
        if block["header"]:  # Skip empty header (pre-block content)
            block["content"] = sort_sub_blocks(
                block["content"], block["header"], exception_pairs, ascending
            )

    # Separate exception blocks from sortable blocks
    exception_blocks = []
    sortable_blocks = []

    for block in main_blocks:
        if block["header"]:
            is_exception = any(
                block["header"] == exc_pair[0] for exc_pair in exception_pairs
            )
            if is_exception:
                exception_blocks.append(block)
            else:
                sortable_blocks.append(block)
        else:
            # Pre-block content stays at the beginning
            exception_blocks.append(block)

    # Sort the sortable blocks
    if sortable_blocks:
        sortable_blocks.sort(key=lambda x: x["header"].lower(), reverse=not ascending)

    # Combine blocks: exceptions first (in original order), then sorted blocks
    final_blocks = []

    # Add exception blocks in their original positions relative to each other
    exception_blocks.sort(key=lambda x: x["original_index"])
    final_blocks.extend(exception_blocks)
    final_blocks.extend(sortable_blocks)

    # Reconstruct the code with proper spacing
    result_lines = []

    for i, block in enumerate(final_blocks):
        # Add spacing before main blocks (except the first one)
        if block["header"] and i > 0:
            # Add 3 blank lines before each main block
            result_lines.extend(["", "", ""])

        # Add the main block header
        if block["header"]:
            result_lines.append(block["header"])

        # Process block content with proper spacing for sub-blocks
        formatted_content = format_block_content(block["content"])
        result_lines.extend(formatted_content)

    sorted_code = "\n".join(result_lines)

    # Handle file output
    if input_file_path is not None:
        # Determine output file path
        if output_file is None:
            # Overwrite the input file
            output_path = input_file_path
        else:
            # Save to specified output file
            output_path = Path(output_file)

        # Write sorted code to file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(sorted_code)
            print(f"Sorted code written to: {output_path}")
        except Exception as e:
            print(f"Error writing to file {output_path}: {e}")

    return sorted_code


def is_inside_code_block(lines: List[str], target_index: int) -> bool:
    """
    Check if a line at target_index is inside a Python code block (function, class, etc.)
    by analyzing indentation levels and Python syntax.
    """
    if target_index >= len(lines):
        return False

    # Get the indentation of the target line
    target_line = lines[target_index]
    target_stripped = target_line.strip()

    # If the line is not indented or only has comment indentation, it's likely a true header
    if not target_line.startswith("    ") and not target_line.startswith("\t"):
        # Check if it's only indented for comment formatting (e.g., "    ## comment")
        if (
            target_stripped.startswith("##")
            and len(target_line) - len(target_line.lstrip()) <= 4
        ):
            return False

    # Look backwards to find the context
    for i in range(target_index - 1, -1, -1):
        line = lines[i].strip()

        # Skip empty lines and pure comments
        if not line or line.startswith("#"):
            continue

        # Check for function/class/method definitions
        if (
            line.startswith("def ")
            or line.startswith("class ")
            or line.startswith("async def ")
            or ":" in line
        ):
            # If we find a function/class definition, check if our target is indented relative to it
            definition_indent = len(lines[i]) - len(lines[i].lstrip())
            target_indent = len(lines[target_index]) - len(lines[target_index].lstrip())

            # If target is indented more than the definition, it's inside the code block
            if target_indent > definition_indent:
                return True

        # If we hit a line that's not indented and not a comment, we're likely at module level
        if len(lines[i]) - len(lines[i].lstrip()) == 0 and line:
            break

    # Additional check: look for patterns that suggest we're inside a function
    # Check if there are indented lines before this that suggest we're in a code block
    indent_levels = []
    for i in range(max(0, target_index - 10), target_index):
        line = lines[i]
        if line.strip() and not line.strip().startswith("#"):
            indent_level = len(line) - len(line.lstrip())
            indent_levels.append(indent_level)

    # If we have consistent indentation before this line, we're likely inside a code block
    if indent_levels:
        target_indent = len(lines[target_index]) - len(lines[target_index].lstrip())
        # If most recent non-comment lines are indented and our target is also indented
        recent_indented = [level for level in indent_levels[-5:] if level > 0]
        if len(recent_indented) >= 2 and target_indent > 0:
            return True

    return False


def format_block_content(content: List[str]) -> List[str]:
    """
    Format block content with proper spacing before sub-blocks (##).
    """
    if not content:
        return content

    formatted_content = []

    for i, line in enumerate(content):
        # Check if this line is a sub-block header (and not inside a code block)
        if re.match(r"^##\s*", line.strip()) and not is_inside_code_block(content, i):
            # Add 2 blank lines before sub-block (except if it's the first line)
            if i > 0 and formatted_content:
                # Check if we already have blank lines
                blank_lines_count = 0
                for j in range(len(formatted_content) - 1, -1, -1):
                    if formatted_content[j].strip() == "":
                        blank_lines_count += 1
                    else:
                        break

                # Add blank lines to make total of 2
                lines_to_add = max(0, 2 - blank_lines_count)
                formatted_content.extend([""] * lines_to_add)

        formatted_content.append(line)

    return formatted_content


def sort_sub_blocks(
    content: List[str],
    main_header: str,
    exception_pairs: List[Tuple[str, str]],
    ascending: bool,
) -> List[str]:
    """
    Sort sub-blocks (##) within a main block's content, ignoring ## comments inside code blocks.
    """
    if not content:
        return content

    # Find sub-blocks (only those not inside code blocks)
    sub_blocks = []
    current_sub_block = None
    current_sub_content = []
    pre_sub_content = []

    for i, line in enumerate(content):
        # Check if line is a sub-block header (and not inside a code block)
        if re.match(r"^##\s*", line.strip()) and not is_inside_code_block(content, i):
            # Save previous sub-block if exists
            if current_sub_block is not None:
                sub_blocks.append(
                    {
                        "header": current_sub_block,
                        "content": current_sub_content,
                        "original_index": len(sub_blocks),
                    }
                )
            elif not sub_blocks and current_sub_content:
                # Content before first sub-block
                pre_sub_content.extend(current_sub_content)

            # Start new sub-block
            current_sub_block = line.strip()
            current_sub_content = []
        else:
            # Add line to current sub-block content
            if current_sub_block is not None:
                current_sub_content.append(line)
            else:
                # Lines before first sub-block
                pre_sub_content.append(line)

    # Add the last sub-block
    if current_sub_block is not None:
        sub_blocks.append(
            {
                "header": current_sub_block,
                "content": current_sub_content,
                "original_index": len(sub_blocks),
            }
        )

    # If no sub-blocks found, return original content
    if not sub_blocks:
        return content

    # Separate exception sub-blocks from sortable ones
    exception_sub_blocks = []
    sortable_sub_blocks = []

    for sub_block in sub_blocks:
        is_exception = any(
            main_header == exc_pair[0] and sub_block["header"] == exc_pair[1]
            for exc_pair in exception_pairs
        )
        if is_exception:
            exception_sub_blocks.append(sub_block)
        else:
            sortable_sub_blocks.append(sub_block)

    # Sort the sortable sub-blocks
    if sortable_sub_blocks:
        sortable_sub_blocks.sort(
            key=lambda x: x["header"].lower(), reverse=not ascending
        )

    # Combine sub-blocks: exceptions first (in original order), then sorted ones
    final_sub_blocks = []
    exception_sub_blocks.sort(key=lambda x: x["original_index"])
    final_sub_blocks.extend(exception_sub_blocks)
    final_sub_blocks.extend(sortable_sub_blocks)

    # Reconstruct content
    result_content = pre_sub_content.copy()

    for sub_block in final_sub_blocks:
        result_content.append(sub_block["header"])
        result_content.extend(sub_block["content"])

    return result_content

# %% String

## order_lines
def order_lines(sort=1):
    """
    Process the text from clipboard.

    Args:
        sort (int, optional): Sorting order. 1 for ascending, 0 for descending. Defaults to 1.

    Returns:
        str: Processed text.
    """

    # Get text from clipboard
    text = pyperclip.paste()

    # Split text into lines
    lines = text.split("\n")

    # Remove duplicates
    lines = list(set(lines))

    # Sort lines based on length
    if sort == 1:
        lines.sort(key=len)
    elif sort == 0:
        lines.sort(key=len, reverse=True)
    else:
        raise ValueError("Invalid sort order. Use 1 for ascending or 0 for descending.")

    # Join lines back into a string
    processed_text = "\n".join(lines)

    # Copy processed text back to clipboard
    pyperclip.copy(processed_text)

    # Print processed text
    print(processed_text)

    return processed_text


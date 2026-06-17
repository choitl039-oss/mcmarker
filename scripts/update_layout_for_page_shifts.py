"""
Update layout.json to accommodate different page sections with different Y offsets.
"""
import json
from pathlib import Path

def update_layout_for_pages():
    """
    Update layout to handle page shifts:
    - Pages 1-5: Q1-Q25 with base_y = 958
    - Pages 6-7: Q1-Q25 with base_y = 934 (shift -24)
    - Pages 8-11: Q1-Q25 with base_y = 958 (back to normal)
    - Pages 12-22: Q1-Q25 with base_y = ? (needs measurement)
    """
    
    layout_path = Path("layout.json")
    with open(layout_path, 'r') as f:
        layout = json.load(f)
    
    # Store original coordinates for reference
    original_bases = {
        "block_1_5": {"questions": list(range(1, 26)), "base_y": 958},
        "block_6_7": {"questions": list(range(1, 26)), "base_y": 934},  # shifted -24
        "block_8_11": {"questions": list(range(1, 26)), "base_y": 958},  # back to normal
    }
    
    # X positions (consistent across all pages)
    x_positions = {
        "A": 423,
        "B": 488,
        "C": 548,
        "D": 608
    }
    
    # Row offsets within a block (consistent)
    row_offsets = [0, 38, 75, 113, 149]  # for questions 1-5, 6-10, etc.
    
    print("Updating layout.json for page-specific Y offsets...")
    print()
    
    # Update Q1-Q25 for pages 6-7 with new base_y
    for q in range(1, 26):
        q_key = str(q)
        
        # Determine row within block
        row_in_block = (q - 1) % 5
        y_offset = row_offsets[row_in_block]
        
        # Create entry for pages 6-7 (base_y = 934)
        page_67_key = f"{q}_page6-7"
        if page_67_key not in layout:
            layout[page_67_key] = {}
            for choice in ["A", "B", "C", "D"]:
                y = 934 + y_offset
                layout[page_67_key][choice] = [x_positions[choice], y, 45, 45]
                
        print(f"Q{q}: pages 1-5 base_y=958, pages 6-7 base_y=934 (y={934 + y_offset})")
    
    # Save updated layout
    with open(layout_path, 'w') as f:
        json.dump(layout, f, indent=2)
    
    print()
    print(f"✓ Updated {layout_path}")
    print()
    print("NOTE: This approach adds separate entries for pages 6-7.")
    print("The detect_answers() function needs to be updated to use page-specific layouts.")

if __name__ == "__main__":
    update_layout_for_pages()

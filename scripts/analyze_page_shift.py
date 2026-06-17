"""
Identify coordinate shifts between pages by comparing detection on specific pages.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grade_mc import convert_pdf_to_images
import json

def analyze_page_shift(pdf_path, page_number, layout_path):
    """
    Show the Y-coordinates being used for a specific page.
    """
    pdf_path = Path(pdf_path)
    layout_path = Path(layout_path)
    
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return
    
    if not layout_path.exists():
        print(f"Error: {layout_path} not found")
        return
    
    with open(layout_path, 'r') as f:
        layout = json.load(f)
    
    images = convert_pdf_to_images(str(pdf_path))
    
    if page_number < 1 or page_number > len(images):
        print(f"Error: Page {page_number} doesn't exist (total pages: {len(images)})")
        return
    
    print(f"\n{'='*80}")
    print(f"PAGE {page_number} COORDINATE ANALYSIS")
    print(f"{'='*80}\n")
    
    print("CURRENT LAYOUT Y-COORDINATES (from layout.json):")
    print(f"{'Question':<12} {'A':<10} {'B':<10} {'C':<10} {'D':<10}")
    print(f"{'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    
    for q in range(1, 26):
        q_key = str(q)
        if q_key in layout:
            q_layout = layout[q_key]
            y_values = [q_layout[choice][1] for choice in ['A', 'B', 'C', 'D']]
            # They should all be the same Y
            y = y_values[0]
            print(f"Q{q:<11} {y:<10} {y:<10} {y:<10} {y:<10}")
    
    print(f"\n{'='*80}")
    print("TO FIX PAGE 6+ SHIFTS:")
    print(f"{'='*80}")
    print("\nUse scripts/measure_coordinates.py to click on these:")
    print("  1. Q1 bubble A on page 6 (middle of the bubble)")
    print("  2. Q2 bubble A on page 6")
    print("  3. Q3 bubble A on page 6")
    print("  4. Q4 bubble A on page 6")
    print("  5. Q5 bubble A on page 6")
    print("\nThen compare the Y-values to the layout.json values above.")
    print("The difference will tell us how much to shift page 6 coordinates.\n")

if __name__ == "__main__":
    pdf_path = Path(__file__).parent.parent / "2526 Bio.pdf"
    layout_path = Path(__file__).parent.parent / "layout.json"
    
    if len(sys.argv) > 1:
        page_num = int(sys.argv[1])
    else:
        page_num = 6
    
    analyze_page_shift(pdf_path, page_num, layout_path)

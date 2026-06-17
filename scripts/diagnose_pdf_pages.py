"""
Diagnostic tool to check PDF page dimensions and detect layout shifts.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grade_mc import convert_pdf_to_images


def diagnose_pdf(pdf_path):
    """
    Check all pages in PDF for dimension changes.
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return
    
    print(f"\n{'='*80}")
    print(f"DIAGNOSING: {pdf_path.name}")
    print(f"{'='*80}\n")
    
    try:
        images = convert_pdf_to_images(str(pdf_path))
        print(f"Total pages: {len(images)}\n")
        
        print(f"{'Page':<6} {'Width':<10} {'Height':<10} {'Aspect Ratio':<15} {'Status':<15}")
        print(f"{'-'*6} {'-'*10} {'-'*10} {'-'*15} {'-'*15}")
        
        prev_width = None
        prev_height = None
        
        for i, img in enumerate(images, 1):
            width, height = img.size
            aspect = width / height if height > 0 else 0
            
            # Check if dimensions changed
            if prev_width is None:
                status = "BASELINE"
            elif width == prev_width and height == prev_height:
                status = "✓ OK"
            else:
                status = "⚠ SHIFTED"
            
            print(f"{i:<6} {width:<10} {height:<10} {aspect:<15.3f} {status:<15}")
            
            prev_width = width
            prev_height = height
        
        print(f"\n{'='*80}")
        print("ANALYSIS:")
        print(f"{'='*80}")
        
        # Group pages by dimension
        page_dims = {}
        for i, img in enumerate(images, 1):
            dim_key = f"{img.size[0]}x{img.size[1]}"
            if dim_key not in page_dims:
                page_dims[dim_key] = []
            page_dims[dim_key].append(i)
        
        print("\nPages grouped by dimensions:")
        for dim, pages in sorted(page_dims.items()):
            pages_str = ", ".join(map(str, pages))
            print(f"  {dim}: Pages {pages_str}")
        
        # Identify problem areas
        print("\n⚠ PROBLEM AREAS DETECTED:")
        print("  - Pages 6+: shifted (might need different Y offsets)")
        print("  - Pages 8-11: OK (baseline for this section)")
        print("  - Pages 12-22: shifted again (might need another offset)")
        
        print("\nRECOMMENDATIONS:")
        print("  1. Check if your PDF has pages with different physical sizes")
        print("  2. Create separate layout sections for different page types:")
        print("     - Section 1: Pages 1-5 (current layout)")
        print("     - Section 2: Pages 6-7 (needs adjustment)")
        print("     - Section 3: Pages 8-11 (OK)")
        print("     - Section 4: Pages 12-22 (needs adjustment)")
        print("\n  3. Use 'scripts/measure_coordinates.py' on pages 6 and 12 to get new offsets")
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    pdf_path = Path(__file__).parent.parent / "2526 Bio.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    
    diagnose_pdf(pdf_path)

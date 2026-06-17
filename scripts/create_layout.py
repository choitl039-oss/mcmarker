import cv2
import json
import argparse

# interactive rectangle drawing code adapted from OpenCV examples

current_rect = None
rects = []
start_pt = None
scale_factor = 1.0


def mouse_callback(event, x, y, flags, param):
    global current_rect, start_pt, rects
    if event == cv2.EVENT_LBUTTONDOWN:
        start_pt = (x, y)
        current_rect = (x, y, x, y)
    elif event == cv2.EVENT_MOUSEMOVE and start_pt:
        current_rect = (start_pt[0], start_pt[1], x, y)
    elif event == cv2.EVENT_LBUTTONUP and start_pt:
        end_pt = (x, y)
        rects.append((start_pt[0], start_pt[1], end_pt[0], end_pt[1]))
        start_pt = None
        current_rect = None


def main():
    global current_rect, start_pt, rects, scale_factor
    
    # Reset globals for fresh run
    current_rect = None
    rects = []
    start_pt = None
    scale_factor = 1.0
    
    parser = argparse.ArgumentParser(description="Draw layout rectangles on blank template")
    parser.add_argument("--pdf", required=True, help="Path to blank PDF template")
    parser.add_argument("--output", required=True, help="JSON file to write layout")
    args = parser.parse_args()

    from pdf2image import convert_from_path

    # Explicitly tell pdf2image where Poppler is located
    poppler_path = r"C:\Users\dmshw00039\poppler-25.12.0\Library\bin"
    images = convert_from_path(args.pdf, poppler_path=poppler_path)
    if len(images) == 0:
        print("No pages found in PDF")
        return
    img = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    
    # Scale image to fit on screen while maintaining aspect ratio
    # Target: fit within ~1200x1600 window
    max_width, max_height = 1200, 1600
    h, w = img.shape[:2]
    scale = min(max_width / w, max_height / h)
    if scale < 1:
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        # Scale rectangle coordinates as well when saving
        scale_factor = scale
    else:
        scale_factor = 1.0
    
    cv2.namedWindow("layout", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("layout", img.shape[1] + 20, img.shape[0] + 80)
    cv2.setMouseCallback("layout", mouse_callback)

    print("\n" + "="*60)
    print("LAYOUT HELPER: Draw rectangles around each bubble")
    print("="*60)
    print("1. Click and drag to draw a box around each bubble")
    print("2. Use mouse wheel to scroll if the page is too tall")
    print("3. Press 'q' when finished drawing all rectangles")
    print("4. You'll then be prompted for question number & choice")
    print("="*60 + "\n")

    while True:
        disp = img.copy()
        # Draw all rectangles
        for (x1, y1, x2, y2) in rects:
            cv2.rectangle(disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
        if current_rect:
            x1, y1, x2, y2 = current_rect
            cv2.rectangle(disp, (x1, y1), (x2, y2), (0, 0, 255), 1)
        
        # Add status text
        status = f"Rectangles drawn: {len(rects)} | Press 'q' to finish"
        cv2.putText(disp, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("layout", disp)
        key = cv2.waitKey(20) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

    if len(rects) == 0:
        print("No rectangles drawn. Exiting.")
        return

    # assign question/choice labels interactively via input
    layout = {}
    print(f"\nFound {len(rects)} rectangles. Now assigning them to questions/choices.\n")
    
    # Scale rectangle coordinates back to original image size if image was resized
    if scale_factor < 1.0:
        rects = [(int(x1/scale_factor), int(y1/scale_factor), int(x2/scale_factor), int(y2/scale_factor)) for x1, y1, x2, y2 in rects]
    
    for idx, (x1, y1, x2, y2) in enumerate(rects, start=1):
        print(f"Rectangle {idx}: pixel box ({x1},{y1})-({x2},{y2})")
        q = input("  → Question number (e.g. 1, 2, 3): ").strip()
        c = input("  → Choice letter (A, B, C, D): ").strip().upper()
        if q and c:
            if q not in layout:
                layout[q] = {}
            layout[q][c] = [x1, y1, x2 - x1, y2 - y1]
        print()

    with open(args.output, "w") as f:
        json.dump(layout, f, indent=2)
    print(f"✓ Layout written to {args.output}")
    print(f"  You can now use this with: python -m src.grade_mc --layout {args.output} ...")



if __name__ == "__main__":
    import numpy as np
    main()

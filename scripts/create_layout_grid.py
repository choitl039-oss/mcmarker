import cv2
import json
import argparse
import numpy as np

# Global state for mouse interaction
start_corner = None
preview_rect = None


def mouse_callback(event, x, y, flags, param):
    global start_corner, preview_rect
    img = param['img']
    disp = param['disp'].copy()
    
    if event == cv2.EVENT_LBUTTONDOWN:
        start_corner = (x, y)
        print(f"Start point recorded: ({x}, {y})")
    elif event == cv2.EVENT_MOUSEMOVE and start_corner:
        preview_rect = (start_corner[0], start_corner[1], x, y)
    elif event == cv2.EVENT_LBUTTONUP and start_corner:
        preview_rect = None


def main():
    parser = argparse.ArgumentParser(description="Generate layout from grid parameters")
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
    
    # Scale image to fit on screen
    max_width, max_height = 1200, 1600
    h, w = img.shape[:2]
    scale = min(max_width / w, max_height / h)
    if scale < 1:
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        scale_factor = scale
    else:
        scale_factor = 1.0
    
    cv2.namedWindow("grid_setup", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("grid_setup", img.shape[1] + 20, img.shape[0] + 80)
    cv2.setMouseCallback("grid_setup", mouse_callback, {'img': img, 'disp': img.copy()})

    print("\n" + "="*60)
    print("GRID LAYOUT HELPER")
    print("="*60)
    print("This tool creates a layout based on a regular grid of bubbles.")
    print("Click on the TOP-LEFT bubble to start.")
    print("="*60 + "\n")

    while True:
        disp = img.copy()
        if start_corner:
            cv2.circle(disp, start_corner, 5, (0, 255, 0), -1)
            cv2.putText(disp, "START", (start_corner[0] + 10, start_corner[1] - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        status = f"Click top-left bubble | Press 'q' to continue"
        cv2.putText(disp, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("grid_setup", disp)
        
        key = cv2.waitKey(20) & 0xFF
        if key == ord("q") and start_corner:
            break
    
    cv2.destroyAllWindows()

    # Get parameters from user
    print(f"\nStart bubble at (scaled): {start_corner}")
    print("Now enter the grid parameters:\n")
    
    x_start = int(input("X coordinate of top-left bubble: ") or start_corner[0])
    y_start = int(input("Y coordinate of top-left bubble: ") or start_corner[1])
    
    bubble_width = int(input("Width of each bubble (pixels): ") or 30)
    bubble_height = int(input("Height of each bubble (pixels): ") or 30)
    
    h_spacing = int(input("Horizontal spacing between bubbles (pixels): ") or 40)
    v_spacing = int(input("Vertical spacing between rows (pixels): ") or 45)
    
    num_questions = int(input("Number of questions: ") or 50)
    choices_per_q = int(input("Number of choices per question (usually 4): ") or 4)
    
    # Build layout grid
    layout = {}
    choice_letters = [chr(65 + i) for i in range(choices_per_q)]  # A, B, C, D, ...
    
    for q in range(1, num_questions + 1):
        row = (q - 1) // choices_per_q
        col_in_row = (q - 1) % choices_per_q
        
        layout[str(q)] = {}
        for c, choice in enumerate(choice_letters):
            x = x_start + c * h_spacing
            y = y_start + row * v_spacing
            
            # Scale back to original image coordinates
            x = int(x / scale_factor)
            y = int(y / scale_factor)
            w = int(bubble_width / scale_factor)
            h = int(bubble_height / scale_factor)
            
            layout[str(q)][choice] = [x, y, w, h]
    
    with open(args.output, "w") as f:
        json.dump(layout, f, indent=2)
    
    print(f"\n✓ Grid layout generated: {num_questions} questions × {choices_per_q} choices")
    print(f"✓ Layout written to {args.output}")
    print(f"\nYou can now use this with:")
    print(f"  python -m src.grade_mc --layout {args.output} ...")


if __name__ == "__main__":
    main()

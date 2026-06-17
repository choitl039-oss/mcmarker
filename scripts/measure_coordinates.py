import cv2
import numpy as np
from pdf2image import convert_from_path
import argparse

zoom_level = 1.0
pan_x, pan_y = 0, 0

def zoom_in():
    global zoom_level
    zoom_level *= 1.1

def zoom_out():
    global zoom_level
    zoom_level /= 1.1
    zoom_level = max(0.5, zoom_level)
click_points = []

def mouse_callback(event, x, y, flags, param):
    global zoom_level, pan_x, pan_y, click_points
    img = param['img']
    h, w = img.shape[:2]
    
    # Convert screen coordinates back to image coordinates
    img_x = int((x - pan_x) / zoom_level)
    img_y = int((y - pan_y) / zoom_level)
    
    if event == cv2.EVENT_MOUSEMOVE:
        print(f"Position: ({img_x}, {img_y})", end='\r')
    elif event == cv2.EVENT_LBUTTONDOWN:
        click_points.append((img_x, img_y))
        print(f"\nClicked at: ({img_x}, {img_y})")
    elif event == cv2.EVENT_MOUSEWHEEL:
        # flags contains the wheel delta in 32-bit signed int (highest word is delta)
        delta = flags >> 16
        if delta > 0:
            zoom_in()
        else:
            zoom_out()

def main():
    # bring globals into this scope since we modify them below
    global zoom_level, pan_x, pan_y, click_points
    parser = argparse.ArgumentParser(description="Load and measure coordinates on blank MC template")
    parser.add_argument("--pdf", required=True, help="Path to blank PDF template")
    parser.add_argument("--page", type=int, default=1, help="Page number (1-indexed, default: 1)")
    args = parser.parse_args()

    poppler_path = r"C:\Users\dmshw00039\poppler-25.12.0\Library\bin"
    images = convert_from_path(args.pdf, poppler_path=poppler_path)
    if len(images) == 0:
        print("No pages found in PDF")
        return
    
    # Convert 1-indexed to 0-indexed
    page_idx = args.page - 1
    if page_idx < 0 or page_idx >= len(images):
        print(f"Error: Page {args.page} not found. PDF has {len(images)} pages.")
        return
    
    img = cv2.cvtColor(np.array(images[page_idx]), cv2.COLOR_RGB2BGR)
    orig_h, orig_w = img.shape[:2]
    
    cv2.namedWindow("Coordinate Finder", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Coordinate Finder", 1200, 900)
    cv2.setMouseCallback("Coordinate Finder", mouse_callback, {'img': img})
    
    print("\n" + "="*60)
    print("COORDINATE FINDER")
    print("="*60)
    print(f"Page: {args.page} (Click on any point to see its coordinates)")
    print("Use mouse wheel to zoom in/out")
    print("Press 'q' to quit and show all clicked points")
    print("="*60 + "\n")
    
    while True:
        # Display current zoom/pan
        h, w = img.shape[:2]
        display = cv2.resize(img, (max(1, int(w * zoom_level)), max(1, int(h * zoom_level))))
        
        # Create canvas and paste zoomed image
        canvas = np.ones((1000, 1400, 3), dtype=np.uint8) * 50
        dh, dw = display.shape[:2]
        y1, y2 = max(0, pan_y), min(1000, pan_y + dh)
        x1, x2 = max(0, pan_x), min(1400, pan_x + dw)
        
        sy1 = max(0, -pan_y)
        sy2 = sy1 + (y2 - y1)
        sx1 = max(0, -pan_x)
        sx2 = sx1 + (x2 - x1)
        
        canvas[y1:y2, x1:x2] = display[sy1:sy2, sx1:sx2]
        
        # Add status text
        cv2.putText(canvas, f"Zoom: {zoom_level:.2f}x | Pan: ({pan_x}, {pan_y}) | Clicked: {len(click_points)}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # draw numbered markers for each clicked point
        for idx, (px, py) in enumerate(click_points, start=1):
            # transform back to display coordinates
            dx = int(px * zoom_level) + pan_x
            dy = int(py * zoom_level) + pan_y
            if 0 <= dx < canvas.shape[1] and 0 <= dy < canvas.shape[0]:
                cv2.circle(canvas, (dx, dy), 5, (0, 0, 255), -1)
                cv2.putText(canvas, str(idx), (dx + 8, dy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        
        cv2.imshow("Coordinate Finder", canvas)
        key = cv2.waitKey(50) & 0xFF
        
        if key == ord("q"):
            break
        elif key == ord("+") or key == ord("="):  # zoom in
            zoom_in()
        elif key == ord("-"):  # zoom out
            zoom_out()
        elif key == ord("w"):  # pan up
            pan_y -= 20
        elif key == ord("s"):  # pan down
            pan_y += 20
        elif key == ord("a"):  # pan left
            pan_x -= 20
        elif key == ord("d"):  # pan right
            pan_x += 20
    
    cv2.destroyAllWindows()
    
    print("\n" + "="*60)
    print(f"Clicked {len(click_points)} points:")
    for i, (x, y) in enumerate(click_points, start=1):
        print(f"  {i}. ({x}, {y})")
    print("="*60)

if __name__ == "__main__":
    main()

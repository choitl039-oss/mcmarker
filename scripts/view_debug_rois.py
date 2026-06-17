import cv2
import os
import numpy as np

def show_debug_rois():
    """Display all debug ROI images in a grid"""
    debug_dir = "debug_rois"
    if not os.path.exists(debug_dir):
        print(f"No {debug_dir} folder found")
        return
    
    # Get all PNG files
    files = sorted([f for f in os.listdir(debug_dir) if f.endswith('.png')])
    if not files:
        print(f"No PNG files in {debug_dir}")
        return
    
    print(f"Found {len(files)} ROI images. Displaying...")
    
    # Group by question
    from collections import defaultdict
    by_question = defaultdict(dict)
    for fname in files:
        # q1_A.png -> question 1, choice A
        parts = fname.replace('.png', '').split('_')
        q = parts[0]  # 'q1'
        choice = parts[1]  # 'A'
        by_question[q][choice] = os.path.join(debug_dir, fname)
    
    # Display each question's 4 choices in a 2x2 grid
    for q_label in sorted(by_question.keys()):
        choices_dict = by_question[q_label]
        print(f"\n{q_label.upper()}:")
        
        # Create 2x2 grid: A B / C D
        images = []
        labels = ['A', 'B', 'C', 'D']
        for label in labels:
            path = choices_dict.get(label)
            if path:
                img = cv2.imread(path)
                if img is not None:
                    # Add label text
                    h, w = img.shape[:2]
                    cv2.putText(img, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    images.append(img)
                else:
                    images.append(np.zeros((45, 45, 3), dtype=np.uint8))
            else:
                images.append(np.zeros((45, 45, 3), dtype=np.uint8))
        
        # Stack into 2x2
        row1 = np.hstack([images[0], images[1]])
        row2 = np.hstack([images[2], images[3]])
        grid = np.vstack([row1, row2])
        
        # Show in window
        cv2.imshow(f"{q_label.upper()}", grid)
        print(f"  Showing {q_label.upper()} (A B / C D). Press any key to continue, 'q' to exit.")
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        if key == ord('q'):
            break

if __name__ == "__main__":
    show_debug_rois()

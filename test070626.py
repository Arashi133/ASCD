import cv2
import numpy as np
import pandas as pd
import gradio as gr
import tempfile
import os
import fitz  # PyMuPDF (pip install pymupdf)

def process_input_file(file_path):
    """
    Detects if the input file is a PDF or an image.
    Converts PDFs natively using PyMuPDF without requiring system packages.
    """
    if file_path is None:
        return None, None, None, None, None, None, None, None, None
    
    # Check if file extension is a PDF
    if file_path.lower().endswith('.pdf'):
        doc = fitz.open(file_path)
        page = doc[0]  # Extract first page
        
        # Render the page to an image matrix at 300 DPI
        pix = page.get_pixmap(dpi=300)
        img_data = np.frombuffer(pix.samples, dtype=np.uint8)
        input_image = img_data.reshape((pix.h, pix.w, pix.n))
        
        # Convert to standard RGB/BGR channel spaces properly
        if pix.n == 4:
            input_image = cv2.cvtColor(input_image, cv2.COLOR_RGBA2RGB)
        else:
            input_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)
    else:
        # Read standard image arrays and convert from BGR to working RGB space
        input_image = cv2.imread(file_path)
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        
    return analyze_and_highlight_lines(input_image)


def analyze_and_highlight_lines(input_image):
    if input_image is None:
        return None, None, None, None, None, None, None, None, None
    
    # 1. Image preprocessing bases
    gray = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    skeleton = cv2.ximgproc.thinning(binary)
    
    # Create clean canvas arrays for our structural layer presets
    img_all = input_image.copy()
    img_1 = input_image.copy()
    img_2 = input_image.copy()
    img_3 = input_image.copy()
    img_4 = input_image.copy()
    img_5 = input_image.copy()
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skeleton)
    lines_records = []
    
    for label in range(1, num_labels):
        mask = (labels == label)
        pts = np.argwhere(mask)  # [y, x] coordinates
        
        if len(pts) < 3:
            continue
            
        # Compute exact thickness metrics safely
        thickness_values = dist_transform[mask] * 2
        avg_thickness = np.mean(thickness_values)
        pixel_length = float(len(pts))
        
        # --- SAFE ENDPOINT DETECTION USING CONVEX HULL ---
        if len(pts) > 100:
            hull_pts = cv2.convexHull(pts[:, [1, 0]].astype(np.int32)).reshape(-1, 2)
            diff = hull_pts[:, np.newaxis, :] - hull_pts[np.newaxis, :, :]
            dist_sq = np.sum(diff**2, axis=-1)
            idx1, idx2 = np.unravel_index(np.argmax(dist_sq), dist_sq.shape)
            start_pt = (int(hull_pts[idx1][0]), int(hull_pts[idx1][1]))
            end_pt = (int(hull_pts[idx2][0]), int(hull_pts[idx2][1]))
        else:
            diff = pts[:, np.newaxis, :] - pts[np.newaxis, :, :]
            dist_sq = np.sum(diff**2, axis=-1)
            idx1, idx2 = np.unravel_index(np.argmax(dist_sq), dist_sq.shape)
            start_pt = (int(pts[idx1][1]), int(pts[idx1][0]))
            end_pt = (int(pts[idx2][1]), int(pts[idx2][0]))
        
        lines_records.append({
            "Line ID": label,
            "Start Point": f"({start_pt[0]}, {start_pt[1]})",
            "End Point": f"({end_pt[0]}, {end_pt[1]})",
            "Length (px)": round(pixel_length, 1),
            "Avg Thickness (px)": round(avg_thickness, 1)
        })
        
        if avg_thickness < 1:
            group_color = (0, 255, 255)   # Cyan
            target_canvas = img_1
        elif 1 <= avg_thickness <= 2:
            group_color = (0, 255, 0)     # Green
            target_canvas = img_2
        elif 2 < avg_thickness <= 3:
            group_color = (255, 165, 0)   # Orange
            target_canvas = img_3
        elif 3 < avg_thickness <= 4:
            group_color = (255, 0, 0)     # Red
            target_canvas = img_4
        else:
            group_color = (255, 0, 255)   # Magenta
            target_canvas = img_5

        # --- PIXEL HEATMAP LAYER GENERATION ---
        for y, x in pts:
            # 🔥 FIX part 2: Dynamic thickness profiling for accurate width, but unified group coloration
            w = dist_transform[y, x] * 2
            dot_radius = max(1, int(w / 2))
            
            # Draw matching unified group colors to master and group canvas
            cv2.circle(img_all, (x, y), dot_radius, group_color, -1)
            cv2.circle(target_canvas, (x, y), dot_radius, group_color, -1)

        # --- DRAW VISUAL ENDPOINT CIRCLES (RGB Space Maps) ---
        # 1. Master Overlay
        cv2.circle(img_all, start_pt, 4, (0, 255, 0), -1)  # Green Start
        cv2.circle(img_all, end_pt, 4, (255, 0, 0), -1)    # Red End
        
        # # 2. Conditional Overlays per Preset Subcategory
        # if group_1:
        #     cv2.circle(img_1, start_pt, 4, (0, 255, 0), -1)
        #     cv2.circle(img_1, end_pt, 4, (255, 0, 0), -1)
        # elif group_2:
        #     cv2.circle(img_2, start_pt, 4, (0, 255, 0), -1)
        #     cv2.circle(img_2, end_pt, 4, (255, 0, 0), -1)
        # elif group_3:
        #     cv2.circle(img_3, start_pt, 4, (0, 255, 0), -1)
        #     cv2.circle(img_3, end_pt, 4, (255, 0, 0), -1)
        # elif group_4:
        #     cv2.circle(img_4, start_pt, 4, (0, 255, 0), -1)
        #     cv2.circle(img_4, end_pt, 4, (255, 0, 0), -1)
        # else:
        #     cv2.circle(img_5, start_pt, 4, (0, 255, 0), -1)
        #     cv2.circle(img_5, end_pt, 4, (255, 0, 0), -1)

    # Compile dataset row references
    if lines_records:
        df = pd.DataFrame(lines_records)
    else:
        df = pd.DataFrame(columns=["Line ID", "Start Point", "End Point", "Length (px)", "Avg Thickness (px)"])
    
    temp_dir = tempfile.gettempdir()
    csv_path = os.path.join(temp_dir, "discrete_line_analysis.csv")
    df.to_csv(csv_path, index=False)
    
    return img_all, df, csv_path, img_all, img_1, img_2, img_3, img_4, img_5


# --- Target Canvas Swapping Logic ---
def show_all_canvas(cache_all): return cache_all
def show_1_canvas(cache_1): return cache_1
def show_2_canvas(cache_2): return cache_2
def show_3_canvas(cache_3): return cache_3
def show_4_canvas(cache_4): return cache_4
def show_5_canvas(cache_5): return cache_5


# --- Gradio User Interface ---
with gr.Blocks(title="Advanced File Filtering") as demo:
    gr.Markdown("##Visual Density Selector: Filter Images & PDFs dynamically via Buttons")
    
    # Hidden application buffer storage parameters
    stored_img_all = gr.State()
    stored_img_1 = gr.State()
    stored_img_2 = gr.State()
    stored_img_3 = gr.State()
    stored_img_4 = gr.State()
    stored_img_5 = gr.State()

    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="Upload Image or PDF Document", file_types=[".pdf", ".png", ".jpg", ".jpeg"])
            submit_btn = gr.Button("Analyze Line Geometry", variant="primary")
        
        with gr.Column():
            image_output = gr.Image(type="numpy", label="Interactive Viewport Display", format="png")
            
    gr.Markdown("### 🔍 Filter the Highlighted Results Directly on the Image:")
    with gr.Row():
        btn_view_all = gr.Button("View All Lines Map", variant="secondary")
        btn_view_1 = gr.Button("View Lines < 1 px", variant="secondary")
        btn_view_2 = gr.Button("View Lines 1-2 px", variant="secondary")
        btn_view_3 = gr.Button("View Lines 2-3 px", variant="secondary")
        btn_view_4 = gr.Button("View Lines 3-4 px", variant="secondary")
        btn_view_5 = gr.Button("View Lines > 4 px", variant="secondary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Extracted Line Geometry Database")
            table_output = gr.Dataframe(interactive=False, wrap=True) 
        
        with gr.Column():
            gr.Markdown("### Export Data Sheet")
            file_output = gr.File(label="Download Full Geometry CSV")

    gr.Markdown("""
    ### Thickness Key:
    * 🔵 **Cyan:** <1 px | 🟢 **Green:** 1-2 px | 🟠 **Orange:** 2-3 px | 🔴 **Red:** 3-4 px | 🟣 **Magenta:** >4 px
    """)

    # Tie routing processing architecture directly to systemic input-outputs
    submit_btn.click(
        fn=process_input_file,
        inputs=file_input,
        outputs=[image_output, table_output, file_output, stored_img_all, stored_img_1, stored_img_2, stored_img_3, stored_img_4, stored_img_5]
    )
    
    # Map click events to swap the displayed image instantly using our cached layers
    btn_view_all.click(fn=show_all_canvas, inputs=stored_img_all, outputs=image_output)
    btn_view_1.click(fn=show_1_canvas, inputs=stored_img_1, outputs=image_output)
    btn_view_2.click(fn=show_2_canvas, inputs=stored_img_2, outputs=image_output)
    btn_view_3.click(fn=show_3_canvas, inputs=stored_img_3, outputs=image_output)
    btn_view_4.click(fn=show_4_canvas, inputs=stored_img_4, outputs=image_output)
    btn_view_5.click(fn=show_5_canvas, inputs=stored_img_5, outputs=image_output)

if __name__ == "__main__":
    demo.launch()
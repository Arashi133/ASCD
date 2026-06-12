import gradio as gr
from app.utils.test070626 import process_input_file
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
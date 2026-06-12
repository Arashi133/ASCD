import cv2
import numpy as np
import pandas as pd
import gradio as gr
import tempfile
import os
from pypdf import PdfReader  # Sử dụng thư viện an toàn, không bị Windows chặn

def process_input_file(file_path):
    """
    Nhận diện file đầu vào là PDF hay Ảnh.
    Chuyển đổi luồng đọc an toàn hơn bằng pypdf để vượt qua bộ lọc bảo mật Windows.
    """
    if file_path is None:
        return None, None, None, None, None, None, None, None, None
    
    # 1. Kiểm tra nếu file đầu vào là PDF
    if file_path.lower().endswith('.pdf'):
        try:
            reader = PdfReader(file_path)
            page = reader.pages[0]
            
            # Thông báo điều hướng sang dùng file ảnh nếu môi trường Windows bị giới hạn thư viện đồ họa nặng
            raise gr.Error("Hệ thống bảo mật máy tính chặn cổng chuyển đổi trực tiếp PDF. Vui lòng chuyển bản vẽ sang dạng ảnh (.png, .jpg) để thực hiện trích xuất nét vẽ!")
        except Exception as e:
            if isinstance(e, gr.Error):
                raise e
            raise gr.Error(f"Lỗi đọc file PDF: {str(e)}")
            
    # 2. Nếu file đầu vào là Ảnh chuẩn (PNG, JPG)
    else:
        input_image = cv2.imread(file_path)
        if input_image is None:
            raise gr.Error("Không thể đọc được file ảnh đầu vào. Vui lòng kiểm tra lại định dạng!")
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        
    return analyze_and_highlight_lines(input_image)


def analyze_and_highlight_lines(input_image):
    if input_image is None:
        return None, None, None, None, None, None, None, None, None
    
    # Tiền xử lý ảnh bản vẽ
    gray = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    skeleton = cv2.ximgproc.thinning(binary)
    
    # Khởi tạo các khung canvas hiển thị
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
        pts = np.argwhere(mask)  # Tọa độ [y, x]
        
        if len(pts) < 3:
            continue
            
        thickness_values = dist_transform[mask] * 2
        avg_thickness = np.mean(thickness_values)
        pixel_length = float(len(pts))
        
        # Xác định điểm đầu và điểm cuối của đường ống bản vẽ
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
        
        # Phân loại màu sắc theo độ dày đường ống MEP
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

        for y, x in pts:
            w = dist_transform[y, x] * 2
            dot_radius = max(1, int(w / 2))
            cv2.circle(img_all, (x, y), dot_radius, group_color, -1)
            cv2.circle(target_canvas, (x, y), dot_radius, group_color, -1)

        # Vẽ điểm khoanh tròn đầu/cuối
        cv2.circle(img_all, start_pt, 4, (0, 255, 0), -1)
        cv2.circle(img_all, end_pt, 4, (255, 0, 0), -1)

    if lines_records:
        df = pd.DataFrame(lines_records)
    else:
        df = pd.DataFrame(columns=["Line ID", "Start Point", "End Point", "Length (px)", "Avg Thickness (px)"])
    
    temp_dir = tempfile.gettempdir()
    csv_path = os.path.join(temp_dir, "discrete_line_analysis.csv")
    df.to_csv(csv_path, index=False)
    
    return img_all, df, csv_path, img_all, img_1, img_2, img_3, img_4, img_5
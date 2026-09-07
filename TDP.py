import pandas as pd
import numpy as np
import streamlit as st

# Cấu hình trang (Tùy chọn)
st.set_page_config(
    page_title="Tra cứu trạm gần nhất",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📍 Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu Data nền từ file Excel
@st.cache_data
def load_data():
    # Đọc sheet 'Data' và lấy dữ liệu từ hàng 3 trở đi
    # Skiprows=2 để bỏ qua 2 hàng tiêu đề đầu tiên
    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=2)
    return df

try:
    df_raw = load_data()

    # 2. Tiền xử lý dữ liệu để đảm bảo các ô trống không gây lỗi
    df_clean = df_raw.copy()

    # Chuyển đổi cột Lat và Long (Cột T và U) sang kiểu số
    df_clean.iloc[:, 19] = pd.to_numeric(df_clean.iloc[:, 19], errors='coerce')
    df_clean.iloc[:, 20] = pd.to_numeric(df_clean.iloc[:, 20], errors='coerce')

    # Loại bỏ các hàng mà dữ liệu Lat hoặc Long bị trống (NaN)
    # df_clean.columns[19] là tên cột T, df_clean.columns[20] là tên cột U
    df_clean = df_clean.dropna(subset=[df_clean.columns[19], df_clean.columns[20]])

    # 3. Nhập tọa độ cần tra cứu
    # Bạn có thể điều chỉnh giá trị mặc định (value=...) tại đây
    input_lat = st.number_input("Nhập LATITUDE (Vĩ độ):", format="%.6f", value=10.584259)
    input_lng = st.number_input("Nhập LONGITUDE (Kinh độ):", format="%.6f", value=107.058034)

    if st.button("Tính khoảng cách", type="primary"):
        with st.spinner('Đang tính toán khoảng cách...'):
            # Chuyển đổi tọa độ nhập vào và tọa độ trong dữ liệu sang Radians
            lat1, lon1 = np.radians(input_lat), np.radians(input_lng)
            lat2 = np.radians(df_clean.iloc[:, 19])
            lon2 = np.radians(df_clean.iloc[:, 20])

            # Công thức Haversine để tính khoảng cách (mét)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            r = 6371000  # Bán kính Trái Đất (m) - trùng công thức ô W3
            
            # Gán kết quả tính toán (Khoảng cách tính bằng mét)
            df_clean['Khoảng cách (m)'] = c * r

            # Sắp xếp để lấy 5 kết quả gần nhất (tương đương H3:H7)
            top5 = df_clean.sort_values(by='Khoảng cách (m)').head(5)

            st.subheader("🎯 Kết quả 5 trạm gần nhất:")
            
            # Hiển thị bảng kết quả với định dạng rõ ràng
            # Bạn có thể điều chỉnh danh sách và thứ tự các cột hiển thị tại đây
            display_cols = ['Khoảng cách (m)', 'Mã trạm theo SU', 'Tên trạm', 'Lat', 'Long', 'Địa chỉ', 'Tỉnh']
            cols_to_show = [c for c in display_cols if c in top5.columns]
            
            # Nếu không tìm thấy các tên cột chuẩn, hiển thị tất cả các cột
            if not cols_to_show:
                cols_to_show = top5.columns

            # reset_index(drop=True) để hiển thị STT từ 0 đến 4
            st.dataframe(top5[cols_to_show].reset_index(drop=True), use_container_width=True)

except FileNotFoundError:
    st.error("Không tìm thấy file dữ liệu 'DATA Trạm.xlsx'. Bạn hãy đảm bảo file này đã được tải lên cùng thư mục với file `.py`.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi không xác định. Có thể file 'DATA Trạm.xlsx' có cấu trúc không đúng hoặc bị lỗi: {e}")

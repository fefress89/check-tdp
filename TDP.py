import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Tra cứu trạm gần nhất", layout="wide")
st.title("📍 Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu Data nền từ file Excel
@st.cache_data
def load_data():
    # Đọc sheet 'Data' và lấy dữ liệu từ hàng 3 trở đi
    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=2)
    return df

try:
    df_raw = load_data()

    # 2. Tiền xử lý dữ liệu để sửa lỗi TypeError
    # Bản sao để tránh làm hỏng dữ liệu gốc
    df_clean = df_raw.copy()

    # Thử chuyển đổi cột Lat và Long (Cột 20 và 21) sang kiểu số
    # coerce: Nếu gặp ô trống/văn bản thì chuyển thành NaN (Not a Number)
    df_clean.iloc[:, 19] = pd.to_numeric(df_clean.iloc[:, 19], errors='coerce')
    df_clean.iloc[:, 20] = pd.to_numeric(df_clean.iloc[:, 20], errors='coerce')

    # Loại bỏ các hàng mà dữ liệu Lat hoặc Long bị trống (NaN)
    df_clean = df_clean.dropna(subset=[df_clean.columns[19], df_clean.columns[20]])

    # 3. Nhập tọa độ (Mô phỏng ô D7 hoặc nhập riêng D3, E3)
    # Lấy tọa độ ví dụ từ file Excel của bạn: D7 = 10.584258989621397, 107.05803434236459
    input_lat = st.number_input("Nhập LATITUDE (Vĩ độ):", format="%.6f", value=10.584259)
    input_lng = st.number_input("Nhập LONGITUDE (Kinh độ):", format="%.6f", value=107.058034)

    if st.button("Tính khoảng cách", type="primary"):
        with st.spinner('Đang tính toán khoảng cách...'):
            # Chuyển đổi tọa độ nhập vào và tọa độ trong dữ liệu sang Radians
            lat1, lon1 = np.radians(input_lat), np.radians(input_lng)
            
            # Sử dụng dữ liệu đã làm sạch để tính toán
            lat2 = np.radians(df_clean.iloc[:, 19].astype(float))
            lon2 = np.radians(df_clean.iloc[:, 20].astype(float))

            # Công thức Haversine/Khoảng cách tương đương cột W trong sheet Data:
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            
            r = 6371000 # Bán kính Trái Đất (m) - Giống công thức W3
            
            # Gán kết quả tính toán (Khoảng cách tính bằng mét)
            df_clean['Khoảng cách (m)'] = c * r

            # Lấy 5 hàng có khoảng cách nhỏ nhất (tương đương H3:H7)
            top5 = df_clean.sort_values(by='Khoảng cách (m)').head(5)

            st.subheader("🎯 Kết quả 5 trạm gần nhất:")
            
            # Hiển thị bảng kết quả với định dạng rõ ràng
            # Bạn có thể điều chỉnh các cột muốn hiển thị tại đây
            display_cols = ['Tên trạm', 'Địa chỉ', 'Tỉnh', 'Lat', 'Long', 'Khoảng cách (m)']
            cols_to_show = [c for c in display_cols if c in top5.columns]
            
            if not cols_to_show: # Nếu không tìm thấy các tên cột chuẩn, hiển thị tất cả
                cols_to_show = top5.columns

            st.dataframe(top5[cols_to_show].reset_index(drop=True), use_container_width=True)

except Exception as e:
    st.error(f"Đã xảy ra lỗi khi tải dữ liệu. Hãy đảm bảo file 'DATA Trạm.xlsx' có cấu trúc đúng: {e}")
    st.info("Kiểm tra lại nếu file Excel của bạn có sheet tên 'Data' và dữ liệu tọa độ nằm ở cột T và U từ hàng 3.")

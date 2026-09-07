import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Tra cứu trạm gần nhất",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu Data nền từ file Excel
@st.cache_data
def load_data():
    # Đọc sheet 'Data', dòng 2 là tiêu đề cột (skiprows=1)
    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=1)
    return df

try:
    df_raw = load_data()
    df_clean = df_raw.copy()

    # Tìm chính xác cột Lat và Long
    lat_col = 'Lat' if 'Lat' in df_clean.columns else df_clean.columns[19]
    long_col = 'Long' if 'Long' in df_clean.columns else df_clean.columns[20]

    # Chuyển đổi dữ liệu cột Lat và Long sang kiểu số (float)
    df_clean[lat_col] = pd.to_numeric(df_clean[lat_col], errors='coerce')
    df_clean[long_col] = pd.to_numeric(df_clean[long_col], errors='coerce')

    # Loại bỏ các hàng có tọa độ trống (NaN)
    df_clean = df_clean.dropna(subset=[lat_col, long_col])

    # 2. Ô dán tọa độ duy nhất (Dán cả LAT, LONG vào đây)
    raw_coord = st.text_input(
        "Dán tọa độ LATITUDE, LONGITUDE vào đây:",
        value="10.734728, 106.663666",
        placeholder="Ví dụ: 10.734728, 106.663666"
    )

    if st.button("Tính khoảng cách", type="primary"):
        # Tách chuỗi nhập vào theo dấu phẩy hoặc khoảng trắng
        clean_input = raw_coord.strip().replace('\t', ',')
        
        if ',' in clean_input:
            parts = [p.strip() for p in clean_input.split(',')]
        else:
            parts = clean_input.split()

        if len(parts) >= 2:
            try:
                input_lat = float(parts[0])
                input_lng = float(parts[1])

                with st.spinner('Đang tính toán khoảng cách...'):
                    # Chuyển đổi tọa độ nhập vào và mảng dữ liệu sang Radians
                    lat1 = np.radians(input_lat)
                    lon1 = np.radians(input_lng)
                    
                    lat2 = np.radians(df_clean[lat_col].values.astype(float))
                    lon2 = np.radians(df_clean[long_col].values.astype(float))

                    # Công thức Haversine tính khoảng cách (mét) tương đương cột W
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
                    c = 2 * np.arcsin(np.sqrt(a))
                    r = 6371000  # Bán kính Trái Đất (m)
                    
                    # Gán kết quả khoảng cách
                    df_clean['Khoảng cách (m)'] = c * r

                    # Lấy 5 trạm có khoảng cách nhỏ nhất
                    top5 = df_clean.sort_values(by='Khoảng cách (m)').head(5).copy()

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")
                    
                    # Chọn các cột hiển thị
                    cols_priority = ['Khoảng cách (m)', 'Mã trạm theo SU', 'Tên trạm', 'Địa chỉ', 'Tỉnh', lat_col, long_col]
                    cols_to_show = [c for c in cols_priority if c in top5.columns]
                    
                    if not cols_to_show:
                        cols_to_show = top5.columns

                    # Làm tròn khoảng cách đến 2 chữ số thập phân
                    top5['Khoảng cách (m)'] = top5['Khoảng cách (m)'].round(2)

                    st.dataframe(top5[cols_to_show].reset_index(drop=True), use_container_width=True)

            except ValueError:
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng đảm bảo chỉ nhập số, ví dụ: 10.734728, 106.663666")
        else:
            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ phân tách bởi dấu phẩy (ví dụ: 10.734728, 106.663666).")

except FileNotFoundError:
    st.error("Không tìm thấy file 'DATA Trạm.xlsx'. Bạn hãy đảm bảo file này đã được tải lên cùng thư mục trên GitHub.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi: {e}")

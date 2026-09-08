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
    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=1)
    return df

try:
    df_raw = load_data()
    df_clean = df_raw.copy()

    # Xác định vị trí cột theo tên hoặc chỉ số cột Excel
    col_ten_tram = 'Tên trạm' if 'Tên trạm' in df_clean.columns else df_clean.columns[6]          # Cột G
    col_ma_tram = 'Mã trạm theo SU' if 'Mã trạm theo SU' in df_clean.columns else df_clean.columns[5] # Cột F/H
    col_trang_thai = 'Trạng thái' if 'Trạng thái' in df_clean.columns else df_clean.columns[14]   # Cột O
    col_tinh = 'Tỉnh' if 'Tỉnh' in df_clean.columns else df_clean.columns[17]                     # Cột R
    col_mien_dia_ly = 'Miền địa lý' if 'Miền địa lý' in df_clean.columns else df_clean.columns[18]   # Cột S
    col_lat = 'Lat' if 'Lat' in df_clean.columns else df_clean.columns[19]                        # Cột T
    col_long = 'Long' if 'Long' in df_clean.columns else df_clean.columns[20]                     # Cột U

    # Chuyển đổi dữ liệu cột Lat và Long sang kiểu số (float)
    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors='coerce')
    df_clean[col_long] = pd.to_numeric(df_clean[col_long], errors='coerce')

    # Loại bỏ các hàng có tọa độ trống (NaN)
    df_clean = df_clean.dropna(subset=[col_lat, col_long])

    # 2. Ô dán tọa độ duy nhất
    raw_coord = st.text_input(
        "Dán tọa độ LATITUDE, LONGITUDE vào đây:",
        value="10.734728, 106.663666",
        placeholder="Ví dụ: 10.734728, 106.663666"
    )

    if st.button("Tính khoảng cách", type="primary"):
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
                    
                    lat2 = np.radians(df_clean[col_lat].values.astype(float))
                    lon2 = np.radians(df_clean[col_long].values.astype(float))

                    # Công thức Haversine tính khoảng cách (mét)
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
                    c = 2 * np.arcsin(np.sqrt(a))
                    r = 6371000  # Bán kính Trái Đất (m)
                    
                    # Gán kết quả khoảng cách
                    df_clean['Khoảng cách (m)'] = c * r

                    # Lấy 5 trạm có khoảng cách nhỏ nhất
                    top5 = df_clean.sort_values(by='Khoảng cách (m)').head(5).copy()

                    # Định dạng làm tròn khoảng cách 2 chữ số thập phân
                    top5['Khoảng cách (m)'] = top5['Khoảng cách (m)'].round(2)

                    # Tạo chuỗi tọa độ để copy (Lat, Long)
                    top5['Tọa độ Copy (Lat, Long)'] = top5.apply(
                        lambda r: f"{r[col_lat]}, {r[col_long]}", axis=1
                    )

                    # Đổi tên các cột hiển thị
                    rename_map = {
                        col_ten_tram: 'Tên Trạm',
                        col_ma_tram: 'Mã Trạm',
                        col_trang_thai: 'Trạng Thái',
                        col_tinh: 'Tỉnh',
                        col_mien_dia_ly: 'Miền Địa Lý',
                        col_lat: 'Lat',
                        col_long: 'Long'
                    }
                    top5 = top5.rename(columns=rename_map)

                    # Ép Lat, Long sang kiểu chuỗi để giữ nguyên chính xác tất cả số thập phân
                    top5['Lat'] = top5['Lat'].astype(str)
                    top5['Long'] = top5['Long'].astype(str)

                    # Thứ tự các cột hiển thị đúng như bảng kẻ khung yêu cầu (Không có STT)
                    output_cols = [
                        'Khoảng cách (m)', 
                        'Tên Trạm', 
                        'Mã Trạm', 
                        'Trạng Thái', 
                        'Tỉnh', 
                        'Miền Địa Lý', 
                        'Lat', 
                        'Long', 
                        'Tọa độ Copy (Lat, Long)'
                    ]
                    
                    cols_to_display = [col for col in output_cols if col in top5.columns]

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")
                    
                    # Bảng Kẻ Khung nguyên bản với ô Copy nhanh chuẩn Streamlit
                    st.dataframe(
                        top5[cols_to_display].reset_index(drop=True),
                        use_container_width=True
                    )

            except ValueError:
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng đảm bảo chỉ nhập số, ví dụ: 10.734728, 106.663666")
        else:
            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ phân tách bởi dấu phẩy.")

except FileNotFoundError:
    st.error("Không tìm thấy file 'DATA Trạm.xlsx'. Bạn hãy đảm bảo file này đã được tải lên cùng thư mục trên GitHub.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi: {e}")

import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Tra cứu trạm gần nhất", layout="wide")
st.title("📍 Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu từ sheet 'Data'
@st.cache_data
def load_data():
    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=1)
    return df

try:
    df_data = load_data()

    # 2. Ô nhập tọa độ D7
    input_d7 = st.text_input("Nhập tọa độ LAT, LONG (Ví dụ: 10.584258, 107.058034):", value="10.584258, 107.058034")

    if st.button("Tính khoảng cách", type="primary"):
        if "," in input_d7:
            try:
                # Tách D3 (Lat) và E3 (Long)
                parts = input_d7.split(",")
                lat_check = float(parts[0].strip())
                long_check = float(parts[1].strip())

                # Đổi sang Radians
                lat1_rad = np.radians(lat_check)
                long1_rad = np.radians(long_check)
                
                lat2_rad = np.radians(df_data['Lat'].astype(float))
                long2_rad = np.radians(df_data['Long'].astype(float))

                # Công thức Haversine (tương đương cột W trong Excel)
                dlat = lat2_rad - lat1_rad
                dlong = long2_rad - long1_rad

                a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlong / 2)**2
                c = 2 * np.arcsin(np.sqrt(a))
                
                # Khoảng cách tính bằng mét (6371000m như công thức Excel)
                df_data['Khoảng cách (m)'] = 6371000 * c

                # Sắp xếp lấy 5 kết quả gần nhất (tương đương H3:H7)
                result = df_data.sort_values(by='Khoảng cách (m)').head(5)

                st.subheader("🎯 Kết quả 5 trạm gần nhất:")
                
                # Hiển thị bảng kết quả
                display_cols = ['Mã trạm theo SU', 'Tên trạm', 'Địa chỉ', 'Tỉnh', 'Lat', 'Long', 'Khoảng cách (m)']
                cols_to_show = [c for c in display_cols if c in result.columns]
                
                st.dataframe(result[cols_to_show].reset_index(drop=True), use_container_width=True)

            except Exception as e:
                st.error(f"Lỗi xử lý dữ liệu: {e}")
        else:
            st.warning("Vui lòng nhập đúng định dạng: `LAT, LONG` (có dấu phẩy ở giữa).")

except Exception as e:
    st.error(f"Không thể đọc file 'DATA Trạm.xlsx'. Bạn hãy đảm bảo file này đã được tải lên GitHub: {e}")
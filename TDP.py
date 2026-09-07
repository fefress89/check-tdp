import pandas as pd
import numpy as np
import streamlit as st

st.title("Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu Data nền từ file Excel
@st.cache_data
def load_data():
    # Đọc sheet 'Data' và lấy dữ liệu từ hàng 3 trở đi
    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=2)
    return df

df_data = load_data()

# 2. Nhập tọa độ (Mô phỏng ô D7 hoặc nhập riêng D3, E3)
input_lat = st.number_input("Nhập LATITUDE (Vĩ độ):", format="%.6f", value=10.0)
input_lng = st.number_input("Nhập LONGITUDE (Kinh độ):", format="%.6f", value=105.0)

if st.button("Tính khoảng cách"):
    # Giả định cột T là LATITUDE, cột U là LONGITUDE trong sheet Data
    # Công thức Haversine/Khoảng cách tương đương cột W trong sheet Data:
    lat1, lon1 = np.radians(input_lat), np.radians(input_lng)
    lat2, lon2 = np.radians(df_data.iloc[:, 19]), np.radians(df_data.iloc[:, 20]) # T=cột 20, U=cột 21

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # Bán kính Trái Đất (km)
    
    # Gán kết quả tính toán (Cột W)
    df_data['Distance'] = c * r

    # Lấy 5 khoảng cách nhỏ nhất (tương đương H3:H7)
    top5 = df_data.sort_values(by='Distance').head(5)

    st.subheader("Kết quả 5 khoảng cách gần nhất:")
    for i, (idx, row) in enumerate(top5.iterrows(), start=1):
        st.write(f"**Gần thứ {i} (H{i+2}):** {row['Distance']:.3f} km")
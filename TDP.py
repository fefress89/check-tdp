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
    # Chuẩn hóa tên cột (xóa khoảng trắng thừa)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_raw = load_data()
    df_clean = df_raw.copy()

    # Hàm tìm cột linh hoạt theo danh sách tên gọi có thể có
    def get_col_name(df, possible_names, fallback_index):
        for name in possible_names:
            for col in df.columns:
                if name.lower() == str(col).lower():
                    return col
        if fallback_index < len(df.columns):
            return df.columns[fallback_index]
        return None

    # Xác định các cột dữ liệu
    col_pic_ptml = get_col_name(df_clean, ['PIC PTML', 'PIC_PTML'], 4)         # Cột E
    col_phan_loai = get_col_name(df_clean, ['Phân loại', 'Phan loai'], 1)       # Cột B
    col_ten_tram = get_col_name(df_clean, ['Tên trạm', 'Ten tram'], 6)          # Cột G
    col_ma_tram = get_col_name(df_clean, ['Mã trạm theo SU', 'Mã trạm'], 5)    # Cột F
    col_trang_thai = get_col_name(df_clean, ['Trạng thái', 'Trang thai'], 14)   # Cột O
    col_tinh = get_col_name(df_clean, ['Tỉnh', 'Tinh'], 17)                     # Cột R
    col_mien_dia_ly = get_col_name(df_clean, ['Miền địa lý', 'Mien dia ly'], 18)# Cột S
    col_lat = get_col_name(df_clean, ['Lat', 'LAT', 'Latitude'], 19)            # Cột T
    col_long = get_col_name(df_clean, ['Long', 'LONG', 'Longitude'], 20)        # Cột U

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

                    # 3. Sắp xếp theo khoảng cách tăng dần
                    df_sorted = df_clean.sort_values(by='Khoảng cách (m)').copy()

                    # Danh sách các cột cần kiểm tra trùng lặp thông tin
                    check_cols = [col_ten_tram, col_ma_tram, col_trang_thai, col_tinh, col_mien_dia_ly, col_lat, col_long]
                    existing_cols = [c for c in check_cols if c and c in df_sorted.columns]

                    # Loại bỏ các dòng trùng thông tin hoàn toàn, chỉ giữ lại dòng đầu tiên
                    df_dedup = df_sorted.drop_duplicates(subset=existing_cols, keep='first').copy()

                    # Lấy đúng 5 kết quả độc nhất gần nhất
                    top5 = df_dedup.head(5).copy()

                    # Định dạng làm tròn khoảng cách 2 chữ số thập phân
                    top5['Khoảng cách (m)'] = top5['Khoảng cách (m)'].round(2)

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")

                    # Mã HTML tạo bảng kẻ khung
                    html_code = """
                    <style>
                        .custom-table {
                            width: 100%;
                            border-collapse: collapse;
                            margin: 10px 0;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            color: #ffffff;
                        }
                        .custom-table th {
                            background-color: #262730;
                            color: #fafafa;
                            text-align: left;
                            padding: 12px;
                            border: 1px solid #41444C;
                        }
                        .custom-table td {
                            padding: 10px 12px;
                            border: 1px solid #41444C;
                            background-color: #0e1117;
                        }
                        .copy-btn {
                            background-color: #ff4b4b;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-weight: bold;
                            font-size: 13px;
                            transition: 0.2s;
                        }
                        .copy-btn:hover {
                            background-color: #d33a3a;
                        }
                    </style>

                    <script>
                    function copyToClipboard(text, btn) {
                        navigator.clipboard.writeText(text).then(function() {
                            var originalText = btn.innerHTML;
                            btn.innerHTML = "✅ Đã Copy!";
                            btn.style.backgroundColor = "#28a745";
                            setTimeout(function() {
                                btn.innerHTML = originalText;
                                btn.style.backgroundColor = "#ff4b4b";
                            }, 1500);
                        });
                    }
                    </script>

                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th style="width: 50px;"></th>
                                <th>Khoảng cách (m)</th>
                                <th>Tên Trạm</th>
                                <th>Mã Trạm</th>
                                <th>Trạng Thái</th>
                                <th>Loại Trạm</th>
                                <th>Tỉnh</th>
                                <th>Miền Địa Lý</th>
                                <th>Lat</th>
                                <th>Long</th>
                                <th style="text-align: center;">Tọa độ Copy (Lat, Long)</th>
                            </tr>
                        </thead>
                        <tbody>
                    """

                    for idx, (_, row) in enumerate(top5.iterrows()):
                        lat_val = str(row[col_lat])
                        long_val = str(row[col_long])
                        coord_str = f"{lat_val}, {long_val}"
                        
                        # Ưu tiên lấy dữ liệu từ PIC PTML (cột E), nếu trống thì thử lấy Phân loại (cột B)
                        loai_tram_val = ""
                        if col_pic_ptml in row and pd.notna(row[col_pic_ptml]) and str(row[col_pic_ptml]).strip() != "":
                            loai_tram_val = str(row[col_pic_ptml]).strip()
                        elif col_phan_loai in row and pd.notna(row[col_phan_loai]) and str(row[col_phan_loai]).strip() != "":
                            loai_tram_val = str(row[col_phan_loai]).strip()
                        else:
                            loai_tram_val = "-"

                        html_code += f"""
                            <tr>
                                <td style="text-align: center; color: #888888; font-weight: bold;">{idx}</td>
                                <td><b>{row['Khoảng cách (m)']}</b></td>
                                <td>{row[col_ten_tram]}</td>
                                <td>{row[col_ma_tram]}</td>
                                <td>{row[col_trang_thai]}</td>
                                <td>{loai_tram_val}</td>
                                <td>{row[col_tinh]}</td>
                                <td>{row[col_mien_dia_ly]}</td>
                                <td>{lat_val}</td>
                                <td>{long_val}</td>
                                <td style="text-align: center;">
                                    <button class="copy-btn" onclick="copyToClipboard('{coord_str}', this)">📋 Copy</button>
                                </td>
                            </tr>
                        """

                    html_code += """
                        </tbody>
                    </table>
                    """

                    st.components.v1.html(html_code, height=320, scrolling=True)

            except ValueError:
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng đảm bảo chỉ nhập số, ví dụ: 10.734728, 106.663666")
        else:
            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ phân tách bởi dấu phẩy.")

except FileNotFoundError:
    st.error("Không tìm thấy file 'DATA Trạm.xlsx'. Bạn hãy đảm bảo file này đã được tải lên cùng thư mục trên GitHub.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi: {e}")

import streamlit as st
import pandas as pd

# 1. CẤU HÌNH HỆ THỐNG
st.set_page_config(page_title="Quản Lý Lương STK", layout="wide")

def format_money(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập Quản trị viên")
    user = st.text_input("Tài khoản")
    pw = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Hệ Thống Quản Lý Lương STK")
    tab1, tab2 = st.tabs(["📄 Xem File Excel Có Sẵn", "📝 Tính Lương Mới (Luật LĐ)"])

    # --- TAB 1: ĐỌC FILE EXCEL ---
    with tab1:
        uploaded_file = st.file_uploader("Tải file Excel (.xlsx)", type=["xlsx"], key="tab1_upload")
        if uploaded_file:
            excel_data = pd.ExcelFile(uploaded_file)
            selected_sheet = st.selectbox("Chọn Table:", excel_data.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet).fillna("")
            df_fmt = df.copy()
            for col in df_fmt.columns:
                df_fmt[col] = df_fmt[col].apply(format_money)
            st.dataframe(df_fmt, use_container_width=True)

    # --- TAB 2: TÍNH LƯƠNG THEO LUẬT LAO ĐỘNG ---
    with tab2:
        st.header("🧮 Công cụ tính lương & Thuế TNCN")
        with st.form("calc_form"):
            c1, c2 = st.columns(2)
            with c1:
                ten = st.text_input("Họ và Tên NV")
                l_chinh = st.number_input("Lương chính (Lương đóng BH)", min_value=0, step=100000)
                pc_an = st.number_input("Phụ cấp ăn trưa (Miễn thuế < 730k)", min_value=0, value=730000)
                pc_khac = st.number_input("Phụ cấp khác (Điện thoại, xăng xe...)", min_value=0)
            with c2:
                thuong = st.number_input("Thưởng / Thu nhập khác", min_value=0)
                nguoi_phu_thuoc = st.number_input("Số người phụ thuộc", min_value=0, step=1)
                gio_tang_ca = st.number_input("Tiền tăng ca (Miễn thuế phần chênh lệch)", min_value=0)

            if st.form_submit_button("Tính Lương & Kết Xuất Phiếu"):
                # --- LOGIC TÍNH TOÁN THEO LUẬT ---
                # 1. Bảo hiểm (8% Hưu trí, 1.5% BHYT, 1% BHTN = 10.5%)
                bh_dv = l_chinh * 0.105 
                
                # 2. Thu nhập chịu thuế (TNCT)
                # TNCT = Tổng thu nhập - Ăn trưa miễn thuế - Tăng ca miễn thuế
                tong_tn = l_chinh + pc_an + pc_khac + thuong + gio_tang_ca
                tn_chịu_thue = tong_tn - min(pc_an, 730000) - bh_dv
                
                # 3. Các khoản giảm trừ
                giam_tru_ca_nhan = 11000000
                giam_tru_phu_thuoc = nguoi_phu_thuoc * 4400000
                tn_tinh_thue = max(0, tn_chịu_thue - giam_tru_ca_nhan - giam_tru_phu_thuoc)
                
                # 4. Tính thuế TNCN lũy tiến
                thue = 0
                if tn_tinh_thue <= 5000000: thue = tn_tinh_thue * 0.05
                elif tn_tinh_thue <= 10000000: thue = tn_tinh_thue * 0.1 - 250000
                elif tn_tinh_thue <= 18000000: thue = tn_tinh_thue * 0.15 - 750000
                elif tn_tinh_thue <= 32000000: thue = tn_tinh_thue * 0.2 - 1650000
                else: thue = tn_tinh_thue * 0.25 - 3250000 # Rút gọn các bậc cao
                
                thuc_nhan = tong_tn - bh_dv - thue
                
                # --- HIỂN THỊ KẾT QUẢ ---
                st.divider()
                st.subheader(f"📑 Phiếu Lương: {ten}")
                res_df = pd.DataFrame({
                    "Hạng mục": ["Tổng thu nhập", "Bảo hiểm trừ lương (10.5%)", "Giảm trừ gia cảnh (Bản thân)", "Giảm trừ người phụ thuộc", "Thuế TNCN phải nộp", "THỰC NHẬN (Lương Net)"],
                    "Số tiền (VNĐ)": [tong_tn, bh_dv, giam_tru_ca_nhan, giam_tru_phu_thuoc, thue, thuc_nhan]
                })
                res_df["Số tiền (VNĐ)"] = res_df["Số tiền (VNĐ)"].apply(format_money)
                st.table(res_df)
                st.balloons()

# 4. THANH BÊN (SIDEBAR)
st.sidebar.markdown("---")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()
st.sidebar.info("Luật áp dụng: Giảm trừ gia cảnh 11tr/tháng, BH 10.5%")

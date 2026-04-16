import streamlit as st
import pandas as pd

# 1. CẤU HÌNH HỆ THỐNG
st.set_page_config(page_title="Quản Lý Lương STK", layout="wide")

# Hàm định dạng tiền tệ có dấu phẩy
def format_money(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# Hàm hiển thị gợi ý số tiền bằng chữ để không nhập nhầm
def gợi_ý_tiền(n):
    if n == 0: return ""
    if n >= 1000000: return f"👉 Số tiền: **{format_money(n)}** ({n/1000000:.2f} triệu đồng)"
    if n >= 1000: return f"👉 Số tiền: **{format_money(n)}** ({n/1000:.0f} ngàn đồng)"
    return f"👉 Số tiền: {format_money(n)}"

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập Quản trị viên")
    c1, c2 = st.columns([1,2])
    with c1:
        user = st.text_input("Tài khoản")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if user == "admin" and pw == "123":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Sai thông tin!")
else:
    # 3. GIAO DIỆN CHÍNH
    st.title("📊 Hệ Thống Quản Lý Lương STK")
    tab1, tab2 = st.tabs(["📄 Tra Cứu File Excel", "📝 Tính Lương & Thuế (Luật LĐ)"])

    # --- TAB 1: XEM FILE EXCEL ---
    with tab1:
        uploaded_file = st.file_uploader("Tải file Excel (.xlsx)", type=["xlsx"], key="tab1_upload")
        if uploaded_file:
            excel_data = pd.ExcelFile(uploaded_file)
            selected_sheet = st.selectbox("Chọn bảng (Sheet) cần xem:", excel_data.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet).fillna("")
            # Định dạng dấu phẩy cho bảng hiển thị
            df_display = df.copy().astype(str)
            st.dataframe(df_display, use_container_width=True)

    # --- TAB 2: TÍNH LƯƠNG MỚI ---
    with tab2:
        st.header("🧮 Công cụ tính lương & Thuế TNCN")
        st.info("💡 Lưu ý: Không gõ dấu chấm/phẩy. Ví dụ 6.5 triệu thì gõ 6500000")
        
        with st.form("calc_form"):
            col1, col2 = st.columns(2)
            with col1:
                ten = st.text_input("Họ và Tên NV", value="Nguyễn Văn A")
                l_chinh = st.number_input("Lương chính (Đóng BH)", min_value=0, step=100000, value=6500000)
                st.markdown(gợi_ý_tiền(l_chinh))
                
                pc_an = st.number_input("Phụ cấp ăn trưa", min_value=0, value=730000)
                st.markdown(gợi_ý_tiền(pc_an))
                
                pc_khac = st.number_input("Phụ cấp khác (Điện thoại, xăng xe...)", min_value=0, value=0)
                st.markdown(gợi_ý_tiền(pc_khac))
            
            with col2:
                nguoi_phu_thuoc = st.number_input("Số người phụ thuộc", min_value=0, max_value=20, step=1, value=0)
                thuong = st.number_input("Thưởng / Thu nhập khác", min_value=0, step=100000, value=0)
                st.markdown(gợi_ý_tiền(thuong))
                
                gio_tang_ca = st.number_input("Tiền tăng ca (Phần miễn thuế)", min_value=0, value=0)
                st.markdown(gợi_ý_tiền(gio_tang_ca))

            submit = st.form_submit_button("TÍNH LƯƠNG & XUẤT PHIẾU")

            if submit:
                # --- LOGIC TÍNH TOÁN ---
                bh_dv = l_chinh * 0.105 # BHXH 10.5%
                tong_tn = l_chinh + pc_an + pc_khac + thuong + gio_tang_ca
                
                # Tính thuế TNCN
                tn_chiu_thue = tong_tn - min(pc_an, 730000) - gio_tang_ca
                giam_tru_ca_nhan = 11000000
                giam_tru_phu_thuoc = nguoi_phu_thuoc * 4400000
                tn_tinh_thue = max(0, tn_chiu_thue - bh_dv - giam_tru_ca_nhan - giam_tru_phu_thuoc)
                
                # Biểu thuế lũy tiến
                def tinh_thue(tntt):
                    if tntt <= 5000000: return tntt * 0.05
                    if tntt <= 10000000: return tntt * 0.1 - 250000
                    if tntt <= 18000000: return tntt * 0.15 - 750000
                    if tntt <= 32000000: return tntt * 0.2 - 1650000
                    return tntt * 0.25 - 3250000

                thue_phai_nop = tinh_thue(tn_tinh_thue)
                thuc_nhan = tong_tn - bh_dv - thue_phai_nop

                # --- HIỂN THỊ KẾT QUẢ ---
                st.divider()
                st.success(f"### 📑 PHIẾU LƯƠNG: {ten.upper()}")
                
                res_data = {
                    "Nội dung diễn giải": ["Tổng thu nhập", "Bảo hiểm trừ lương (10.5%)", "Giảm trừ cá nhân", "Giảm trừ người phụ thuộc", "Thu nhập tính thuế", "Thuế TNCN phải nộp", "THỰC NHẬN (Lương Net)"],
                    "Số tiền (VNĐ)": [tong_tn, -bh_dv, -giam_tru_ca_nhan, -giam_tru_phu_thuoc, tn_tinh_thue, -thue_phai_nop, thuc_nhan]
                }
                res_df = pd.DataFrame(res_data)
                res_df["Số tiền (VNĐ)"] = res_df["Số tiền (VNĐ)"].apply(format_money)
                st.table(res_df)
                st.balloons()

# 4. THANH BÊN
st.sidebar.markdown("---")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()
st.sidebar.info("Hệ thống STK v1.4 - Tính lương chuẩn 2026")

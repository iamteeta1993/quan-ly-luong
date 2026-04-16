import streamlit as st
import pandas as pd

# 1. CẤU HÌNH
st.set_page_config(page_title="Quản Lý Lương STK", layout="wide")

def format_money(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập Admin")
    user = st.text_input("Tài khoản")
    pw = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Hệ Thống Quản Lý Lương STK")
    tab1, tab2 = st.tabs(["📄 Xem File Excel", "📝 Tính Lương (Nhập Tắt)"])

    with tab1:
        uploaded_file = st.file_uploader("Tải file Excel", type=["xlsx"], key="tab1")
        if uploaded_file:
            excel_data = pd.ExcelFile(uploaded_file)
            sheet = st.selectbox("Chọn Table:", excel_data.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet).fillna("")
            st.dataframe(df.astype(str), use_container_width=True)

    with tab2:
        st.header("🧮 Công cụ tính lương nhanh")
        st.info("💡 **Quy tắc nhập tắt:** Bạn nhập số, App tự nhân với 1.000. \n\n (Ví dụ: Gõ **6500** = 6.5 triệu | Gõ **650** = 650 ngàn)")
        
        with st.form("calc_form"):
            c1, c2 = st.columns(2)
            with c1:
                ten = st.text_input("Họ và Tên NV", value="Nguyễn Văn A")
                
                # Logic nhập tắt: Số nhập vào sẽ được nhân với 1000
                nhap_lương = st.number_input("Nhập lương chính (viết tắt)", min_value=0, value=6500)
                l_chinh = nhap_lương * 1000
                st.success(f"💰 Lương chính: **{format_money(l_chinh)} VNĐ**")
                
                nhap_an_trua = st.number_input("Nhập phụ cấp ăn trưa (viết tắt)", min_value=0, value=730)
                pc_an = nhap_an_trua * 1000
                st.caption(f"👉 Số tiền: {format_money(pc_an)} VNĐ")

            with c2:
                nguoi_phu_thuoc = st.number_input("Số người phụ thuộc", min_value=0, step=1, value=0)
                
                nhap_thuong = st.number_input("Nhập thưởng/khác (viết tắt)", min_value=0, value=0)
                thuong = nhap_thuong * 1000
                st.caption(f"👉 Số tiền: {format_money(thuong)} VNĐ")

            submit = st.form_submit_button("TÍNH LƯƠNG & XUẤT PHIẾU")

            if submit:
                # Bảo hiểm 10.5%
                bh_dv = l_chinh * 0.105 
                tong_tn = l_chinh + pc_an + thuong
                
                # Thuế TNCN (Giảm trừ cá nhân 11tr, phụ thuộc 4.4tr)
                tn_chiu_thue = tong_tn - min(pc_an, 730000)
                tn_tinh_thue = max(0, tn_chiu_thue - bh_dv - 11000000 - (nguoi_phu_thuoc * 4400000))
                
                # Tính thuế lũy tiến (rút gọn)
                tntt = tn_tinh_thue
                if tntt <= 0: thue = 0
                elif tntt <= 5000000: thue = tntt * 0.05
                elif tntt <= 10000000: thue = tntt * 0.1 - 250000
                else: thue = tntt * 0.15 - 750000

                thuc_nhan = tong_tn - bh_dv - thue
                
                st.divider()
                st.success(f"### THỰC NHẬN: {format_money(thuc_nhan)} VNĐ")
                
                # Bảng chi tiết
                data = {
                    "Nội dung": ["Lương chính", "Phụ cấp ăn trưa", "Thưởng/Khác", "Bảo hiểm (10.5%)", "Thuế TNCN", "THỰC NHẬN"],
                    "Số tiền (VNĐ)": [format_money(l_chinh), format_money(pc_an), format_money(thuong), format_money(-bh_dv), format_money(-thue), format_money(thuc_nhan)]
                }
                st.table(pd.DataFrame(data))

st.sidebar.button("Đăng xuất", on_click=lambda: st.session_state.pop("authenticated"))

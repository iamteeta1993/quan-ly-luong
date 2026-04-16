import streamlit as st
import pandas as pd

# 1. CẤU HÌNH
st.set_page_config(page_title="Quản Lý Lương STK 2026", layout="wide")

def format_money(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Hệ Thống Lương STK - Luật 2026")
    user = st.text_input("Tài khoản", value="admin")
    pw = st.text_input("Mật khẩu", type="password", value="123")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Tính Lương Tăng Ca & BHXH (x1000)")
    
    with st.form("salary_form_stk_v3"):
        # --- PHẦN 1: 3 CHỈ SỐ GỐC ---
        st.subheader("📌 3 Chỉ Số Căn Cứ (Nhập tắt x1000)")
        c1, c2, c3 = st.columns(3)
        with c1:
            val_tong_luong = st.number_input("TỔNG LƯƠNG (Gross)", value=12000)
            tong_luong = val_tong_luong * 1000
        with c2:
            val_luong_tc = st.number_input("Lương tính TĂNG CA", value=8780)
            luong_tc = val_luong_tc * 1000
            l_gio = luong_tc / 208 # Mặc định 26 ngày công chuẩn (26 x 8 = 208 giờ)
            st.caption(f"⚙️ Lương 1 giờ: {format_money(l_gio)} đ")
        with c3:
            val_luong_bh = st.number_input("Lương tham gia BHXH", value=6500)
            luong_bh = val_luong_bh * 1000

        st.divider()

        # --- PHẦN 2: TÍNH GIỜ LÀM THÊM ---
        st.subheader("🕒 Nhập giờ làm thêm (Giờ thực tế)")
        col1, col2, col3 = st.columns(3)
        with col1:
            g_ngay = st.number_input("Giờ tăng ca NGÀY (150%)", min_value=0.0, step=0.5, value=0.0)
        with col2:
            g_dem_chinh = st.number_input("Giờ CA ĐÊM chính (130%)", min_value=0.0, step=0.5, value=0.0)
        with col3:
            g_tc_dem = st.number_input("Giờ TĂNG CA ĐÊM (210%)", min_value=0.0, step=0.5, value=0.0)

        # --- PHẦN 3: GIẢM TRỪ ---
        st.subheader("📉 Khấu trừ & Giảm trừ")
        col_a, col_b = st.columns(2)
        with col_a:
            phu_thuoc = st.number_input("Số người phụ thuộc", min_value=0, step=1, value=0)
        with col_b:
            tam_ung = st.number_input("Tạm ứng / Truy thu (x1000)", value=0) * 1000

        submit = st.form_submit_button("TÍNH TOÁN THỰC NHẬN")

        if submit:
            # --- TÍNH TIỀN TĂNG CA ---
            tien_tc_ngay = g_ngay * l_gio * 1.5
            tien_ca_dem = g_dem_chinh * l_gio * 0.3 # Phụ cấp 30% làm đêm
            tien_tc_dem = g_tc_dem * l_gio * 2.1 # 150% + 30% + (20%*150%) = 210%
            tong_tien_tc = tien_tc_ngay + tien_ca_dem + tien_tc_dem

            # --- TÍNH BẢO HIỂM & THUẾ ---
            bh_105 = luong_bh * 0.105
            
            # Thu nhập chịu thuế (Miễn thuế phần tăng ca chênh lệch)
            tn_chiu_thue = (tong_luong + tong_tien_tc) - 730000 - (tien_tc_ngay/3) - (tien_tc_dem * 1.1/2.1)
            
            giam_tru = 11000000 + (phu_thuoc * 4400000)
            tn_tinh_thue = max(0, tn_chiu_thue - bh_105 - giam_tru)
            
            def tinh_thue(tntt):
                if tntt <= 5000000: return tntt * 0.05
                elif tntt <= 10000000: return tntt * 0.1 - 250000
                else: return tntt * 0.15 - 750000
            
            thue_tncn = tinh_thue(tn_tinh_thue)
            thuc_nhan = (tong_luong + tong_tien_tc) - bh_105 - thue_tncn - tam_ung

            # --- HIỂN THỊ ---
            st.success(f"### ⭐ THU NHẬP THỰC NHẬN: {format_money(thuc_nhan)} VNĐ")
            
            res = {
                "Hạng mục": ["Lương chính + PC", "Tiền tăng ca (Ngày/Đêm)", "Bảo hiểm trích lương", "Thuế TNCN", "Tạm ứng/Truy thu", "THỰC NHẬN"],
                "Số tiền": [format_money(tong_luong), format_money(tong_tien_tc), format_money(-bh_105), format_money(-thue_tncn), format_money(-tam_ung), format_money(thuc_nhan)]
            }
            st.table(pd.DataFrame(res))
            
            with st.expander("Chi tiết cách tính tăng ca"):
                st.write(f"- Đơn giá 1 giờ: **{format_money(l_gio)} đ**")
                st.write(f"- Tăng ca ngày (x1.5): {format_money(tien_tc_ngay)} đ")
                st.write(f"- Phụ cấp ca đêm (+30%): {format_money(tien_ca_dem)} đ")
                st.write(f"- Tăng ca đêm (x2.1): {format_money(tien_tc_dem)} đ")

st.sidebar.markdown("---")
st.sidebar.write("Hệ thống STK v1.6")

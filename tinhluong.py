import streamlit as st
import pandas as pd

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Phần mềm Lương STK 2026", layout="wide")

def format_money(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập Admin - CÔNG TY STK")
    user = st.text_input("Tài khoản")
    pw = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai tài khoản hoặc mật khẩu!")
else:
    st.title("📊 Quản Lý & Tính Lương STK (Luật 2026)")
    st.info("💡 **Mẹo nhập nhanh:** App tự nhân 1.000. Ví dụ: gõ **6654** sẽ hiểu là **6,654,000 VNĐ**")
    
    with st.form("salary_form"):
        # --- PHẦN 1: THÔNG TIN NHÂN VIÊN ---
        st.subheader("📌 Thông tin nhân viên")
        c1, c2, c3 = st.columns(3)
        with c1:
            ma_nv = st.text_input("Mã số nhân viên", value="THA32")
        with c2:
            ho_ten = st.text_input("Họ & Tên", value="CAO NGỌC THẮNG")
        with c3:
            ngay_lam = st.text_input("Ngày bắt đầu làm việc", value="14/03/2025")

        st.divider()

        # --- PHẦN 2: THU NHẬP CHUẨN (DỰA TRÊN ẢNH) ---
        st.subheader("💰 Thu nhập & Phụ cấp (Nhập tắt x1000)")
        col1, col2 = st.columns(2)
        
        with col1:
            val_l_bac = st.number_input("Lương theo bậc", value=6654) # 6,654,000
            l_bac = val_l_bac * 1000
            st.caption(f"👉 Thực tính: {format_money(l_bac)}")

            val_pc_tn = st.number_input("Phụ cấp trách nhiệm quản lý", value=563)
            pc_tn = val_pc_tn * 1000
            
            val_thuong_ns = st.number_input("Thưởng kiểm soát năng suất SP", value=3302)
            thuong_ns = val_thuong_ns * 1000
            
            val_ngoai_gio_thue = st.number_input("TN ngoài giờ (Phải chịu thuế)", value=0)
            ngoai_gio_thue = val_ngoai_gio_thue * 1000

        with col2:
            val_pc_xang = st.number_input("Phụ cấp xăng xe / Đi lại", value=500)
            pc_xang = val_pc_xang * 1000
            
            val_pc_com = st.number_input("Phụ cấp cơm giữa ca (Miễn thuế)", value=720)
            pc_com = val_pc_com * 1000

            val_ngoai_gio_mien = st.number_input("TN ngoài giờ (Không chịu thuế)", value=840)
            ngoai_gio_mien = val_ngoai_gio_mien * 1000

            so_nguoi_pt = st.number_input("Số người phụ thuộc (Giảm trừ gia cảnh)", min_value=0, step=1, value=0)

        submit = st.form_submit_button("TÍNH LƯƠNG THỰC NHẬN")

        if submit:
            # --- LOGIC TÍNH TOÁN THEO LUẬT VIỆT NAM 2026 ---
            
            # 1. Tổng lương (Chưa tính tăng ca miễn thuế)
            tong_luong = l_bac + pc_tn + thuong_ns + pc_xang + pc_com + ngoai_gio_thue
            
            # 2. Tổng thu nhập tháng
            tong_thu_nhap = tong_luong + ngoai_gio_mien
            
            # 3. Bảo hiểm trích từ lương (10.5% tính trên Lương bậc + PC Trách nhiệm)
            luong_dong_bh = l_bac + pc_tn
            bh_khau_tru = luong_dong_bh * 0.105
            
            # 4. Thu nhập chịu thuế TNCN
            # Thu nhập chịu thuế = Tổng TN - Cơm trưa (max 730k) - Ngoài giờ miễn thuế
            tn_chiu_thue = tong_thu_nhap - min(pc_com, 730000) - ngoai_gio_mien
            
            # 5. Các khoản giảm trừ
            giam_tru_ban_than = 11000000
            giam_tru_phu_thuoc = so_nguoi_pt * 4400000
            
            # 6. Thu nhập tính thuế
            tn_tinh_thue = max(0, tn_chiu_thue - bh_khau_tru - giam_tru_ban_than - giam_tru_phu_thuoc)
            
            # 7. Tính thuế TNCN lũy tiến
            def tinh_thue_tncn(tntt):
                if tntt <= 5000000: return tntt * 0.05
                elif tntt <= 10000000: return tntt * 0.1 - 250000
                elif tntt <= 18000000: return tntt * 0.15 - 750000
                elif tntt <= 32000000: return tntt * 0.2 - 1650000
                else: return tntt * 0.25 - 3250000

            thue_tncn = tinh_thue_tncn(tn_tinh_thue)
            
            # 8. THU NHẬP THỰC NHẬN CUỐI CÙNG
            thuc_nhan = tong_thu_nhap - bh_khau_tru - thue_tncn

            # --- HIỂN THỊ KẾT QUẢ THEO CẤU TRÚC ẢNH ---
            st.success(f"### ✅ BẢNG TÍNH LƯƠNG THỰC NHẬN: {ho_ten.upper()}")
            
            ket_qua = {
                "Cấu trúc bảng lương": [
                    "Lương theo bậc", "Phụ cấp trách nhiệm", "Thưởng năng suất", "TN ngoài giờ (Miễn thuế)",
                    "Phụ cấp cơm / Xăng xe", "---", "TỔNG THU NHẬP THÁNG", 
                    "Bảo hiểm xã hội (10.5%)", "Giảm trừ gia cảnh bản thân", "Thuế TNCN phải nộp", "---",
                    "TỔNG TIỀN THỰC NHẬN CÒN LẠI"
                ],
                "Số tiền (VNĐ)": [
                    format_money(l_bac), format_money(pc_tn), format_money(thuong_ns), format_money(ngoai_gio_mien),
                    format_money(pc_com + pc_xang), "", format_money(tong_thu_nhap),
                    format_money(-bh_khau_tru), format_money(-giam_tru_ban_than), format_money(-thue_tncn), "",
                    f"⭐ {format_money(thuc_nhan)}"
                ]
            }
            st.table(pd.DataFrame(ket_qua))
            st.balloons()

# Sidebar
st.sidebar.markdown("---")
st.sidebar.write("Hệ thống lương Công ty STK")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

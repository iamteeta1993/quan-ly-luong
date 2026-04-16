import streamlit as st
import pandas as pd

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Quản Lý Lương STK 2026", layout="wide")

def format_money(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập Admin - CÔNG TY STK")
    user = st.text_input("Tài khoản", value="admin")
    pw = st.text_input("Mật khẩu", type="password", value="123")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Quản Lý Lương & Đối Chiếu Công Chuẩn")
    st.info("💡 **Gợi ý:** Nhập tắt x1000. Ví dụ: gõ 12666 = 12,666,000 VNĐ")
    
    with st.form("salary_form_v2"):
        st.subheader("📌 Thông tin nhân viên & Ngày công")
        c1, c2, c3 = st.columns(3)
        with c1:
            thang_nam = st.selectbox("Tháng đối soát", ["01/2026", "02/2026", "03/2026", "04/2026"])
            ma_nv = st.text_input("Mã số nhân viên", value="THA32")
        with c2:
            ho_ten = st.text_input("Họ & Tên", value="CAO NGỌC THẮNG")
            so_cong_thuc_te = st.number_input("Số ngày làm việc thực tế", min_value=0, max_value=31, value=24)
        with c3:
            # Hai mục bạn yêu cầu bổ sung
            val_tn_24 = st.number_input("Thu nhập TỔNG 24 công (x1000)", value=12666)
            val_tn_26 = st.number_input("Thu nhập TỔNG 26 công (x1000)", value=13721)

        st.divider()

        st.subheader("💰 Chi tiết thu nhập & Khấu trừ (x1000)")
        col1, col2 = st.columns(2)
        with col1:
            l_bac = st.number_input("Lương theo bậc", value=6654) * 1000
            pc_tn = st.number_input("Phụ cấp trách nhiệm", value=563) * 1000
            thuong_ns = st.number_input("Thưởng năng suất SP", value=3302) * 1000
            ngoai_gio_mien = st.number_input("Ngoài giờ không thuế", value=840) * 1000
        with col2:
            pc_com_xang = st.number_input("Phụ cấp Cơm + Xăng", value=1220) * 1000
            phu_thuoc = st.number_input("Số người phụ thuộc", min_value=0, value=0)
            tam_ung = st.number_input("Tạm ứng / Truy thu", value=0) * 1000

        submit = st.form_submit_button("TÍNH LƯƠNG THỰC NHẬN")

        if submit:
            # Chuyển đổi giá trị nhập tắt
            tn_24 = val_tn_24 * 1000
            tn_26 = val_tn_26 * 1000
            
            # --- LOGIC ĐỐI CHIẾU THEO CÔNG CHUẨN ---
            # Tính lương 1 ngày dựa trên thu nhập tổng đã nhập
            luong_1_ngay_24 = tn_24 / 24
            luong_1_ngay_26 = tn_26 / 26
            
            # Tính thu nhập dựa trên số ngày làm thực tế (chọn mẫu 24 công phổ biến)
            tn_thuc_te = luong_1_ngay_24 * so_cong_thuc_te 

            # Bảo hiểm 10.5% (Lương bậc + PC trách nhiệm)
            bh_105 = (l_bac + pc_tn) * 0.105
            
            # Giảm trừ gia cảnh 2026: 11tr cá nhân + 4.4tr phụ thuộc
            tn_chiu_thue = tn_thuc_te - 730000 - ngoai_gio_mien # Miễn thuế ăn trưa & ngoài giờ
            tn_tinh_thue = max(0, tn_chiu_thue - bh_105 - 11000000 - (phu_thuoc * 4400000))
            
            # Thuế TNCN lũy tiến
            def tinh_thue(tntt):
                if tntt <= 5000000: return tntt * 0.05
                elif tntt <= 10000000: return tntt * 0.1 - 250000
                else: return tntt * 0.15 - 750000
            thue_tncn = tinh_thue(tn_tinh_thue)

            # THU NHẬP THỰC NHẬN CUỐI CÙNG
            thuc_nhan = tn_thuc_te - bh_105 - thue_tncn - tam_ung

            # HIỂN THỊ KẾT QUẢ ĐỐI SOÁT
            st.success(f"### 📑 PHIẾU LƯƠNG ĐỐI SOÁT {thang_nam}")
            res = {
                "Hạng mục đối soát": ["Thu nhập tổng (24 công)", "Thu nhập tổng (26 công)", "Ngày công thực tế", "Thu nhập thực tế theo ngày công", "Bảo hiểm (10.5%)", "Thuế TNCN", "THỰC NHẬN CÒN LẠI"],
                "Số tiền / Giá trị": [format_money(tn_24), format_money(tn_26), f"{so_cong_thuc_te} ngày", format_money(tn_thuc_te), format_money(-bh_105), format_money(-thue_tncn), f"⭐ {format_money(thuc_nhan)}"]
            }
            st.table(pd.DataFrame(res))
            st.balloons()

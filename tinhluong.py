import streamlit as st
import pandas as pd

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Phần Mềm Lương STK - Full Version", layout="wide")

def fmt(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Hệ Thống Quản Lý Lương STK")
    user = st.text_input("Tài khoản", value="admin")
    pw = st.text_input("Mật khẩu", type="password", value="123")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Bảng Tính Lương Chi Tiết STK (Luật 2026)")
    st.info("💡 Mẹo: Nhập số tiền viết tắt (x1000). Ví dụ: 6654 = 6,654,000đ")

    with st.form("stk_full_form"):
        # --- PHẦN 1: THÔNG TIN CƠ BẢN ---
        st.subheader("📌 1. Thông tin nhân viên")
        c1, c2, c3, c4 = st.columns(4)
        with c1: ma_nv = st.text_input("Mã số nhân viên", value="THA32")
        with c2: phong_ban = st.text_input("Phòng ban làm việc", value="Sản Xuất")
        with c3: ho_ten = st.text_input("Họ & Tên", value="CAO NGỌC THẮNG")
        with c4: ngay_vao = st.text_input("Ngày bắt đầu làm việc", value="14/03/2025")

        # --- PHẦN 2: THU NHẬP CHUẨN & PHỤ CẤP ---
        st.subheader("💰 2. Thu nhập chuẩn & Các khoản phụ cấp (Nhập x1000)")
        c5, c6, c7 = st.columns(3)
        with c5:
            tn_chuan = st.number_input("THU NHẬP CHUẨN / Tháng (24 công)", value=12666) * 1000
            luong_bh = st.number_input("Lương tham gia BH (Bậc + PC)", value=6500) * 1000
            luong_bac = st.number_input("Lương theo bậc", value=6654) * 1000
            pc_tn = st.number_input("Phụ cấp trách nhiệm quản lý", value=563) * 1000
        with c6:
            thuong_ns = st.number_input("Thưởng kiểm soát năng suất SP", value=3302) * 1000
            pc_doc_hai = st.number_input("Phụ cấp độc hại, nặng nhọc...", value=500) * 1000
            pc_di_lai = st.number_input("Phụ cấp đi lại (xăng xe)", value=500) * 1000
            pc_dt = st.number_input("Phụ cấp điện thoại", value=0) * 1000
        with c7:
            chuyen_can = st.number_input("Thưởng chuyên cần", value=500) * 1000
            pc_com = st.number_input("Phụ cấp cơm giữa ca", value=720) * 1000
            tn_ngoai_gio_thue = st.number_input("TN ngoài giờ CHỊU THUẾ", value=0) * 1000
            so_ngay_lam = st.number_input("Số ngày làm việc thực tế", value=24)

        # --- PHẦN 3: TĂNG CA & THỜI GIAN ---
        st.subheader("🕒 3. Chi tiết giờ làm thêm & Thưởng năm")
        c8, c9, c10 = st.columns(3)
        l_gio = luong_bac / 208 # Tính đơn giá 1 giờ dựa trên 26 công
        with c8:
            g_ngay = st.number_input("Số giờ làm thêm (Ban ngày - 150%)", value=0.0, step=0.5)
            g_dem = st.number_input("Số giờ làm thêm (Ban đêm - 210%)", value=0.0, step=0.5)
            g_cn = st.number_input("Số giờ làm thêm (Chủ nhật - 200%)", value=0.0, step=0.5)
        with c9:
            g_le = st.number_input("Số giờ làm thêm (Lễ - 300%)", value=0.0, step=0.5)
            tre_ngay = st.number_input("Số giờ đi trễ/về sớm - NGÀY", value=0.0, step=0.1)
            tre_dem = st.number_input("Số giờ đi trễ/về sớm - ĐÊM", value=0.0, step=0.1)
        with c10:
            phep_nam = st.number_input("Phép năm chưa sử dụng (x1000)", value=0) * 1000
            thuong_13 = st.number_input("THƯỞNG THÁNG 13 (x1000)", value=0) * 1000
            tn_ngoai_gio_ko_thue = st.number_input("TN ngoài giờ MIỄN THUẾ", value=840) * 1000

        # --- PHẦN 4: ĐIỀU CHỈNH & QUYẾT TOÁN ---
        st.subheader("🔄 4. Điều chỉnh lương & Khoản trừ khác (x1000)")
        c11, c12 = st.columns(2)
        with c11:
            chi_hoan = st.number_input("CHI HOÀN TIỀN... (nếu có)", value=0) * 1000
            tam_thu = st.number_input("TẠM THU TIỀN... (nếu có)", value=0) * 1000
            hoan_tra = st.number_input("Hoàn trả tiền lương (nếu có)", value=0) * 1000
        with c12:
            phi_cd = st.number_input("Phí Công đoàn (thường 1%)", value=40) * 1000
            truy_thu_bh = st.number_input("Truy thu BHYT 4.5%", value=0) * 1000
            qt_thue_hoan = st.number_input("QUYẾT TOÁN Thuế (+) Được hoàn", value=0) * 1000
            qt_thue_dong = st.number_input("QUYẾT TOÁN Thuế (-) Đóng thêm", value=0) * 1000

        submit = st.form_submit_button("TÍNH TOÁN VÀ XUẤT PHIẾU THỰC NHẬN")

        if submit:
            # --- TÍNH TOÁN TIỀN TĂNG CA ---
            tien_tc = (g_ngay * l_gio * 1.5) + (g_dem * l_gio * 2.1) + (g_cn * l_gio * 2.0) + (g_le * l_gio * 3.0)
            tien_phat_tre = (tre_ngay * l_gio) + (tre_dem * l_gio * 1.3)
            
            # --- TỔNG LƯƠNG & TỔNG THU NHẬP ---
            tong_luong = luong_bac + pc_tn + thuong_ns + pc_doc_hai + pc_di_lai + pc_dt + chuyen_can + pc_com + tn_ngoai_gio_thue
            tong_tn_thang = tong_luong + phep_nam + thuong_13 + tn_ngoai_gio_ko_thue + tien_tc - tien_phat_tre
            
            # --- KHẤU TRỪ ---
            bh_105 = luong_bh * 0.105
            giam_tru_bh = 11000000 # Giảm trừ cá nhân luật 2026
            tn_tinh_thue = max(0, tong_tn_thang - bh_105 - pc_com - tn_ngoai_gio_ko_thue - giam_tru_bh)
            
            def tinh_thue(tntt):
                if tntt <= 5000000: return tntt * 0.05
                elif tntt <= 10000000: return tntt * 0.1 - 250000
                else: return tntt * 0.15 - 750000
            thue_tncn = tinh_thue(tn_tinh_thue)

            # --- TỔNG THỰC NHẬN ---
            thuc_nhan = tong_tn_thang - bh_105 - phi_cd - thue_tncn + chi_hoan - tam_thu + hoan_tra - truy_thu_bh + qt_thue_hoan - qt_thue_dong
            cty_dong = luong_bh * 0.235 # 23.5% Công ty đóng

            # --- HIỂN THỊ KẾT QUẢ ---
            st.success(f"### 🏆 TỔNG TIỀN THỰC NHẬN CÒN LẠI: {fmt(thuc_nhan)} VNĐ")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**📊 Tóm tắt thu nhập:**")
                st.write(f"- Tổng lương: {fmt(tong_luong)} đ")
                st.write(f"- Tiền tăng ca: {fmt(tien_tc)} đ")
                st.write(f"- Phụ cấp & Thưởng khác: {fmt(phep_nam + thuong_13)} đ")
            with col_b:
                st.write("**📉 Tóm tắt khấu trừ:**")
                st.write(f"- Bảo hiểm (10.5%): -{fmt(bh_105)} đ")
                st.write(f"- Thuế TNCN: -{fmt(thue_tncn)} đ")
                st.write(f"- Phí công đoàn: -{fmt(phi_cd)} đ")

            st.info(f"🏢 Công ty đóng thêm bảo hiểm cho bạn (23.5%): {fmt(cty_dong)} VNĐ")
            st.balloons()

# Sidebar
st.sidebar.markdown("---")
st.sidebar.write("Hệ thống STK v2.0 - Full Structure")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

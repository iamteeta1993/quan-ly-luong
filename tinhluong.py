import streamlit as st
import pandas as pd

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Hệ thống Lương STK - Full Tự Động", layout="wide")

def fmt(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Hệ Thống Lương Nội Bộ STK")
    user = st.text_input("Tài khoản", value="admin")
    pw = st.text_input("Mật khẩu", type="password", value="123")
    if st.button("Đăng nhập"):
        st.session_state["authenticated"] = (user == "admin" and pw == "123")
        if st.session_state["authenticated"]: st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Bảng Tính Lương Chi Tiết & Tự Động")
    st.info("💡 **Tính năng:** Nhập số đến đâu, kết quả THỰC NHẬN tự nhảy đến đó.")

    # --- PHẦN 1: THÔNG TIN HÀNH CHÍNH ---
    st.subheader("📌 1. Thông tin chung")
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        ma_nv = st.text_input("Mã số NV", value="THA32")
        so_ngay_lam = st.number_input("Số ngày làm việc", value=24)
    with c2: 
        ho_ten = st.text_input("Họ & Tên", value="CAO NGỌC THẮNG")
        tn_chuan = st.number_input("TN CHUẨN (x1000)", value=12000)
    with c3: 
        ngay_vao = st.text_input("Ngày vào làm", value="14/03/2025")
        l_dong_bh = st.number_input("Lương đóng BH (x1000)", value=6500, help="Dùng tính BHXH 10.5%")
    with c4: 
        phong_ban = st.text_input("Phòng ban", value="Sản Xuất")
        l_tinh_tc = st.number_input("Lương tính TC (x1000)", value=8780, help="Dùng chia lương giờ")

    # --- PHẦN 2: CÁC KHOẢN THU NHẬP (DỰA THEO 43 MỤC) ---
    st.subheader("💰 2. Các khoản Thu nhập (x1000)")
    col1, col2, col3 = st.columns(3)
    with col1:
        l_bac = st.number_input("Lương theo bậc", value=6654)
        pc_tn = st.number_input("PC trách nhiệm", value=569)
        thuong_ns = st.number_input("Thưởng năng suất SP", value=3902)
        pc_com = st.number_input("PC cơm giữa ca", value=720)
    with col2:
        pc_doc_hai = st.number_input("PC độc hại/nuôi con", value=500)
        pc_xang = st.number_input("PC đi lại (xăng xe)", value=500)
        pc_dt = st.number_input("Phụ cấp điện thoại", value=0)
        chuyen_can = st.number_input("Thưởng chuyên cần", value=500)
    with col3:
        tn_ngoai_gio_thue = st.number_input("TN ngoài giờ (chịu thuế)", value=0)
        tn_ngoai_gio_mien = st.number_input("TN ngoài giờ (miễn thuế)", value=840)
        phep_nam = st.number_input("Tiền phép năm", value=0)
        thuong_13 = st.number_input("Thưởng tháng 13", value=0)

    # --- PHẦN 3: TĂNG CA & TRUY THU (CÔNG THỨC LUẬT) ---
    st.subheader("🕒 3. Tăng ca & Các khoản khấu trừ (x1000)")
    ct1, ct2, ct3 = st.columns(3)
    l_gio = (l_tinh_tc * 1000) / 208
    with ct1:
        g_ngay = st.number_input("Giờ TC Ngày (150%)", value=11.0, step=0.5)
        g_dem = st.number_input("Giờ TC Đêm (210%)", value=0.0, step=0.5)
        g_cn = st.number_input("Giờ TC Chủ nhật (200%)", value=0.0, step=0.5)
    with ct2:
        phi_cd = st.number_input("Phí công đoàn", value=40)
        truy_thu_bh = st.number_input("Truy thu BHYT 4.5%", value=285)
        tam_thu = st.number_input("Tạm thu tiền", value=0)
    with ct3:
        qt_thue_hoan = st.number_input("Quyết toán Thuế (+)", value=656)
        qt_thue_dong = st.number_input("Quyết toán Thuế (-)", value=0)
        nguoi_pt = st.number_input("Số người phụ thuộc", value=0, step=1)

    # --- LOGIC TÍNH TOÁN TỰ ĐỘNG ---
    tien_tc = (g_ngay * l_gio * 1.5) + (g_dem * l_gio * 2.1) + (g_cn * l_gio * 2.0)
    
    # 1. TỔNG LƯƠNG
    tong_luong = (l_bac + pc_tn + thuong_ns + pc_doc_hai + pc_xang + pc_dt + chuyen_can + pc_com + tn_ngoai_gio_thue) * 1000
    
    # 2. TỔNG THU NHẬP THÁNG
    tong_tn_thang = tong_luong + (tn_ngoai_gio_mien * 1000) + (phep_nam * 1000) + (thuong_13 * 1000) + tien_tc
    
    # 3. BẢO HIỂM & THUẾ
    bh_105 = (l_dong_bh * 1000) * 0.105
    tn_chiu_thue = tong_tn_thang - (pc_com * 1000) - (tn_ngoai_gio_mien * 1000)
    giam_tru = 11000000 + (nguoi_pt * 4400000)
    tn_tinh_thue = max(0, tn_chiu_thue - bh_105 - giam_tru)
    
    def tinh_thue(tntt):
        if tntt <= 5000000: return tntt * 0.05
        elif tntt <= 10000000: return tntt * 0.1 - 250000
        else: return tntt * 0.15 - 750000
    thue_tncn = tinh_thue(tn_tinh_thue)

    # 4. TỔNG THỰC NHẬN
    thuc_nhan = tong_tn_thang - bh_105 - (phi_cd * 1000) - thue_tncn - (truy_thu_bh * 1000) - (tam_thu * 1000) + (qt_thue_hoan * 1000) - (qt_thue_dong * 1000)

    # --- HIỂN THỊ KẾT QUẢ CUỐI CÙNG (NHẢY SỐ TỰ ĐỘNG) ---
    st.divider()
    st.markdown(f"### 🏆 TỔNG TIỀN THỰC NHẬN: <span style='color:red'>{fmt(thuc_nhan)} VNĐ</span>", unsafe_allow_html=True)
    
    with st.expander("🔍 Chi tiết các mục tổng (Đối soát công ty)"):
        data = {
            "Danh mục đối soát": ["TỔNG LƯƠNG", "TỔNG THU NHẬP THÁNG", "Khấu trừ Bảo hiểm (10.5%)", "Khấu trừ Thuế TNCN", "Khấu trừ Công đoàn", "Truy thu / Quyết toán", "THỰC NHẬN CUỐI CÙNG"],
            "Số tiền": [fmt(tong_luong), fmt(tong_tn_thap), fmt(-bh_105), fmt(-thue_tncn), fmt(-phi_cd*1000), fmt((qt_thue_hoan - truy_thu_bh - tam_thu - qt_thue_dong)*1000), f"⭐ {fmt(thuc_nhan)}"]
        }
        st.table(pd.DataFrame(data))

# Sidebar
st.sidebar.markdown("---")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

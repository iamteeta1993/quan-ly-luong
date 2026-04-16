import streamlit as st
import pandas as pd

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Hệ thống Lương STK 2026", layout="wide")

def fmt(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Cổng Thông Tin Lương STK")
    user = st.text_input("Tài khoản", value="admin")
    pw = st.text_input("Mật khẩu", type="password", value="123")
    if st.button("Đăng nhập hệ thống"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Bảng Tính Lương Tự Động Cập Nhật")
    st.info("💡 **Tính năng:** Mọi thay đổi bạn nhập ở trên sẽ hiển thị ngay ở kết quả phía dưới.")

    # --- KHU VỰC NHẬP LIỆU (KHÔNG DÙNG FORM ĐỂ TỰ ĐỘNG CẬP NHẬT) ---
    st.subheader("📌 1. Thông tin căn cứ & Lương chính")
    c1, c2, c3 = st.columns(3)
    with c1:
        ho_ten = st.text_input("Họ & Tên", value="CAO NGỌC THẮNG")
        l_tinh_tc = st.number_input("Lương tính tăng ca (x1000)", value=8780)
    with c2:
        ngay_vao = st.text_input("Ngày vào công ty", value="14/03/2025")
        l_dong_bh = st.number_input("Lương tham gia BHXH (x1000)", value=6500)
    with c3:
        so_cong = st.number_input("Số ngày làm thực tế", value=24)
        l_bac = st.number_input("Lương theo bậc (x1000)", value=6654)

    st.subheader("💰 2. Phụ cấp & Tăng ca")
    col1, col2, col3 = st.columns(3)
    with col1:
        pc_an = st.number_input("PC cơm giữa ca (x1000)", value=720)
        pc_xang = st.number_input("PC xăng xe/Đi lại (x1000)", value=500)
    with col2:
        h_tc_ngay = st.number_input("Giờ tăng ca NGÀY (h)", value=11.0, step=0.5)
        h_ca_dem = st.number_input("Giờ CA ĐÊM chính (h)", value=0.0, step=0.5)
    with col3:
        phi_cd = st.number_input("Phí công đoàn (x1000)", value=40)
        nguoi_pt = st.number_input("Số người phụ thuộc", value=0)

    # --- LOGIC TÍNH TOÁN (LUÔN CHẠY MỖI KHI DỮ LIỆU THAY ĐỔI) ---
    l_gio = (l_tinh_tc * 1000) / 208
    tien_tc_ngay = h_tc_ngay * l_gio * 1.5
    tien_ca_dem = h_ca_dem * l_gio * 0.3 
    tong_tc = tien_tc_ngay + tien_ca_dem
    
    # Tổng thu nhập tạm tính (Lương bậc + Cơm + Xăng + Tăng ca)
    thu_nhap_thang = (l_bac + pc_an + pc_xang) * 1000 + tong_tc
    bh_105 = (l_dong_bh * 1000) * 0.105
    
    # Thuế TNCN
    tn_chiu_thue = thu_nhap_thang - (pc_an * 1000)
    giam_tru = 11000000 + (nguoi_pt * 4400000)
    tn_tinh_thue = max(0, tn_chiu_thue - bh_105 - giam_tru)
    
    def tinh_thue(tntt):
        if tntt <= 5000000: return tntt * 0.05
        elif tntt <= 10000000: return tntt * 0.1 - 250000
        else: return tntt * 0.15 - 750000
    thue_tncn = tinh_thue(tn_tinh_thue)
    
    thuc_nhan = thu_nhap_thang - bh_105 - (phi_cd * 1000) - thue_tncn

    # --- HIỂN THỊ KẾT QUẢ (TỰ ĐỘNG THAY ĐỔI) ---
    st.divider()
    st.markdown(f"### 🏆 TỔNG TIỀN THỰC NHẬN: <span style='color:red'>{fmt(thuc_nhan)} VNĐ</span>", unsafe_allow_html=True)
    
    st.subheader("📋 Chi tiết phiếu lương đối soát")
    data_hien_thi = {
        "Hạng mục giải thích": [
            "1. Lương chính & Phụ cấp", 
            "2. Tiền làm thêm giờ (Tăng ca/Ca đêm)", 
            "3. Bảo hiểm trích trừ lương (10.5%)", 
            "4. Thuế TNCN tạm tính", 
            "5. Các khoản phí khác (Công đoàn...)",
            "TỔNG CỘNG THỰC NHẬN"
        ],
        "Số tiền (VNĐ)": [
            fmt((l_bac + pc_an + pc_xang) * 1000),
            fmt(tong_tc),
            fmt(-bh_105),
            fmt(-thue_tncn),
            fmt(-phi_cd * 1000),
            f"⭐ {fmt(thuc_nhan)}"
        ]
    }
    st.table(pd.DataFrame(data_hien_thi))

# Sidebar
st.sidebar.markdown("---")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

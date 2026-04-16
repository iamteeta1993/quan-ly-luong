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
    st.title("🔐 Cổng Thông Tin Lương Nhân Viên STK")
    user = st.text_input("Tài khoản", value="admin")
    pw = st.text_input("Mật khẩu", type="password", value="123")
    if st.button("Đăng nhập hệ thống"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Sai thông tin!")
else:
    st.title("📊 Bảng Tính Lương & Giải Thích Luật 2026")
    st.info("💡 **Hướng dẫn:** Nhấp vào biểu tượng (i) cạnh mỗi mục để xem giải thích luật.")

    with st.form("full_stk_form_v3"):
        # --- NHÓM 1: THÔNG TIN CĂN CỨ ---
        st.subheader("📌 1. Thông tin căn cứ tính lương")
        c1, c2, c3 = st.columns(3)
        with c1:
            ho_ten = st.text_input("Họ & Tên", value="CAO NGỌC THẮNG")
            l_tinh_tc = st.number_input("Lương tính tăng ca (x1000)", value=8780, help="Là số tiền dùng để chia ra tiền lương theo giờ. Thường bằng lương cơ bản + phụ cấp cố định.")
        with c2:
            ngay_vao = st.text_input("Ngày vào công ty", value="14/03/2025")
            l_dong_bh = st.number_input("Lương tham gia BHXH (x1000)", value=6500, help="Mức lương dùng làm căn cứ đóng BHXH, BHYT, BHTN theo quy định Luật Bảo hiểm 2026.")
        with c3:
            so_cong = st.number_input("Số ngày làm thực tế", value=24, help="Số ngày bạn đi làm thực tế trong tháng để tính lương thời gian.")
            tn_chuan = st.number_input("Thu nhập chuẩn/tháng (x1000)", value=12000)

        st.divider()

        # --- NHÓM 2: THU NHẬP CHI TIẾT ---
        st.subheader("💰 2. Các khoản thu nhập & Phụ cấp")
        col1, col2 = st.columns(2)
        with col1:
            l_bac = st.number_input("Lương theo bậc (x1000)", value=6654, help="Lương chính theo thang bảng lương của doanh nghiệp.")
            pc_tn = st.number_input("PC trách nhiệm (x1000)", value=569, help="Phụ cấp dành cho vị trí quản lý hoặc đặc thù công việc.")
            thuong_ns = st.number_input("Thưởng năng suất (x1000)", value=3902, help="Thưởng dựa trên kết quả kiểm soát năng suất sản phẩm.")
            pc_doc_hai = st.number_input("PC độc hại/Nuôi con (x1000)", value=500, help="Khoản bù đắp môi trường làm việc hoặc hỗ trợ đời sống.")
        with col2:
            pc_an = st.number_input("PC cơm giữa ca (x1000)", value=720, help="Khoản tiền cơm được miễn thuế TNCN tối đa 730k/tháng.")
            pc_xang = st.number_input("PC xăng xe/Đi lại (x1000)", value=500, help="Hỗ trợ chi phí di chuyển từ nhà đến nơi làm việc.")
            chuyen_can = st.number_input("Thưởng chuyên cần (x1000)", value=500, help="Thưởng nếu không vi phạm nội quy đi trễ, về sớm.")
            ngoai_gio_mien = st.number_input("Ngoài giờ MIỄN THUẾ (x1000)", value=840, help="Phần tiền làm thêm giờ vượt mức 100% lương chính sẽ được miễn thuế TNCN.")

        st.divider()

        # --- NHÓM 3: TĂNG CA & LÀM ĐÊM ---
        st.subheader("🌙 3. Chế độ làm đêm & Tăng ca")
        st.warning("⚠️ Theo Luật: Làm ca đêm được cộng thêm ít nhất 30% lương (Hệ số x1.3)")
        g1, g2, g3 = st.columns(3)
        l_gio = (l_tinh_tc * 1000) / 208 # 208 giờ = 26 công x 8h
        with g1:
            h_tc_ngay = st.number_input("Giờ tăng ca NGÀY (h)", value=11.0, help="Tính 150% lương giờ bình thường.")
        with g2:
            h_ca_dem = st.number_input("Giờ CA ĐÊM chính (h)", value=0.0, help="Làm việc từ 22h - 6h sáng. Phụ cấp ít nhất 30% (Hệ số x1.3).")
        with g3:
            h_tc_dem = st.number_input("Giờ TĂNG CA ĐÊM (h)", value=0.0, help="Tăng ca vào khung giờ đêm. Hệ số tính là 210% (150% + 30% + 20% x 150%).")

        st.divider()

        # --- NHÓM 4: KHẤU TRỪ & THUẾ ---
        st.subheader("📉 4. Các khoản trích trừ & Thuế")
        k1, k2, k3 = st.columns(3)
        with k1:
            phi_cd = st.number_input("Phí công đoàn (x1000)", value=40, help="Trích 1% tiền lương cơ bản để duy trì hoạt động công đoàn.")
            nguoi_pt = st.number_input("Số người phụ thuộc", value=0, help="Mỗi người phụ thuộc được giảm trừ 4.4 triệu đồng/tháng khi tính thuế TNCN.")
        with k2:
            truy_thu = st.number_input("Truy thu BHYT 4.5% (x1000)", value=286, help="Khấu trừ bù cho các kỳ thiếu hụt bảo hiểm y tế.")
            qt_thue_hoan = st.number_input("Quyết toán Thuế (+) Hoàn (x1000)", value=656, help="Tiền thuế nộp thừa trong năm được Nhà nước trả lại.")
        with k3:
            st.write("**Thuế TNCN (Luật 2026):**")
            st.caption("Giảm trừ gia cảnh bản thân: 11 triệu đồng/tháng.")
            st.caption("Mức thuế lũy tiến bắt đầu từ 5% sau khi trừ gia cảnh.")

        submit = st.form_submit_button("TÍNH LƯƠNG THỰC NHẬN")

        if submit:
            # --- LOGIC TÍNH TOÁN ---
            tien_tc_ngay = h_tc_ngay * l_gio * 1.5
            tien_ca_dem = h_ca_dem * l_gio * 0.3 # Chỉ tính phần phụ cộng thêm 30%
            tien_tc_dem = h_tc_dem * l_gio * 2.1
            tong_tc = tien_tc_ngay + tien_ca_dem + tien_tc_dem
            
            thu_nhap_thang = (l_bac + pc_tn + thuong_ns + pc_doc_hai + pc_xang + pc_an + chuyen_can + ngoai_gio_mien) * 1000 + tong_tc
            
            # Bảo hiểm 10.5% (Luật 2026)
            bh_105 = (l_dong_bh * 1000) * 0.105
            
            # Thuế TNCN
            tn_chiu_thue = thu_nhap_thang - (pc_an * 1000) - ngoai_gio_mien * 1000
            giam_tru = 11000000 + (nguoi_pt * 4400000)
            tn_tinh_thue = max(0, tn_chiu_thue - bh_105 - giam_tru)
            
            def tinh_thue(tntt):
                if tntt <= 5000000: return tntt * 0.05
                elif tntt <= 10000000: return tntt * 0.1 - 250000
                else: return tntt * 0.15 - 750000
            thue_tncn = tinh_thue(tn_tinh_thue)
            
            thuc_nhan = thu_nhap_thang - bh_105 - (phi_cd * 1000) - thue_tncn - (truy_thu * 1000) + (qt_thue_hoan * 1000)

            # --- KẾT QUẢ ---
            st.success(f"### 🏆 TỔNG TIỀN THỰC NHẬN: {fmt(thuc_nhan)} VNĐ")
            
            with st.expander("👉 Xem chi tiết phiếu lương (Dành cho công nhân)"):
                data = {
                    "Mục": ["Tổng thu nhập", "Tiền tăng ca/ca đêm", "Trích đóng BH (10.5%)", "Phí công đoàn", "Thuế TNCN nộp", "Truy thu/Hoàn thuế", "THỰC NHẬN"],
                    "Số tiền": [fmt(thu_nhap_thang - tong_tc), fmt(tong_tc), fmt(-bh_105), fmt(-phi_cd*1000), fmt(-thue_tncn), fmt((qt_thue_hoan - truy_thu)*1000), f"⭐ {fmt(thuc_nhan)}"]
                }
                st.table(pd.DataFrame(data))

# Sidebar
st.sidebar.markdown("---")
st.sidebar.info("Hệ thống STK v2.1 - Giải nghĩa Luật 2026")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

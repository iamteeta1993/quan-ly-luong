import streamlit as st
import pandas as pd

# 1. CẤU HÌNH GIAO DIỆN DI ĐỘNG
st.set_page_config(page_title="Hệ thống Lương STK", layout="wide")

# Hàm định dạng số có dấu phẩy phân cách hàng nghìn
def format_with_commas(val):
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return val

# 2. KIỂM TRA ĐĂNG NHẬP
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập Quản trị viên")
    user = st.text_input("Tài khoản (Username)")
    pw = st.text_input("Mật khẩu (Password)", type="password")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")
else:
    # 3. GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP
    st.title("📊 Phiếu Lương Công Ty STK")
    
    # Nút tải file Excel
    uploaded_file = st.file_uploader("Tải lên file Excel lương (định dạng .xlsx)", type=["xlsx"])

    if uploaded_file:
        # Đọc danh sách tất cả các Sheets/Tables trong file
        excel_data = pd.ExcelFile(uploaded_file)
        sheet_names = excel_data.sheet_names
        
        st.sidebar.success(f"Tìm thấy {len(sheet_names)} bảng dữ liệu")
        selected_sheet = st.sidebar.selectbox("Chọn Table cần xem:", sheet_names)

        # Đọc dữ liệu từ Sheet đã chọn
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        # LÀM SẠCH DỮ LIỆU: Xóa dòng trống và thay None bằng khoảng trắng
        df = df.dropna(how='all')
        df = df.fillna("")

        # ĐỊNH DẠNG DẤU PHẨY CHO SỐ TIỀN
        # Quét qua từng ô, nếu là số thì định dạng dấu phẩy
        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(format_with_commas)

        # HIỂN THỊ BẢNG LƯƠNG TỔNG QUÁT
        st.subheader(f"📋 Dữ liệu: {selected_sheet}")
        st.dataframe(df_formatted, use_container_width=True)

        # TÍNH NĂNG XEM CHI TIẾT (PHIẾU LƯƠNG CÁ NHÂN)
        st.markdown("---")
        st.subheader("🔍 Xem chi tiết phiếu lương")
        
        # Tìm cột Họ Tên (Giả sử nằm ở cột thứ 2)
        # Nếu file của bạn có tên cột cụ thể là 'Họ & Tên', hãy thay vào đây
        list_nv = df.iloc[:, 1].unique() if len(df.columns) > 1 else []
        
        if len(list_nv) > 0:
            ten_selected = st.selectbox("Chọn nhân viên để xem phiếu riêng:", list_nv)
            
            if ten_selected:
                # Lọc dữ liệu nhân viên đó và xoay dọc bảng (Transpose) để dễ nhìn trên điện thoại
                person_data = df[df.iloc[:, 1] == ten_selected].T
                person_data.columns = ["Thông tin chi tiết"]
                
                # Định dạng dấu phẩy cho bảng chi tiết này
                person_data["Thông tin chi tiết"] = person_data["Thông tin chi tiết"].apply(format_with_commas)
                
                st.table(person_data)

# 4. THANH BÊN (SIDEBAR)
st.sidebar.markdown("---")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()
st.sidebar.info("Hệ thống quản lý nội bộ STK v1.2")

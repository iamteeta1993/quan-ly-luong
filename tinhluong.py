import streamlit as st
import pandas as pd

# Cấu hình giao diện di động
st.set_page_config(page_title="Quản Lý Lương STK", layout="centered")

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
    st.title("📊 Phiếu Lương Công Ty STK")
    
    uploaded_file = st.file_uploader("Chọn file Excel lương", type=["xlsx"])

    if uploaded_file:
        # Đọc toàn bộ các Sheet (Table) trong file
        excel_data = pd.ExcelFile(uploaded_file)
        sheet_names = excel_data.sheet_names # Lấy danh sách Table 1, Table 2...
        
        st.success(f"✅ Đã tìm thấy {len(sheet_names)} bảng dữ liệu.")

        # Cho phép chọn Table muốn xem (Phù hợp giao diện điện thoại)
        selected_sheet = st.selectbox("Chọn bảng cần xem (Table):", sheet_names)

        # Đọc dữ liệu của Sheet được chọn
        # skiprows=2 để bỏ qua dòng tiêu đề "Công ty..." và "Phiếu lương..." nếu bạn muốn bảng sạch hơn
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        st.subheader(f"📋 Dữ liệu: {selected_sheet}")
        
        # Hiển thị bảng lương
        st.dataframe(df, use_container_width=True)

        # Tính năng tìm kiếm nhanh theo tên NV trên điện thoại
        search_name = st.text_input("🔍 Tìm tên nhân viên nhanh:")
        if search_name:
            # Giả sử cột họ tên là cột đầu tiên hoặc cột 'A'
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_name, case=False)).any(axis=1)]
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)

st.sidebar.markdown("---")
st.sidebar.write("CÔNG TY TNHH STK")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

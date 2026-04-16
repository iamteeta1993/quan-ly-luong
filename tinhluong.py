import streamlit as st
import pandas as pd

# Cấu hình trang cho di động
st.set_page_config(page_title="Quản Lý Lương", layout="centered")

# --- ĐĂNG NHẬP ---
if "authenticated" not in st.session_state:
    st.title("🔐 Đăng nhập hệ thống")
    user = st.text_input("Tài khoản")
    pw = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if user == "admin" and pw == "123":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")
else:
    st.title("📊 Quản Lý Bảng Lương")
    
    # Tạo menu 2 tab
    tab1, tab2 = st.tabs(["📁 Tải Excel lên", "📋 Xem Bảng Lương"])

    with tab1:
        st.subheader("Bước 1: Đưa dữ liệu từ Excel vào App")
        uploaded_file = st.file_uploader("Chọn file Excel của bạn", type=["xlsx", "xls", "csv"])
        
        if uploaded_file is not None:
            # Đọc dữ liệu từ file bạn tải lên
            try:
                df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(('.xlsx', '.xls')) else pd.read_csv(uploaded_file)
                st.session_state["data_luong"] = df
                st.success("✅ Đã tải dữ liệu thành công!")
                st.write("Xem trước 5 dòng đầu tiên:")
                st.dataframe(df.head())
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    with tab2:
        st.subheader("Bước 2: Kiểm tra dữ liệu trên App")
        if "data_luong" in st.session_state:
            df_display = st.session_state["data_luong"]
            
            # Tính tổng số tiền thực nhận để kiểm tra app có tính đúng không
            if 'Thực nhận' in df_display.columns:
                tong_chi = df_display['Thực nhận'].sum()
                st.metric("Tổng quỹ lương thực nhận", f"{tong_chi:,.0f} VNĐ")
            
            # Hiển thị bảng lương đầy đủ
            st.dataframe(df_display, use_container_width=True)
            
            # Nút xóa để thử lại
            if st.button("Xóa dữ liệu để tải lại file khác"):
                del st.session_state["data_luong"]
                st.rerun()
        else:
            st.info("Chưa có dữ liệu. Vui lòng sang Tab 'Tải Excel lên' để thử.")

# --- SIDEBAR ---
st.sidebar.write("Hệ thống v1.1 - Hoạt động tốt trên Mobile")
if st.sidebar.button("Đăng xuất"):
    del st.session_state["authenticated"]
    st.rerun()

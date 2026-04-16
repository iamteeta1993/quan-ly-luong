import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. KHỞI TẠO CƠ SỞ DỮ LIỆU (Lưu trữ file tại máy) ---
conn = sqlite3.connect('database_luong.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bang_luong 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, ma_nv TEXT, ho_ten TEXT, phong_ban TEXT, 
              thang_nam TEXT, luong_bac REAL, pc_trach_nhiem REAL, luong_bh REAL, 
              pc_xang REAL, pc_dt REAL, thuong_13 REAL, ngoai_gio_thue REAL, 
              ngoai_gio_ko_thue REAL, bh_tru REAL, thue_tncn REAL, tam_ung REAL, 
              truy_thu REAL, tong_nhan REAL)''')
conn.commit()

# --- 2. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="Quản Lý Lương Admin", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.subheader("🔑 Đăng nhập quyền Admin")
        user = st.text_input("Tài khoản")
        pw = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if user == "admin" and pw == "123": # Bạn có thể đổi mật khẩu ở đây
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu")
        return False
    return True

if check_password():
    st.sidebar.title("Menu Quản Lý")
    menu = ["Thêm Bảng Lương", "Xem Danh Sách Lưu Trữ"]
    choice = st.sidebar.selectbox("Chọn tính năng", menu)

    # --- 3. TÍNH NĂNG THÊM MỚI ---
    if choice == "Thêm Bảng Lương":
        st.header("📝 Nhập Dữ Liệu Lương Nhân Viên")
        
        with st.form("form_luong"):
            c1, c2 = st.columns(2)
            with c1:
                st.info("📌 Thông tin cơ bản")
                ma_nv = st.text_input("Mã NV")
                ho_ten = st.text_input("Họ tên")
                phong = st.text_input("Phòng ban")
                thang = st.date_input("Lương tháng/năm")
                
                st.success("💰 Thu nhập (Có thuế)")
                l_bac = st.number_input("Lương bậc", value=0.0)
                pc_tn = st.number_input("Phụ cấp trách nhiệm", value=0.0)
                l_bh = st.number_input("Lương đóng BH", value=0.0)
                ngoai_thue = st.number_input("Ngoài giờ (Có thuế)", value=0.0)
            
            with c2:
                st.warning("🎁 Thu nhập (Không thuế)")
                pc_xang = st.number_input("Phụ cấp xăng xe", value=0.0)
                pc_dt = st.number_input("Phụ cấp điện thoại", value=0.0)
                ngoai_ko_thue = st.number_input("Ngoài giờ (Không thuế)", value=0.0)
                thuong = st.number_input("Thưởng tháng 13", value=0.0)
                
                st.error("📉 Các khoản giảm trừ")
                bh = st.number_input("Trích đóng BH (10.5%)", value=0.0)
                thue = st.number_input("Thuế TNCN", value=0.0)
                ung = st.number_input("Tạm ứng", value=0.0)
                truy = st.number_input("Truy thu BHYT 4.5%", value=0.0)

            if st.form_submit_button("Lưu vào hệ thống"):
                # Công thức tính tổng nhận (Dựa theo logic Excel của bạn)
                tong = (l_bac + pc_tn + ngoai_thue + pc_xang + pc_dt + ngoai_ko_thue + thuong) - (bh + thue + ung + truy)
                
                c.execute('''INSERT INTO bang_luong (ma_nv, ho_ten, phong_ban, thang_nam, luong_bac, 
                             pc_trach_nhiem, luong_bh, pc_xang, pc_dt, thuong_13, ngoai_gio_thue, 
                             ngoai_gio_ko_thue, bh_tru, thue_tncn, tam_ung, truy_thu, tong_nhan) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', 
                          (ma_nv, ho_ten, phong, thang.strftime("%m/%Y"), l_bac, pc_tn, l_bh, 
                           pc_xang, pc_dt, thuong, ngoai_thue, ngoai_ko_thue, bh, thue, ung, truy, tong))
                conn.commit()
                st.success(f"Đã lưu! Tổng thực nhận của {ho_ten}: {tong:,.0f} VNĐ")

    # --- 4. TÍNH NĂNG XEM DỮ LIỆU ---
    elif choice == "Xem Danh Sách Lưu Trữ":
        st.header("📊 Lịch Sử Bảng Lương")
        df = pd.read_sql("SELECT * FROM bang_luong", conn)
        st.dataframe(df)
        
        # Cho phép tải về file Excel
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Tải file Excel (.csv)", csv, "bang_luong.csv", "text/csv")

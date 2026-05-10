import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

st.set_page_config(page_title="🆔 Veloreg", layout="wide")

# 🔐 ПРОСТАЯ АВТОРИЗАЦИЯ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.name = None

if not st.session_state.logged_in:
    st.markdown("## 🔐 Добро пожаловать в Veloreg CRM")
    col1, col2 = st.columns([1,2])
    with col1:
        username = st.text_input("Логин", placeholder="admin")
    with col2:
        password = st.text_input("Пароль", type="password", placeholder="******")
    
    if st.button("🚀 Войти"):
        if username == "admin" and password == "Veloreg2026!":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.session_state.name = "Главный администратор"
            st.rerun()
        elif username == "manager" and password == "Manager123!":
            st.session_state.logged_in = True
            st.session_state.role = "manager"
            st.session_state.name = "Менеджер"
            st.rerun()
        else:
            st.error("❌ Неверный логин/пароль")
    st.stop()

# ✅ ОСНОВНОЙ ИНТЕРФЕЙС
st.sidebar.success(f"👋 {st.session_state.name}")
st.sidebar.info(f"🎭 Роль: **{st.session_state.role.upper()}**")
if st.sidebar.button("🚪 Выход"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.title("🆔 **Veloreg CRM**")

@st.cache_resource
def get_db():
    db_path = 'veloreg.db'
    if not os.path.exists(db_path) and os.path.exists('VELY.-Uchet.xlsx'):
        conn_temp = sqlite3.connect(db_path)
        xl = pd.ExcelFile('VELY.-Uchet.xlsx')
        for sheet in xl.sheet_names:
            df = pd.read_excel('VELY.-Uchet.xlsx', sheet_name=sheet)
            df.to_sql(sheet.lower().replace(' ', '_'), conn_temp, if_exists='replace', index=False)
        conn_temp.close()
        st.success("✅ Данные загружены!")
    return sqlite3.connect(db_path)

conn = get_db()

page = st.sidebar.selectbox("📂 Разделы", ["📊 Дашборд", "🚲 Байки", "👥 Арендаторы", "⚡ Выдача"])

if page == "📊 Дашборд":
    col1, col2, col3, col4 = st.columns(4)
    df_b = pd.read_sql("SELECT * FROM реестр_байков", conn)
    if len(df_b) > 0:
        cols = df_b.columns[df_b.columns.str.contains('Статус', case=False, na=False)]
        if len(cols) > 0:
            status = df_b[cols[0]].value_counts()
            with col1: st.metric("🔴 В аренде", status.get('В аренде', 0))
            with col2: st.metric("🟢 Готово", status.get('Готов к выдаче', 0))
            with col3: st.metric("🟡 Сервис", status.get('В сервисе', 0))
            with col4: st.metric("📦 Всего", len(df_b))
    
    fig = px.pie([10,20,30], names=['В аренде', 'Готово', 'Сервис'])
    st.plotly_chart(fig)

elif page == "⚡ Выдача":
    st.header("🚀 Выдача байка")
    with st.form("issue"):
        col1, col2 = st.columns(2)
        with col1:
            fio = st.text_input("👤 ФИО")
            bike_num = st.number_input("🚲 № байка", 1000, 1100, 1001)
        with col2:
            phone = st.text_input("📱 Телефон")
            kanal = st.selectbox("📢 Канал", ["Специалист", "Авито"])
        
        if st.form_submit_button("✅ Выдать байк"):
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE реестр_байков SET Статус='В аренде' WHERE номер_байка=?", (bike_num,))
                cursor.execute("INSERT OR IGNORE INTO арендаторы (ФИО, номер_байка, номер_телефона) VALUES (?, ?, ?)", 
                              (fio, bike_num, phone or ""))
                conn.commit()
                st.success(f"✅ Байк {bike_num} выдан {fio}!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ {e}")

elif page == "🚲 Байки":
    df = pd.read_sql("SELECT * FROM реестр_байков", conn)
    st.dataframe(df.head(20))

elif page == "👥 Арендаторы":
    df = pd.read_sql("SELECT * FROM арендаторы", conn)
    st.dataframe(df.head(20))

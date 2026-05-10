import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

st.set_page_config(page_title="🆔 Veloreg", layout="wide")

# 🔐 ПРОСТАЯ АВТОРИЗАЦИЯ (без внешних библиотек!)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def login():
    """Простая форма логина"""
    st.markdown("## 🔐 Вход в Veloreg CRM")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("👤 Логин", placeholder="admin")
    with col2:
        password = st.text_input("🔑 Пароль", type="password", placeholder="*****")
    
    if st.button("🚀 Войти", use_container_width=True):
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
            st.error("❌ Неверный логин или пароль!")
    
    st.info("**admin / Veloreg2026!**\n**manager / Manager123!**")

if not st.session_state.logged_in:
    login()
    st.stop()

# ✅ АВТОРИЗОВАННЫЙ БЛОК
st.sidebar.success(f"👋 **{st.session_state.name}**")
st.sidebar.info(f"🎭 **{st.session_state.role.upper()}**")

if st.sidebar.button("🚪 Выход"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

st.title("🆔 **Veloreg CRM**")

@st.cache_resource
def get_db():
    db_path = 'veloreg.db'
    if not os.path.exists(db_path) and os.path.exists('VELY.-Uchet.xlsx'):
        st.info("📥 Импорт данных...")
        conn_temp = sqlite3.connect(db_path)
        xl = pd.ExcelFile('VELY.-Uchet.xlsx')
        for sheet in xl.sheet_names:
            df = pd.read_excel('VELY.-Uchet.xlsx', sheet_name=sheet)
            df.to_sql(sheet.lower().replace(' ', '_'), conn_temp, if_exists='replace')
        conn_temp.close()
    return sqlite3.connect(db_path)

conn = get_db()

# Навигация
page = st.sidebar.selectbox("📂 Разделы", ["📊 Дашборд", "🚲 Байки", "👥 Арендаторы", "⚡ Выдача", "📋 Акты"])

if page == "📊 Дашборд":
    col1, col2, col3, col4 = st.columns(4)
    df_b = pd.read_sql("SELECT * FROM реестр_байков", conn)
    if len(df_b.columns) > 0:
        status_col = df_b.columns[df_b.columns.str.contains('Статус', case=False)]
        if len(status_col) > 0:
            status = df_b[status_col[0]].value_counts()
            with col1: st.metric("🔴 В аренде", status.get('В аренде', 0))
            with col2: st.metric("🟢 Готово", status.get('Готов к выдаче', 0))
            with col3: st.metric("🟡 Сервис", status.get('В сервисе', 0))
            with col4: st.metric("📦 Всего", len(df_b))
    
    fig = px.pie(values=[1,1,1], names=['Загрузка', 'Готово', 'Сервис'])
    st.plotly_chart(fig)

elif page == "⚡ Выдача":
    st.header("🚀 Быстрая выдача байка")
    with st.form("issue_bike"):
        col1, col2 = st.columns(2)
        with col1:
            fio = st.text_input("👤 ФИО *")
            bike_num = st.number_input("🚲 № байка *", 1000, 1100, 1001)
        with col2:
            phone = st.text_input("📱 Телефон")
            kanal = st.selectbox("📢 Канал", ["Специалист", "Авито", "Рекомендация"])
        
        if st.form_submit_button("✅ Выдать байк!", use_container_width=True):
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE реестр_байков 

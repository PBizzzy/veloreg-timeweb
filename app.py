import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import tempfile

st.set_page_config(page_title="🆔 Veloreg", layout="wide")

# 🔐 АВТОРИЗАЦИЯ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.name = None

if not st.session_state.logged_in:
    st.markdown("### 🔐 Veloreg CRM — Вход")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Логин", placeholder="admin")
    with col2:
        password = st.text_input("Пароль", type="password")
    
    if st.button("🚀 Войти", use_container_width=True):
        if username == "admin" and password == "Veloreg2026!":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.session_state.name = "Администратор"
            st.rerun()
        elif username == "manager" and password == "Manager123!":
            st.session_state.logged_in = True
            st.session_state.role = "manager" 
            st.session_state.name = "Менеджер"
            st.rerun()
        else:
            st.error("❌ Неверный логин/пароль")
    st.stop()

# ✅ ИНТЕРФЕЙС
st.sidebar.success(f"👋 {st.session_state.name}")
st.sidebar.info(f"🎭 Роль: **{st.session_state.role.upper()}**")
if st.sidebar.button("🚪 Выход"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

st.title("🆔 **Veloreg CRM**")

# 🔄 НОВЫЙ подход к БД — без кэша соединения!
def load_table(table_name):
    """Загружает таблицу без проблем с потоками"""
    try:
        with sqlite3.connect('veloreg.db', timeout=10) as conn:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        return df
    except:
        return pd.DataFrame()

def execute_sql(sql, params=()):
    """Безопасное выполнение SQL"""
    try:
        with sqlite3.connect('veloreg.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
        return True
    except Exception as e:
        st.error(f"❌ БД ошибка: {e}")
        return False

# Инициализация БД
if not os.path.exists('veloreg.db') and os.path.exists('VELY.-Uchet.xlsx'):
    st.info("📥 Первая загрузка данных...")
    with sqlite3.connect('veloreg.db') as conn:
        xl = pd.ExcelFile('VELY.-Uchet.xlsx')
        for sheet in xl.sheet_names:
            df = pd.read_excel('VELY.-Uchet.xlsx', sheet_name=sheet)
            df.to_sql(sheet.lower().replace(' ', '_'), conn, if_exists='replace')
    st.success("✅ Данные загружены!")

page = st.sidebar.selectbox("📂 Разделы", ["📊 Дашборд", "🚲 Байки", "👥 Арендаторы", "📋 Акты", "⚡ Выдача"])

if page == "📊 Дашборд":
    col1, col2, col3, col4 = st.columns(4)
    
    df_baiki = load_table('реестр_байков')
    df_arend = load_table('арендаторы')
    
    with col1: st.metric("👥 Арендаторов", len(df_arend))
    with col2: st.metric("🚲 Байков", len(df_baiki))
    with col3: st.metric("📋 Актов", 326)  # Пока статично
    with col4: st.metric("🟢 Статус", "🟢 OK")
    
    if len(df_baiki) > 0:
        cols = [c for c in df_baiki.columns if 'Статус' in str(c).upper()]
        if cols:
            status = df_baiki[cols[0]].value_counts()
            fig = px.pie(status.values, status.index, hole=0.3)
            st.plotly_chart(fig)

elif page == "🚲 Байки":
    df = load_table('реестр_байков')
    st.dataframe(df.head(20), use_container_width=True)

elif page == "👥 Арендаторы":
    df = load_table('арендаторы')
    search = st.text_input("🔍 Поиск:")
    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]
    st.dataframe(df.head(20))

elif page == "📋 Акты":
    df = load_table('реестр_актов')
    st.dataframe(df.tail(20))

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
        
        if st.form_submit_button("✅ Выдать!", use_container_width=True):
            success = execute_sql(
                "UPDATE реестр_байков SET Статус='В аренде' WHERE номер_байка=?",
                (bike_num,)
            )
            if success:
                execute_sql(
                    "INSERT OR IGNORE INTO арендаторы (ФИО, номер_байка, номер_телефона) VALUES (?, ?, ?)",
                    (fio, bike_num, phone)
                )
                st.success(f"🎉 Байк **{bike_num}** выдан **{fio}**!")
                st.balloons()
            st.rerun()

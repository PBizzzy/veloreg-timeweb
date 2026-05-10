import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

st.set_page_config(page_title="🆔 Veloreg", layout="wide")
st.title("🆔 **Veloreg CRM** на Timeweb")

# ✅ ИСПРАВЛЕННАЯ инициализация БД
@st.cache_resource  # ← cache_resource вместо cache_data!
def get_connection():
    """Создает подключение к БД"""
    db_path = 'veloreg.db'
    
    # Импорт данных при первом запуске
    if not os.path.exists(db_path) and os.path.exists('VELY.-Uchet.xlsx'):
        st.info("📥 Импортируем данные...")
        conn_temp = sqlite3.connect(db_path)
        xl = pd.ExcelFile('VELY.-Uchet.xlsx')
        for sheet in xl.sheet_names:
            df = pd.read_excel('VELY.-Uchet.xlsx', sheet_name=sheet)
            df.to_sql(sheet.lower().replace(' ', '_'), conn_temp, if_exists='replace', index=False)
        conn_temp.close()
        st.success("✅ База данных готова!")
    
    return sqlite3.connect(db_path)

# Подключение
@st.cache_resource
def get_db():
    return get_connection()

conn = get_db()

# Sidebar навигация
st.sidebar.title("📂 Навигация")
page = st.sidebar.selectbox("", ["📊 Дашборд", "🚲 Байки", "👥 Арендаторы", "📋 Акты", "⚡ Выдача"])

if page == "📊 Дашборд":
    col1, col2, col3, col4 = st.columns(4)
    
    # Статистика
    try:
        df_baiki = pd.read_sql("SELECT * FROM реестр_байков", conn)
        status_col = df_baiki.columns[df_baiki.columns.str.contains('Статус', case=False)].tolist()
        if status_col:
            status = df_baiki[status_col[0]].value_counts()
            with col1: st.metric("🔴 В аренде", status.get('В аренде', 0))
            with col2: st.metric("🟢 Готово", status.get('Готов к выдаче', 0))
            with col3: st.metric("🟡 Сервис", status.get('В сервисе', 0))
            with col4: st.metric("📦 Всего", len(df_baiki))
        
        # График
        fig = px.pie(values=status.values, names=status.index, hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("📊 Данные загружаются...")

elif page == "🚲 Байки":
    df = pd.read_sql("SELECT * FROM реестр_байков LIMIT 50", conn)
    st.dataframe(df)

elif page == "👥 Арендаторы":
    df = pd.read_sql("SELECT * FROM арендаторы LIMIT 50", conn)
    st.dataframe(df)

elif page == "📋 Акты":
    df = pd.read_sql("SELECT * FROM реестр_актов ORDER BY id DESC LIMIT 50", conn)
    st.dataframe(df)

elif page == "⚡ Выдача":
    st.header("🚀 Быстрая выдача байка")
    
    with st.form("issue_form"):
        col1, col2 = st.columns(2)
        with col1:
            fio = st.text_input("👤 ФИО *")
            bike_num = st.number_input("🚲 № байка *", 1000, 1100, 1001)
        with col2:
            phone = st.text_input("📱 Телефон")
            kanal = st.selectbox("📢 Канал привлечения", ["Специалист", "Авито", "Рекомендация"])
        
        submitted = st.form_submit_button("✅ Выдать байк!", use_container_width=True)
        
        if submitted and fio and bike_num:
            try:
                cursor = conn.cursor()
                # Обновляем байк
                cursor.execute("UPDATE реестр_байков SET Статус='В аренде' WHERE номер_байка=?", (bike_num,))
                # Добавляем арендатора
                cursor.execute("INSERT INTO арендаторы (ФИО, номер_байка, номер_телефона) VALUES (?, ?, ?)", 
                              (fio, bike_num, phone))
                conn.commit()
                st.success(f"🎉 **Байк {bike_num} выдан {fio}!**")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")

st.sidebar.markdown("---")
st.sidebar.info("**🆔 Veloreg CRM v2.0**")

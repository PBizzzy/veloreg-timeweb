import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

st.set_page_config(page_title="🆔 Veloreg", layout="wide")
st.title("🆔 **Veloreg** на Timeweb")

@st.cache_data
def init_db():
    db_path = 'veloreg.db'
    if not os.path.exists(db_path) and os.path.exists('VELY.-Uchet.xlsx'):
        conn = sqlite3.connect(db_path)
        xl = pd.ExcelFile('VELY.-Uchet.xlsx')
        for sheet in xl.sheet_names:
            df = pd.read_excel('VELY.-Uchet.xlsx', sheet_name=sheet)
            df.to_sql(sheet.lower().replace(' ', '_'), conn, if_exists='replace', index=False)
        conn.close()
        st.success("✅ База создана!")
    return sqlite3.connect(db_path)

conn = init_db()

page = st.sidebar.selectbox("📂 Навигация", ["📊 Дашборд", "🚲 Байки", "👥 Арендаторы", "📈 Аналитика"])

if page == "📊 Дашборд":
    col1, col2, col3 = st.columns(3)
    df_b = pd.read_sql("SELECT * FROM реестр_байков", conn)
    if len(df_b) > 0:
        status = df_b.iloc[:, -1].value_counts()
        with col1: st.metric("🔴 В аренде", status.get('В аренде', 0))
        with col2: st.metric("🟢 Готово", status.get('Готов к выдаче', 0))
        with col3: st.metric("🟡 Сервис", status.get('В сервисе', 0))
    
    fig = px.pie(status, names=status.index) if len(status) > 0 else px.pie()
    st.plotly_chart(fig)

elif page == "🚲 Байки":
    df = pd.read_sql("SELECT * FROM реестр_байков", conn)
    st.dataframe(df)

elif page == "👥 Арендаторы":
    df = pd.read_sql("SELECT * FROM арендаторы", conn)
    st.dataframe(df)

elif page == "📈 Аналитика":
    df_a = pd.read_sql("SELECT * FROM реестр_актов", conn)
    st.dataframe(df_a.tail(20))
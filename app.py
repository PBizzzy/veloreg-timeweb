import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px
import sqlite3
import os
import yaml
from datetime import timedelta

st.set_page_config(page_title="🆔 Veloreg", layout="wide")

# 🔐 Конфигурация пользователей
config = {
    'credentials': {
        'usernames': {
            'admin': {
                'email': 'admin@veloreg.ru',
                'name': 'Главный администратор',
                'password': 'Veloreg2026!'  # ← ИЗМЕНИТЕ на свой пароль!
            },
            'manager': {
                'email': 'manager@veloreg.ru', 
                'name': 'Менеджер',
                'password': 'Manager123!'     # ← ИЗМЕНИТЕ!
            }
        }
    },
    'cookie': {
        'expiry_days': 7,
        'key': 'veloreg_secret_cookie_key_change_me_2026',
        'name': 'veloreg_auth'
    },
    'preauthorized': {
        'emails': {}
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'], 
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('🔐 Вход в систему', fields=['email', 'password'])

if authentication_status == False:
    st.error('❌ Неверный логин или пароль')
    st.stop()
elif authentication_status == None:
    st.warning('🔐 Пожалуйста, введите логин и пароль')
    st.stop()
elif authentication_status:
    # ✅ АВТОРИЗОВАННЫЙ БЛОК
    st.sidebar.success(f'👋 Добро пожаловать *{name}*')
    authenticator.logout('🚪 Выход', 'main')
    
    st.title(f"🆔 **Veloreg CRM** | {name}")
    
    # Роли
    role = 'admin' if username == 'admin' else 'manager'
    st.sidebar.info(f"🎭 Роль: **{role.upper()}**")
    
    # Навигация
    page = st.sidebar.selectbox("📂 Раздел", ["📊 Дашборд", "🚲 Байки", "👥 Арендаторы", "⚡ Выдача"])
    
    @st.cache_resource
    def get_db():
        db_path = 'veloreg.db'
        if not os.path.exists(db_path) and os.path.exists('VELY.-Uchet.xlsx'):
            conn_temp = sqlite3.connect(db_path)
            xl = pd.ExcelFile('VELY.-Uchet.xlsx')
            for sheet in xl.sheet_names:
                df = pd.read_excel('VELY.-Uchet.xlsx', sheet_name=sheet)
                df.to_sql(sheet.lower().replace(' ', '_'), conn_temp, if_exists='replace')
            conn_temp.close()
        return sqlite3.connect(db_path)
    
    conn = get_db()
    
    if page == "📊 Дашборд":
        col1, col2, col3 = st.columns(3)
        df_b = pd.read_sql("SELECT * FROM реестр_байков", conn)
        status_col = next((col for col in df_b.columns if 'Статус' in col), None)
        if status_col:
            status = df_b[status_col].value_counts()
            with col1: st.metric("🔴 В аренде", status.get('В аренде', 0))
            with col2: st.metric("🟢 Готово", status.get('Готов к выдаче', 0))
            with col3: st.metric("🟡 Сервис", status.get('В сервисе', 0))
        
        fig = px.pie(status) if status_col else px.pie()
        st.plotly_chart(fig)
    
    elif page == "⚡ Выдача":
        st.header("🚀 Выдача байка")
        with st.form("issue"):
            col1, col2 = st.columns(2)
            with col1:
                fio = st.text_input("👤 ФИО")
                bike = st.number_input("🚲 № байка", 1000, 1100)
            with col2:
                phone = st.text_input("📱 Телефон")
                kanal = st.selectbox("📢 Канал", ["Специалист", "Авито"])
            
            if st.form_submit_button("✅ Выдать!"):
                cursor = conn.cursor()
                cursor.execute("UPDATE реестр_байков SET Статус='В аренде' WHERE номер_байка=?", (bike,))
                cursor.execute("INSERT INTO арендаторы (ФИО, номер_байка, номер_телефона) VALUES(?,?,?)", 
                              (fio, bike, phone))
                conn.commit()
                st.success(f"🎉 Байк {bike} выдан {fio}!")
                st.balloons()
                st.rerun()
    
    # Остальные страницы...

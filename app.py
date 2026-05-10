import streamlit as st
import streamlit_authenticator as stauth

# Простая авторизация
credentials = {
    "usernames": {
        "admin": {
            "name": "Главный администратор",
            "password": "veloreg2026"  # ← ИЗМЕНИТЕ!
        },
        "manager": {
            "name": "Менеджер",
            "password": "manager123"   # ← ИЗМЕНИТЕ!
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='veloreg_auth',
    key='random_key_2026',  # ← ИЗМЕНИТЕ!
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('main', fields=['username', 'password'])

if authentication_status == False:
    st.error('❌ Неправильный логин/пароль')
elif authentication_status == None:
    st.warning('🔐 Войдите для доступа')
    st.stop()
elif authentication_status:
    # Главная страница...
    authenticator.logout('Logout', 'main')

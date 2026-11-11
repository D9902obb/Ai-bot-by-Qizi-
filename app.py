import streamlit as st
import google.generativeai as genai

# --- Настройка страницы ---
st.set_page_config(page_title="Мой ИИ-помощник", page_icon="🤖", layout="centered")
st.title("🤖 Мой ИИ-помощник")
st.caption("Работает на Google Gemini. Бесплатно.")

# --- Боковая панель с кнопкой очистки ---
with st.sidebar:
    st.header("Настройки")
    if st.button("Очистить историю чата"):
        st.session_state.messages = []
        st.rerun()

# --- Подключение API-ключа ---
try:
    # Ключ берется из секретов Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY. Добавьте его в настройках Streamlit Cloud (Settings → Secrets).")
    st.stop()

# Настройка Gemini
genai.configure(api_key=api_key)

# Выбираем модель (gemini-1.5-flash быстрая и бесплатная)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Инициализация истории диалога ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Показываем прошлые сообщения при перезагрузке страницы
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Поле ввода и логика чата ---
if prompt := st.chat_input("Напишите сообщение..."):
    # 1. Добавляем сообщение пользователя в историю и выводим на экран
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Формируем ответ
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                # Преобразуем историю в формат, понятный для Gemini
                history = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                # Отправляем запрос
                response = model.generate_content(history)
                answer = response.text
                
                # Выводим ответ
                st.markdown(answer)
                
                # 3. Сохраняем ответ бота в историю
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Произошла ошибка при обращении к ИИ: {e}")

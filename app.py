import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="ИИ-Помощник ученика", page_icon="🎓", layout="centered")
st.title("🎓 ИИ-Помощник ученика")
st.caption("Объяснит любую тему простыми словами и поможет с домашкой.")

# --- Подключение API-ключа ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY. Добавьте его в настройках Streamlit Cloud.")
    st.stop()

# Инициализация клиента
client = genai.Client(api_key=api_key)

# --- Боковая панель ---
with st.sidebar:
    st.header("Настройки")
    subject = st.selectbox(
        "Какой предмет изучаем?",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    if st.button("Очистить историю"):
        st.session_state.messages = []
        st.rerun()

# --- Инструкция для бота ---
base_prompt = (
    "Ты — талантливый, терпеливый и дружелюбный учитель. "
    "Объясняй сложные вещи простым и понятным языком, приводи примеры из жизни. "
    "Если ученик просит решить домашнее задание, НЕ давай сразу готовый ответ, "
    "а объясни принцип решения и задай наводящий вопрос. "
    "Хвали за правильные ответы и поддерживай при ошибках."
)
if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}."

# --- История сообщений ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Логика чата ---
if prompt := st.chat_input("Задай вопрос или напиши тему..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Преобразуем историю для SDK
            contents = []
            for m in st.session_state.messages:
                contents.append(
                    types.Content(
                        role="user" if m["role"] == "user" else "model",
                        parts=[types.Part(text=m["content"])]
                    )
                )

            # Отправляем запрос с потоковой передачей, используя новую модель
            response = client.models.generate_content_stream(
                model="gemini-3.8-flash", # Актуальная модель
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=base_prompt)
            )
            
            # Печатаем ответ по кусочкам
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            # Убираем мигающий курсор в конце
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ошибка: {e}")

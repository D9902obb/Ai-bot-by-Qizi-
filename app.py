import streamlit as st
from google import genai
from google.genai import types
import os

st.set_page_config(page_title="ИИ-Помощник ученика", page_icon="🎓", layout="centered")
st.title("🎓 ИИ-Помощник ученика")
st.caption("Объяснит любую тему простыми словами и поможет с домашкой.")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY. Добавьте его в настройках Streamlit Cloud.")
    st.stop()

# Новый клиент google-genai с таймаутом 40 секунд
client = genai.Client(api_key=api_key)

with st.sidebar:
    st.header("Настройки")
    subject = st.selectbox(
        "Какой предмет изучаем?",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    if st.button("Очистить историю"):
        st.session_state.messages = []
        st.rerun()

base_prompt = (
    "Ты — талантливый, терпеливый и дружелюбный учитель. "
    "Объясняй сложные вещи простым и понятным языком, приводи примеры из жизни. "
    "Если ученик просит решить домашнее задание, НЕ давай сразу готовый ответ, "
    "а объясни принцип решения и задай наводящий вопрос. "
    "Хвали за правильные ответы и поддерживай при ошибках."
)
if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}."

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Задай вопрос или напиши тему..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Учитель готовит объяснение..."):
            try:
                # Собираем историю в формат нового SDK
                contents = []
                for m in st.session_state.messages:
                    contents.append(
                        types.Content(
                            role="user" if m["role"] == "user" else "model",
                            parts=[types.Part(text=m["content"])]
                        )
                    )

                # Запрос с таймаутом, чтобы не зависало навсегда
                response = client.models.generate_content(
                    model="gemini-3.5-flash", # при желании можно вернуть 3.8-flash
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=base_prompt,
                        http_options=types.HttpOptions(timeout=40) # 40 секунд максимум
                    )
                )
                
                answer = response.text
                if not answer:
                    st.warning("Модель вернула пустой ответ. Попробуйте переформулировать вопрос.")
                else:
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
            except Exception as e:
                st.error(f"Ошибка: {e}. Возможно, сервер Gemini перегружен. Попробуйте позже.")

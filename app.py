import streamlit as st
import google.generativeai as genai

# --- Настройка страницы ---
st.set_page_config(page_title="ИИ-Помощник ученика", page_icon="🎓", layout="centered")
st.title("🎓 ИИ-Помощник ученика")
st.caption("Объяснит любую тему простыми словами и поможет с домашкой.")

# --- Подключение API-ключа ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY. Добавьте его в настройках Streamlit Cloud (Settings → Secrets).")
    st.stop()

genai.configure(api_key=api_key)

# --- Боковая панель ---
with st.sidebar:
    st.header("Настройки")
    
    # Выбор предмета
    subject = st.selectbox(
        "Какой предмет изучаем?",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    
    if st.button("Очистить историю"):
        st.session_state.messages = []
        st.rerun()

# --- Формирование характера бота (System Instruction) ---
base_prompt = (
    "Ты — талантливый, терпеливый и дружелюбный учитель. "
    "Твоя цель — помочь ученику разобраться в теме. "
    "Объясняй сложные вещи простым и понятным языком, как будто рассказываешь другу. "
    "Обязательно приводи примеры из жизни. "
    "Если ученик просит решить домашнее задание, НЕ давай сразу готовый ответ. "
    "Вместо этого объясни принцип решения и задай наводящий вопрос, чтобы ученик сам дошел до ответа. "
    "Хвали ученика, если он правильно отвечает, и поддерживай, если он ошибается. "
    "Если используешь формулы, пиши их понятно текстом."
)

# Добавляем специфику предмета
if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}. Отвечай с учетом специфики этого предмета."

# --- Инициализируем модель ---
model = genai.GenerativeModel(
    "gemini-3.8-flash",
    system_instruction=base_prompt
)

# --- Инициализация истории диалога ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Показываем прошлые сообщения при перезагрузке страницы
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Поле ввода и логика чата ---
if prompt := st.chat_input("Задай вопрос или напиши тему..."):
    # 1. Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Формируем ответ
    with st.chat_message("assistant"):
        with st.spinner("Учитель готовит объяснение..."):
            try:
                # Собираем историю
                history = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                # Отправляем запрос (без потоковой передачи)
                response = model.generate_content(history)
                
                # Проверяем, не пустой ли ответ
                if not response.text:
                    st.warning("Модель вернула пустой ответ. Попробуйте переформулировать вопрос.")
                else:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")

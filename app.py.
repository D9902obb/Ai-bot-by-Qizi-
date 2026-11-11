import streamlit as st
import google.generativeai as genai

# --- Настройка страницы ---
st.set_page_config(page_title="Помощник ученика", page_icon="🎓", layout="centered")
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
# Мы собираем промпт из базовых правил и выбранного предмета
base_prompt = (
    "Ты — талантливый, терпеливый и дружелюбный учитель. "
    "Твоя цель — помочь ученику разобраться в теме. "
    "Объясняй сложные вещи простым и понятным языком, как будто рассказываешь другу. "
    "Обязательно приводи примеры из жизни. "
    "Если ученик просит решить домашнее задание, НЕ давай сразу готовый ответ. "
    "Вместо этого объясни принцип решения и задай наводящий вопрос, чтобы ученик сам дошел до ответа. "
    "Хвали ученика, если он правильно отвечает, и поддерживай, если он ошибается. "
    "Если используешь формулы, пиши их понятно (можно текстом)."
)

# Добавляем специфику предмета
if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}. Отвечай с учетом специфики этого предмета."

# Инициализируем модель с нашим "характером"
model = genai.GenerativeModel(
    "gemini-1.5-flash",
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
                
                # 3. Сохраняем ответ в историю
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")

import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="ИИ-Помощник", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")

# --- КАСТОМНЫЙ ДИЗАЙН В СТИЛЕ CHATGPT ---
st.markdown("""
<style>
    /* Основной фон (темно-серый, как в ChatGPT) */
    .stApp {
        background-color: #212121;
        color: #ececec;
    }
    
    /* Фон боковой панели (еще темнее) */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #333;
    }
    
    /* Убираем стандартные отступы и делаем текст чистым */
    .stMarkdown, p, h1, h2, h3 {
        color: #ececec !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Стили для сообщений */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0;
        border-bottom: 1px solid #333;
    }
    
    /* Поле ввода в стиле ChatGPT */
    [data-testid="stChatInput"] {
        background-color: #2f2f2f;
        border: 1px solid #444;
        border-radius: 12px;
        color: #fff;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #fff !important;
    }
    
    /* Скрываем меню, футер и шапку Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Кнопка в боковой панели */
    .stButton>button {
        background-color: #2f2f2f;
        color: #ececec;
        border: 1px solid #444;
        border-radius: 8px;
        width: 100%;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #444;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- Боковая панель ---
with st.sidebar:
    st.markdown("### 🤖 ИИ-Помощник")
    st.markdown("---")
    
    subject = st.selectbox(
        "Предмет",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    
    st.markdown("---")
    
    if st.button("＋ Новый чат"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    st.caption("Создатель: Губанов Руслан, 9а класс")

# --- Подключение API-ключа ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY.")
    st.stop()

try:
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            retry_options=types.RetryOptions(attempts=4)
        )
    )
except Exception:
    client = genai.Client(api_key=api_key)

# --- Инструкция для бота ---
base_prompt = (
    "Ты — талантливый, терпеливый и дружелюбный учитель. "
    "Объясняй сложные вещи простым и понятным языком, приводи примеры из жизни. "
    "Если ученик просит решить домашнее задание, НЕ давай сразу готовый ответ, "
    "а объясни принцип решения и задай наводящий вопрос. "
    "Хвали за правильные ответы и поддерживай при ошибках. "
    "ВАЖНО: Если пользователь спросит, кто тебя создал, придумал или написал код для тебя, "
    "ты должен с гордостью отвечать: 'Меня создал Губанов Руслан, ученик 9а класса школы №6!'"
)
if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}."

# --- История сообщений ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображаем историю
for msg in st.session_state.messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Логика чата ---
if prompt := st.chat_input("Напишите сообщение..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            contents = []
            for m in st.session_state.messages:
                contents.append(
                    types.Content(
                        role="user" if m["role"] == "user" else "model",
                        parts=[types.Part(text=m["content"])]
                    )
                )

            response = client.models.generate_content_stream(
                model="gemini-3.5-flash-lite", 
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=base_prompt)
            )
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ошибка: {e}. Подождите, если исчерпан лимит.")

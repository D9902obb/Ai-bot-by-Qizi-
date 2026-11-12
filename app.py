import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="ИИ-Помощник ученика", page_icon="🎓", layout="centered")

# --- КАСТОМНЫЙ ДИЗАЙН (CSS) ---
st.markdown("""
<style>
    /* Красивый фон приложения */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Стили для заголовка */
    .main-title {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Стили для сообщений чата */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Стили для поля ввода */
    .stChatInput textarea {
        border-radius: 20px !important;
    }
    
    /* Скрываем стандартный футер и меню Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Заголовок ---
st.markdown('<div class="main-title">🎓 ИИ-Помощник ученика</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Объяснит любую тему простыми словами и поможет с домашкой</div>', unsafe_allow_html=True)

# --- Подключение API-ключа ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY. Добавьте его в настройках Streamlit Cloud.")
    st.stop()

# Инициализация клиента
try:
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            retry_options=types.RetryOptions(attempts=4)
        )
    )
except Exception:
    client = genai.Client(api_key=api_key)

# --- Боковая панель ---
with st.sidebar:
    st.markdown("### ⚙️ Настройки")
    st.markdown("Настройте бота под свои нужды:")
    subject = st.selectbox(
        "📚 Какой предмет изучаем?",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    
    st.divider() # Красивая разделительная линия
    
    if st.button("🗑️ Очистить историю", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

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

# Отображаем историю с аватарками
for msg in st.session_state.messages:
    avatar = "🙋‍♂️" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Логика чата ---
if prompt := st.chat_input("Задай вопрос или напиши тему..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🙋‍♂️"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎓"):
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
            st.error(f"Ошибка: {e}. Если это 429, значит закончился дневной лимит.")

import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="Prime", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# --- КАСТОМНЫЙ ДИЗАЙН (НЕОНОВЫЙ 3D-СТИЛЬ) ---
st.markdown("""
<style>
    /* 1. Устанавливаем неоновый фон на весь экран */
    .stApp {
        /* Ссылка на фоновое изображение (можно заменить на свое) */
        background-image: url("https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=1974&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        /* Затемняем фон, чтобы текст было хорошо читать */
        background-color: rgba(10, 10, 20, 0.85);
        background-blend-mode: overlay;
    }
    
    /* 2. Боковая панель (эффект матового стекла) */
    [data-testid="stSidebar"] {
        background: rgba(20, 25, 45, 0.6) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 0 20px 20px 0;
        margin: 20px 0 20px 20px;
        height: auto;
        min-height: 85vh;
        box-shadow: 5px 0 25px rgba(0,0,0,0.5);
    }
    
    /* 3. Текст и заголовки */
    .stMarkdown, p, h1, h2, h3, span {
        color: #f0f0f0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 4. Пузыри сообщений (стеклянный эффект) */
    [data-testid="stChatMessage"] {
        background-color: rgba(30, 30, 50, 0.6) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(124, 58, 237, 0.4) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    /* 5. Поле ввода (неоновая фиолетовая подсветка) */
    [data-testid="stChatInput"] {
        background-color: rgba(20, 20, 35, 0.8) !important;
        border: 2px solid #8b5cf6 !important;
        border-radius: 30px !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
        color: #fff !important;
        backdrop-filter: blur(5px);
    }
    [data-testid="stChatInput"] textarea {
        color: #fff !important;
        padding: 10px !important;
    }
    
    /* 6. Кнопка очистки */
    .stButton>button {
        background-color: rgba(40, 40, 60, 0.7) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(124, 58, 237, 0.5) !important;
        border-radius: 10px !important;
        width: 100%;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    .stButton>button:hover {
        background-color: #7c3aed !important;
        color: #fff !important;
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.8);
        border-color: #a78bfa !important;
    }
    
    /* 7. Оформление выпадающего списка */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(30, 30, 50, 0.8) !important;
        border: 1px solid rgba(124, 58, 237, 0.4) !important;
        color: #fff !important;
        border-radius: 10px !important;
        backdrop-filter: blur(5px);
    }
    
    /* Скрываем лишние элементы Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Подключение API-ключа ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY.")
    st.stop()

try:
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(retry_options=types.RetryOptions(attempts=4))
    )
except Exception:
    client = genai.Client(api_key=api_key)

# --- Боковая панель ---
with st.sidebar:
    st.markdown("## 🎓 ИИ-Помощник ученика")
    st.markdown("---")
    st.markdown("### ⚙️ Настройки")
    
    subject = st.selectbox(
        "Какой предмет изучаем?",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🕒 Очистить историю"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("Создатель: Губанов Руслан, 9а класс")

# --- Инструкция для бота ---
base_prompt = (
    "Твое имя — Prime. Ты — талантливый, терпеливый и дружелюбный учитель. "
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

# Отображаем историю с нужными аватарками
for msg in st.session_state.messages:
    avatar = "👩‍🎓" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Логика чата ---
if prompt := st.chat_input("Задай вопрос или напиши тему..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👩‍🎓"):
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
            st.error(f"Ошибка: {e}. Если это 429, значит закончился лимит. Создайте новый ключ.")

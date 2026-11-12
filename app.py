import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="Prime", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# --- КАСТОМНЫЙ ДИЗАЙН (НЕОНОВЫЙ 3D-СТИЛЬ) ---
st.markdown("""
<style>
    /* Основной фон */
    .stApp {
        background-image: url("https://raw.githubusercontent.com/D9902obb/Ai-bot-by-Qizi-/6f164babca9829332a8448705c6c84796ffe72a6/IMG_20261112_111419_754.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: rgba(10, 10, 20, 0.85);
        background-blend-mode: overlay;
    }
    
    /* Боковая панель */
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 35, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(124, 58, 237, 0.3);
    }
    
    /* Текст */
    .stMarkdown, p, h1, h2, h3, span {
        color: #f8fafc !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Пузыри сообщений */
    [data-testid="stChatMessage"] {
        background-color: rgba(30, 35, 55, 0.75) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(124, 58, 237, 0.4) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    /* Поле ввода */
    [data-testid="stChatInput"] {
        background-color: rgba(20, 25, 40, 0.9) !important;
        border: 2px solid #8b5cf6 !important;
        border-radius: 30px !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.6) !important;
    }
    
    /* Кнопки в стартовом меню */
    .stButton>button {
        background: rgba(30, 35, 55, 0.6) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(124, 58, 237, 0.5) !important;
        border-radius: 12px !important;
        width: 100%;
        height: 60px;
        font-size: 16px !important;
        transition: all 0.3s ease;
        backdrop-filter: blur(5px);
    }
    .stButton>button:hover {
        background: rgba(124, 58, 237, 0.8) !important;
        color: #fff !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.8);
        border-color: #a78bfa !important;
        transform: translateY(-2px);
    }
    
    /* Скрываем лишнее */
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
    st.markdown("## 🎓 ИИ-Помощник")
    st.markdown("---")
    st.markdown("### ⚙️ Настройки")
    subject = st.selectbox(
        "Предмет:",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🕒 Очистить историю"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    st.caption("Создатель: Губанов Руслан, 9а класс")

# --- Инструкция для бота ---
base_prompt = (
    "Твое имя — Prime. Ты — талантливый, терпеливый и дружелюбный учитель. "
    "Объясняй сложные вещи простым и понятным языком, приводи примеры из жизни. "
    "Если ученик присылает фото задачи, внимательно прочитай текст на нем и реши задачу шаг за шагом. "
    "Если ученик просит решить домашнее задание текстом, НЕ давай сразу готовый ответ, а объясни принцип. "
    "Хвали за правильные ответы и поддерживай при ошибках. "
    "ВАЖНО: Если пользователь спросит, кто тебя создал, придумал или написал код, "
    "ты должен с гордостью отвечать: 'Меня создал Губанов Руслан, ученик 9а класса школы №6!'"
)
if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}."

# --- Инициализация истории ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "starter_prompt" not in st.session_state:
    st.session_state.starter_prompt = None

# --- Логика стартового экрана (если чат пуст) ---
if not st.session_state.messages and not st.session_state.starter_prompt:
    st.markdown("<h2 style='text-align: center; color: #a78bfa; margin-bottom: 30px;'>Привет! Я Prime 🤖<br><span style='font-size: 18px; color: #cbd5e1;'>Чем я могу помочь тебе сегодня?</span></h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Объясни теорему Пифагора"):
            st.session_state.starter_prompt = "Объясни теорему Пифагора простыми словами"
            st.rerun()
        if st.button("🧬 Что такое фотосинтез?"):
            st.session_state.starter_prompt = "Объясни процесс фотосинтеза кратко и понятно"
            st.rerun()
    with col2:
        if st.button("📝 Помоги написать конспект"):
            st.session_state.starter_prompt = "Как правильно и быстро написать конспект по параграфу?"
            st.rerun()
        if st.button("🌍 Столицы стран"):
            st.session_state.starter_prompt = "Перечисли столицы Европы и дай к ним короткие подсказки для запоминания"
            st.rerun()

# --- Отображение истории ---
for msg in st.session_state.messages:
    avatar = "👩‍🎓" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            st.image(msg["image"], width=300)
        if msg["content"]:
            st.markdown(msg["content"])

# --- Поле ввода ---
chat_input = st.chat_input("Задай вопрос или прикрепи фото (📎)...", accept_file=True, file_type=["jpg", "jpeg", "png"])

# Проверяем, была ли нажата кнопка стартового меню
if st.session_state.starter_prompt:
    class MockInput:
        def __init__(self, text):
            self.text = text
            self.files = []
    chat_input = MockInput(st.session_state.starter_prompt)
    st.session_state.starter_prompt = None

# --- Логика чата ---
if chat_input:
    user_text = chat_input.text if hasattr(chat_input, 'text') else str(chat_input)
    user_files = chat_input.files if hasattr(chat_input, 'files') else []

    msg_data = {"role": "user", "content": user_text, "image": None}
    if user_files:
        msg_data["image"] = user_files[0]

    st.session_state.messages.append(msg_data)
    
    with st.chat_message("user", avatar="👩‍🎓"):
        if msg_data["image"]:
            st.image(msg_data["image"], width=300)
        if msg_data["content"]:
            st.markdown(msg_data["content"])

    with st.chat_message("assistant", avatar="🎓"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            contents = []
            for m in st.session_state.messages:
                parts = []
                if m.get("content"):
                    parts.append(types.Part(text=m["content"]))
                if m.get("image"):
                    img_file = m["image"]
                    parts.append(
                        types.Part.from_bytes(data=img_file.getvalue(), mime_type=img_file.type)
                    )
                if parts:
                    contents.append(
                        types.Content(role="user" if m["role"] == "user" else "model", parts=parts)
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
            st.session_state.messages.append({"role": "assistant", "content": full_response, "image": None})
            
        except Exception as e:
            st.error(f"Ошибка: {e}")

import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="Prime", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- КАСТОМНЫЙ ДИЗАЙН (КРАСНЫЙ НЕОН С ВАШИМ ФОНОМ) ---
st.markdown("""
<style>
    /* Основной фон (используется ваша картинка с GitHub) */
    .stApp {
        background-image: url("https://raw.githubusercontent.com/D9902obb/Ai-bot-by-Qizi-/a4d581252982667f5819c2d29eac44c58f286e9e/IMG_20261112_130305_537.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: #000000;
    }
    
    /* Боковая панель (полупрозрачная) */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.85) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid #ff1a1a;
    }
    
    /* Текст */
    .stMarkdown, p, h1, h2, h3, span, label {
        color: #f8fafc !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Стили для пузырей сообщений */
    [data-testid="stChatMessage"] {
        background-color: rgba(17, 17, 17, 0.85) !important;
        backdrop-filter: blur(5px);
        border: 1px solid #ff1a1a !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 0 15px rgba(255, 26, 26, 0.15);
    }
    
    /* Поле ввода (красная неоновая рамка) */
    [data-testid="stChatInput"] {
        background-color: rgba(10, 10, 10, 0.9) !important;
        border: 2px solid #ff1a1a !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(255, 26, 26, 0.4) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    
    /* Кнопки */
    .stButton>button {
        background-color: rgba(17, 17, 17, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid #ff1a1a !important;
        border-radius: 8px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff1a1a !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(255, 26, 26, 0.7);
    }
    
    /* Выпадающий список */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(17, 17, 17, 0.9) !important;
        border: 1px solid #ff1a1a !important;
        color: #fff !important;
    }
    
    /* Радиокнопки (режимы) */
    [data-testid="stSidebar"] .stRadio > div {
        background-color: rgba(17, 17, 17, 0.8);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255, 26, 26, 0.3);
    }
    
    /* Кастомный заголовок */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        margin-top: -20px;
        margin-bottom: 0px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }
    .main-title .red-letter {
        color: #ff1a1a;
        text-shadow: 0 0 20px rgba(255, 26, 26, 0.8);
    }
    .main-subtitle {
        text-align: center;
        color: #d1d5db;
        font-size: 1.2rem;
        margin-bottom: 40px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }
    
    /* Скрываем лишнее */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- КАСТОМНЫЙ ЗАГОЛОВОК ---
st.markdown("""
<div class="main-title">
    <span>🎓</span>
    <span><span class="red-letter">P</span>rime</span>
</div>
<div class="main-subtitle">ИИ-Помощник ученика. Объясняет любую тему простыми словами.</div>
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
    st.markdown("<h2 style='color: #ff1a1a;'>🎓 Prime</h2>", unsafe_allow_html=True)
    st.markdown("### Настройки")
    
    subject = st.selectbox(
        "Какой предмет изучаем?",
        ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык", "Биология", "Химия"]
    )
    
    st.markdown("---")
    st.markdown("### 🧠 Умный режим")
    learning_mode = st.radio(
        "Стиль общения:",
        ["Обычный помощник", "Объясни как 5-летнему", "Режим Экзаменатора"]
    )
    
    st.markdown("---")
    if st.button("🗑 Очистить историю"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Создатель: Губанов Руслан, 9а класс")

# --- Формирование инструкции для бота ---
base_prompt = (
    "Твое имя — Prime. Ты — талантливый, дружелюбный учитель. "
    "ВАЖНО: Если пользователь спросит, кто тебя создал, придумал или написал код, "
    "ты должен с гордостью отвечать: 'Меня создал Губанов Руслан, ученик 9а класса школы №6!' "
)

if subject != "Общие вопросы":
    base_prompt += f" Сейчас мы изучаем предмет: {subject}. "

if learning_mode == "Объясни как 5-летнему":
    base_prompt += (
        "ОБЯЗАТЕЛЬНОЕ ПРАВИЛО: Объясняй любую тему так, как будто объясняешь пятилетнему ребенку. "
        "Используй самые простые слова, приводи примеры с игрушками или конфетами. "
        "Никаких сложных терминов."
    )
elif learning_mode == "Режим Экзаменатора":
    base_prompt += (
        "ОБЯЗАТЕЛЬНОЕ ПРАВИЛО: Ты — строгий экзаменатор. "
        "Задай ученику ОДИН вопрос по теме. Дождись ответа. Проверь его, укажи на ошибки и задай следующий. "
        "Не давай правильный ответ сразу. В конце поставь оценку (например, 4/5)."
    )
else:
    base_prompt += (
        "Объясняй сложные вещи простым и понятным языком, приводи примеры из жизни. "
        "Если ученик просит решить домашнее задание, НЕ давай сразу готовый ответ, а объясни принцип. "
        "Хвали за правильные ответы и поддерживай при ошибках."
    )

# --- Инициализация истории ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "starter_prompt" not in st.session_state:
    st.session_state.starter_prompt = None

# --- Стартовый экран (если чат пуст) ---
if not st.session_state.messages and not st.session_state.starter_prompt:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧮 Объясни теорему Пифагора"):
            st.session_state.starter_prompt = "Объясни теорему Пифагора простыми словами"
            st.rerun()
        if st.button("🧬 Что такое фотосинтез?"):
            st.session_state.starter_prompt = "Объясни процесс фотосинтеза кратко и понятно"
            st.rerun()
    with col2:
        if st.button("📝 Проверь мои знания по истории"):
            st.session_state.starter_prompt = "Начни экзамен по истории. Задай мне первый вопрос."
            st.rerun()
        if st.button("🌍 Столицы стран"):
            st.session_state.starter_prompt = "Перечисли столицы Европы и дай к ним короткие подсказки для запоминания"
            st.rerun()

# --- Отображение истории ---
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            st.image(msg["image"], width=300)
        if msg["content"]:
            st.markdown(msg["content"])

# --- Поле ввода ---
chat_input = st.chat_input("Задай вопрос или прикрепи фото (📎)...", accept_file=True, file_type=["jpg", "jpeg", "png"])

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
    
    with st.chat_message("user", avatar="👤"):
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

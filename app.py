import streamlit as st
from google import genai
from google.genai import types

# --- Настройка страницы ---
st.set_page_config(page_title="Prime", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# --- КАСТОМНЫЙ ДИЗАЙН (НЕОНОВЫЙ 3D-СТИЛЬ) ---
st.markdown("""
<style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/D9902obb/Ai-bot-by-Qizi-/6f164babca9829332a8448705c6c84796ffe72a6/IMG_20261112_111419_754.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: rgba(10, 10, 20, 0.85);
        background-blend-mode: overlay;
    }
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 35, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(124, 58, 237, 0.3);
    }
    .stMarkdown, p, h1, h2, h3, span, label {
        color: #f8fafc !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(30, 35, 55, 0.75) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(124, 58, 237, 0.4) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stChatInput"] {
        background-color: rgba(20, 25, 40, 0.9) !important;
        border: 2px solid #8b5cf6 !important;
        border-radius: 30px !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.6) !important;
    }
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
    /* Красивое оформление радиокнопок в сайдбаре */
    [data-testid="stSidebar"] .stRadio > div {
        background-color: rgba(30, 35, 55, 0.5);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(124, 58, 237, 0.3);
    }
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
    
    st.markdown("---")
    
    # НОВОЕ: Умный режим обучения
    st.markdown("### 🧠 Умный режим")
    learning_mode = st.radio(
        "Выберите стиль общения:",
        ["Обычный помощник", "Объясни как 5-летнему", "Режим Экзаменатора"]
    )
    
    st.markdown("---")
    
    if st.button("🕒 Очистить историю"):
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

# Добавляем правила в зависимости от выбранного режима
if learning_mode == "Объясни как 5-летнему":
    base_prompt += (
        "ОБЯЗАТЕЛЬНОЕ ПРАВИЛО: Объясняй любую тему так, как будто объясняешь пятилетнему ребенку. "
        "Используй самые простые слова, приводи примеры с игрушками, конфетами или сказочными персонажами. "
        "Никаких сложных терминов и длинных формул."
    )
elif learning_mode == "Режим Экзаменатора":
    base_prompt += (
        "ОБЯЗАТЕЛЬНОЕ ПРАВИЛО: Ты — строгий, но справедливый экзаменатор. "
        "Когда ученик называет тему, задай ему ОДИН вопрос по этой теме. Дождись его ответа. "
        "Проверь ответ, укажи на ошибки (если есть) и задай следующий вопрос. Не давай правильный ответ сразу, "
        "дай ученику подумать. В конце поставь оценку (например, 4/5)."
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
    st.markdown("<h2 style='text-align: center; color: #a78bfa; margin-bottom: 30px;'>Привет! Я Prime 🤖<br><span style='font-size: 18px; color: #cbd5e1;'>Выбери режим в меню слева и давай учиться!</span></h2>", unsafe_allow_html=True)
    
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
    avatar = "👩‍🎓" if msg["role"] == "user" else "🎓"
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

import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
from gtts import gTTS
import io
import re
import json

# --- Настройка страницы ---
st.set_page_config(
    page_title="Prime", 
    page_icon="https://raw.githubusercontent.com/D9902obb/Ai-bot-by-Qizi-/1ecdb4de9502c3edfc2a7a29db13ba5819763dc7/IMG_20261112_203701_728.jpg", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ДИЗАЙН (КРАСНЫЙ НЕОН) ---
st.markdown("""
<style>
    .stApp { background-image: url("https://raw.githubusercontent.com/D9902obb/Ai-bot-by-Qizi-/a4d581252982667f5819c2d29eac44c58f286e9e/IMG_20261112_130305_537.jpg"); background-size: cover; background-position: center; background-attachment: fixed; background-color: #000000; }
    [data-testid="stSidebar"] { background-color: rgba(10, 10, 10, 0.85) !important; backdrop-filter: blur(10px); border-right: 1px solid #ff1a1a; }
    .stMarkdown, p, h1, h2, h3, span, label { color: #f8fafc !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stChatMessage"] { background-color: rgba(17, 17, 17, 0.85) !important; backdrop-filter: blur(5px); border: 1px solid #ff1a1a !important; border-radius: 12px !important; padding: 15px !important; margin-bottom: 15px !important; box-shadow: 0 0 15px rgba(255, 26, 26, 0.15); }
    [data-testid="stChatInput"] { background-color: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff1a1a !important; border-radius: 12px !important; box-shadow: 0 0 20px rgba(255, 26, 26, 0.4) !important; }
    [data-testid="stChatInput"] textarea { color: #ffffff !important; }
    .stButton>button, .stDownloadButton>button { background-color: rgba(17, 17, 17, 0.8) !important; color: #ffffff !important; border: 1px solid #ff1a1a !important; border-radius: 8px !important; width: 100%; transition: all 0.3s ease; }
    .stButton>button:hover, .stDownloadButton>button:hover { background-color: #ff1a1a !important; color: #ffffff !important; box-shadow: 0 0 20px rgba(255, 26, 26, 0.7); }
    .stSelectbox div[data-baseweb="select"] > div { background-color: rgba(17, 17, 17, 0.9) !important; border: 1px solid #ff1a1a !important; color: #fff !important; }
    [data-testid="stSidebar"] .stRadio > div { background-color: rgba(17, 17, 17, 0.8); padding: 10px; border-radius: 10px; border: 1px solid rgba(255, 26, 26, 0.3); }
    .main-title { text-align: center; font-size: 3.5rem; font-weight: 800; margin-top: -20px; margin-bottom: 0px; display: flex; justify-content: center; align-items: center; gap: 15px; }
    .main-title .red-letter { color: #ff1a1a; text-shadow: 0 0 20px rgba(255, 26, 26, 0.8); }
    .main-subtitle { text-align: center; color: #d1d5db; font-size: 1.2rem; margin-bottom: 40px; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title"><span><span class="red-letter">P</span>rime</span></div>
<div class="main-subtitle">ИИ-Помощник ученика. Проверка сочинений и карточки для запоминания.</div>
""", unsafe_allow_html=True)

# --- ПОДКЛЮЧЕНИЕ ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("⚠️ Не найден ключ GEMINI_API_KEY.")
    st.stop()

try:
    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(retry_options=types.RetryOptions(attempts=4)))
except Exception:
    client = genai.Client(api_key=api_key)

# --- ОЗВУЧКА ---
def generate_audio(text):
    try:
        clean_text = re.sub(r'\$\$(.*?)\$\$', '... формула ...', text, flags=re.DOTALL)
        clean_text = re.sub(r'\$(.*?)\$', r'\1', clean_text).replace('*', '').replace('#', '').replace('_', '')
        tts = gTTS(text=clean_text, lang='ru', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# --- ИНИЦИАЛИЗАЦИЯ ---
if "messages" not in st.session_state: st.session_state.messages = []
if "starter_prompt" not in st.session_state: st.session_state.starter_prompt = None
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff1a1a; text-align: center;'>🎓 Prime</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ПРОФИЛЬ УЧЕНИКА
    st.markdown("### 👤 Профиль ученика")
    user_name = st.text_input("Как тебя зовут?", placeholder="Например: Руслан")
    
    # ПОИСК В ИНТЕРНЕТЕ
    st.markdown("### 🌐 Поиск в интернете")
    web_search_enabled = st.toggle("Включить актуальные данные", value=False)
    
    st.markdown("---")
    
    # ВЫБОР ИНСТРУМЕНТА
    st.markdown("### 🛠 Режим работы")
    tool_mode = st.radio("Выберите инструмент:", ["💬 Умный чат", "🃏 Генератор карточек"])
    
    st.markdown("---")
    
    # НАСТРОЙКИ (Только для чата)
    if tool_mode == "💬 Умный чат":
        st.markdown("### ⚙️ Настройки")
        subject = st.selectbox("Предмет:", ["Общие вопросы", "Математика", "Физика", "История", "Русский язык", "Английский язык"])
        
        st.markdown("### 🧠 Умный режим")
        learning_mode = st.radio("Стиль:", ["Обычный", "Объясни как 5-летнему", "Экзаменатор"])

        st.markdown("---")
        # Голосовой ввод
        st.markdown("### 🎤 Голосовой ввод")
        audio_value = st.audio_input("Нажмите и говорите")
        if audio_value is not None and audio_value.file_id != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_value.file_id
            st.session_state.messages.append({"role": "user", "content": "🎤 Голосовое сообщение", "audio": audio_value, "image": None})
            st.rerun()

        st.markdown("---")
    
    # Скачивание истории
    if st.session_state.messages:
        chat_text = f"История диалога с Prime\nДата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        for msg in st.session_state.messages:
            role = "Вы" if msg["role"] == "user" else "Prime"
            content = msg.get("content", "")
            if msg.get("image"): content += " [Фото]"
            if msg.get("audio"): content = " [Голосовое сообщение]"
            chat_text += f"{role}: {content}\n\n"
        st.download_button("📥 Скачать историю (.txt)", data=chat_text, file_name=f"Prime_Chat.txt", mime="text/plain")

    if st.button("🗑 Очистить историю"):
        st.session_state.messages = []
        st.session_state.last_audio_id = None
        st.rerun()
        
    st.caption("Создатель: Губанов Руслан, 9а класс")

# --- ФОРМИРОВАНИЕ ПРОМПТА ДЛЯ ЧАТА ---
base_prompt = (
    "Твое имя — Prime. Ты — талантливый, дружелюбный учитель. "
    "ВАЖНО: Если пользователь спросит, кто тебя создал, отвечай: 'Меня создал Губанов Руслан, ученик 9а класса школы №6!' "
    "ОБЯЗАТЕЛЬНОЕ ПРАВИЛО ДЛЯ ФОРМУЛ: Все математические формулы оформляй в формате LaTeX через $."
)

# ПЕРСОНАЛИЗАЦИЯ
if user_name:
    base_prompt += f" Обращайся к ученику по имени: {user_name}. Хвали его по имени ('Отличная работа, {user_name}!')."

if tool_mode == "💬 Умный чат":
    if subject != "Общие вопросы": base_prompt += f" Предмет: {subject}. "
    if learning_mode == "Объясни как 5-летнему": base_prompt += "ОБЪЯСНЯЙ КАК 5-ЛЕТНЕМУ."
    elif learning_mode == "Экзаменатор": base_prompt += "Ты строгий экзаменатор."

# НАСТРОЙКА ПОИСКА В ИНТЕРНЕТЕ
# Добавляем инструмент, если переключатель включен
tools_list = []
if web_search_enabled:
    tools_list.append(types.Tool(google_search=types.GoogleSearch()))

# ==========================================
# ЭКРАН 1: ГЕНЕРАТОР КАРТОЧЕК
# ==========================================
if tool_mode == "🃏 Генератор карточек":
    st.markdown("### 🃏 Создай карточки для запоминания")
    st.info("Введите тему, и Prime создаст список вопросов и ответов. Нажмите на карточку, чтобы проверить себя!")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Тема (например: Неправильные глаголы английского, Столицы Европы, Формулы физики):")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("Создать карточки")
        
    if generate_btn and topic:
        with st.spinner("Prime придумывает карточки..."):
            prompt = f"Создай 5 карточек (вопрос-ответ) по теме: {topic}. Выведи их СТРОГО в формате JSON-массива, без лишнего текста. Пример: [{{\"q\": \"Вопрос 1\", \"a\": \"Ответ 1\"}}, {{\"q\": \"Вопрос 2\", \"a\": \"Ответ 2\"}}]"
            try:
                res = client.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
                raw_json = res.text.replace("```json", "").replace("```", "").strip()
                cards = json.loads(raw_json)
                
                st.markdown("---")
                st.markdown("### 👇 Нажми на карточку, чтобы увидеть ответ")
                for card in cards:
                    with st.expander(f"❓ {card['q']}"):
                        st.success(f"**Ответ:** {card['a']}")
            except Exception as e:
                st.error(f"Не удалось создать карточки. Попробуйте еще раз. Ошибка: {e}")

# ==========================================
# ЭКРАН 2: УМНЫЙ ЧАТ
# ==========================================
else:
    # Стартовый экран
    if not st.session_state.messages and not st.session_state.starter_prompt:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Проверить мое сочинение"):
                st.session_state.starter_prompt = f"Я хочу, чтобы ты проверил мое сочинение. Я прикреплю фото рукописного текста. Найди в нем грамматические и пунктуационные ошибки, объясни их и выдели главную мысль. {'Меня зовут ' + user_name + '.' if user_name else ''}"
                st.rerun()
        with col2:
            if st.button("🌐 Какая сегодня погода?"):
                st.session_state.starter_prompt = f"{user_name + ', ' if user_name else ''}Какая сегодня погода в моем городе?"
                st.rerun()

    # Отображение истории
    for i, msg in enumerate(st.session_state.messages):
        avatar = "👤" if msg["role"] == "user" else "🎓"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("audio"): st.audio(msg["audio"])
            if msg.get("image"): st.image(msg["image"], width=300)
            if msg.get("content") and msg["content"] != "🎤 Голосовое сообщение":
                st.markdown(msg["content"])
                
            if msg["role"] == "assistant":
                if st.button("🔊 Прослушать", key=f"tts_{i}"):
                    audio_data = generate_audio(msg["content"])
                    if audio_data: st.audio(audio_data, format="audio/mp3")

    # Поле ввода
    chat_input = st.chat_input("Задай вопрос или прикрепи фото сочинения (📎)...", accept_file=True, file_type=["jpg", "jpeg", "png"])

    if st.session_state.starter_prompt:
        class MockInput:
            def __init__(self, text):
                self.text = text
                self.files = []
        chat_input = MockInput(st.session_state.starter_prompt)
        st.session_state.starter_prompt = None

    if chat_input:
        user_text = chat_input.text if hasattr(chat_input, 'text') else str(chat_input)
        user_files = chat_input.files if hasattr(chat_input, 'files') else []

        msg_data = {"role": "user", "content": user_text, "image": None, "audio": None}
        if user_files: msg_data["image"] = user_files[0]

        st.session_state.messages.append(msg_data)
        st.rerun() 

    # Ответ ИИ
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="🎓"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                contents = []
                for m in st.session_state.messages:
                    parts = []
                    if m.get("content") and m["content"] != "🎤 Голосовое сообщение":
                        parts.append(types.Part(text=m["content"]))
                    if m.get("image"):
                        parts.append(types.Part.from_bytes(data=m["image"].getvalue(), mime_type=m["image"].type))
                    if m.get("audio"):
                        parts.append(types.Part.from_bytes(data=m["audio"].getvalue(), mime_type=m["audio"].type))
                    
                    if parts:
                        contents.append(types.Content(role="user" if m["role"] == "user" else "model", parts=parts))

                # Включаем поиск в интернете, если он активирован
                config = types.GenerateContentConfig(
                    system_instruction=base_prompt,
                    tools=tools_list if tools_list else None
                )

                response = client.models.generate_content_stream(
                    model="gemini-3.5-flash-lite", 
                    contents=contents,
                    config=config
                )
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        response_placeholder.markdown(full_response.replace("$$", "$$ ") + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                if st.button("🔊 Прослушать ответ", key="tts_new"):
                    audio_data = generate_audio(full_response)
                    if audio_data: st.audio(audio_data, format="audio/mp3")
                            
            except Exception as e:
                st.error(f"Ошибка: {e}")

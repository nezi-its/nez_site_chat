# pip install streamlit google-generativeai

import os
import json
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import Content, Part, Tool, GenerateContentConfig, ThinkingConfig
from time import sleep

# Файл для истории чата
DB_FILE = "chat_history.json"

# Загружаем историю
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        chat_history = json.load(f)
else:
    chat_history = []

# --- Оформление страницы ---
st.set_page_config(page_title="✨ Minecraft Code Generator", page_icon="🛡️", layout="wide")

# Кастомизация интерфейса через sidebar
st.sidebar.title("⚙️ Настройки интерфейса")
theme_choice = st.sidebar.selectbox("Тема", ["Светлая", "Тёмная", "Minecraft Зеленая"])
font_size = st.sidebar.slider("Размер шрифта", min_value=12, max_value=24, value=16)
chat_bg_color = st.sidebar.color_picker("Цвет фона чата", "#f0f0f5")
user_bg_color = st.sidebar.color_picker("Цвет фона сообщений пользователя", "#d1e7dd")
ai_bg_color = st.sidebar.color_picker("Цвет фона сообщений AI", "#f8d7da")
button_color = st.sidebar.color_picker("Цвет кнопки", "#6a11cb")

# Применение кастомизации
if theme_choice == "Тёмная":
    st.markdown("""
    <style>
    body {background-color: #121212; color: #ffffff;}
    .stTextArea textarea {background-color: #1e1e1e; color: #ffffff; font-size: %dpx;}
    .stButton button {background-color: %s; color: white; font-weight: bold;}
    .chat-box {padding: 10px; border-radius: 10px; margin-bottom: 10px;}
    .user-box {background-color: %s; color: #0f5132;}
    .ai-box {background-color: %s; color: #842029;}
    </style>
    """ % (font_size, button_color, user_bg_color, ai_bg_color), unsafe_allow_html=True)
elif theme_choice == "Minecraft Зеленая":
    st.markdown("""
    <style>
    body {background-color: #228B22; color: #000000;}
    .stTextArea textarea {background-color: #90EE90; color: #000000; font-size: %dpx;}
    .stButton button {background-color: %s; color: white; font-weight: bold;}
    .chat-box {padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #006400;}
    .user-box {background-color: %s; color: #006400;}
    .ai-box {background-color: %s; color: #8B4513;}
    </style>
    """ % (font_size, button_color, user_bg_color, ai_bg_color), unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stTextArea textarea {background-color: %s; color: #111; font-size: %dpx;}
    .stButton button {background-color: %s; color: white; font-weight: bold;}
    .chat-box {padding: 10px; border-radius: 10px; margin-bottom: 10px;}
    .user-box {background-color: %s; color: #0f5132;}
    .ai-box {background-color: %s; color: #842029;}
    </style>
    """ % (chat_bg_color, font_size, button_color, user_bg_color, ai_bg_color), unsafe_allow_html=True)

st.title("🛡️ Minecraft Code Generator")
st.subheader("Генерируй код для модов, скриптов и миров Minecraft с помощью AI")

# API ключ через переменные окружения (без ввода в интерфейсе)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API ключ не найден! Установите переменную окружения GEMINI_API_KEY.")
else:
    # Ввод сообщения с фокусом на Minecraft
    user_input = st.text_area("Опишите, какой код Minecraft вам нужен (например, 'мод на новый меч' или 'скрипт для автоматической фермы'):", height=150)

    if st.button("Генерировать код"):
        if not user_input.strip():
            st.warning("Введите описание!")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")  # Исправил на реальную модель (предполагаю опечатку в оригинале)

            # Контекст для фокуса на Minecraft
            system_prompt = "Ты эксперт по Minecraft. Генерируй только код и инструкции для модов, скриптов (на Java, Python с MCreator или datapacks) или миров. Не добавляй лишний текст, только полезный код с комментариями."

            contents = [
                Content(
                    role="user",
                    parts=[Part.from_text(system_prompt + "\n\n" + user_input)],
                ),
            ]

            # Инструменты (если нужны, но в оригинале был GoogleSearch, который не стандартный; убрал для простоты)
            # Если нужно добавить поиск, реализуйте через внешние API

            generate_content_config = GenerateContentConfig(
                # Убрал thinking_config, так как он не стандартный; используйте temperature для креативности
                temperature=0.7,
            )

            # Потоковая генерация ответа
            response_text = ""
            response_container = st.empty()
            with st.spinner("🛡️ AI генерирует код..."):
                response = model.generate_content(contents, stream=True, generation_config=generate_content_config)
                for chunk in response:
                    if hasattr(chunk, 'text'):
                        response_text += chunk.text
                        response_container.markdown(f"<div class='chat-box ai-box'>{response_text}</div>", unsafe_allow_html=True)
                        sleep(0.02)  # Плавный эффект печати

            # Сохраняем в локальную базу
            chat_history.append({"user": user_input, "ai": response_text})
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)

# --- История чата ---
st.markdown("### 💬 История генераций")
for item in reversed(chat_history[-20:]):  # Последние 20 сообщений
    st.markdown(f"<div class='chat-box user-box'><b>Запрос:</b> {item['user']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='chat-box ai-box'><b>Код от AI:</b> {item['ai']}</div>", unsafe_allow_html=True)

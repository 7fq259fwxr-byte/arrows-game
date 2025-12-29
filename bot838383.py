#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arrows Pro Ultra Bot - Исправленная версия для PythonAnywhere
"""

import requests
import time
import json
import logging

# ====================== КОНФИГУРАЦИЯ ======================
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://7fq259fwxr-byte.github.io/arrows-game/"
SUPPORT_BOT = "@arrow_game_support_bot"

# ====================== ЛОГИРОВАНИЕ ======================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== ФУНКЦИИ ДЛЯ TELEGRAM API ======================

def telegram_api(method, data=None):
    """Универсальная функция для вызовов Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    
    try:
        # Используем таймауты и повторные попытки
        for attempt in range(3):
            try:
                if data:
                    response = requests.post(url, json=data, timeout=10)
                else:
                    response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        return result
                    else:
                        logger.error(f"Telegram API error: {result}")
                        time.sleep(2)  # Ждем перед повторной попыткой
                else:
                    logger.error(f"HTTP error {response.status_code}")
                    time.sleep(2)
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                time.sleep(2)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}")
                time.sleep(2)
                
    except Exception as e:
        logger.error(f"Error in telegram_api: {e}")
    
    return None

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения"""
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    if reply_markup:
        data["reply_markup"] = reply_markup
    
    return telegram_api("sendMessage", data)

def get_updates(offset=None, timeout=30):
    """Получение обновлений"""
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    
    try:
        # Для getUpdates используем GET запрос
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url, params=params, timeout=timeout + 5)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"GetUpdates HTTP error: {response.status_code}")
    except Exception as e:
        logger.error(f"Error in get_updates: {e}")
    
    return {"ok": False, "result": []}

def answer_callback_query(callback_query_id):
    """Ответ на callback запрос"""
    return telegram_api("answerCallbackQuery", {"callback_query_id": callback_query_id})

# ====================== КЛАВИАТУРЫ ======================

def create_main_keyboard():
    """Главное меню"""
    return {
        "inline_keyboard": [
            [{"text": "🎮 НАЧАТЬ ИГРУ", "web_app": {"url": GAME_URL}}],
            [
                {"text": "📊 Статистика", "callback_data": "stats"},
                {"text": "❓ Помощь", "callback_data": "help"}
            ],
            [{"text": "🆘 Поддержка", "url": f"https://t.me/{SUPPORT_BOT[1:]}"}]
        ]
    }

def create_simple_keyboard():
    """Простая клавиатура для теста"""
    return {
        "inline_keyboard": [
            [{"text": "🎮 ТЕСТ КНОПКИ", "web_app": {"url": GAME_URL}}]
        ]
    }

# ====================== ОБРАБОТЧИКИ ======================

def handle_start(chat_id, user_name):
    """Обработка /start"""
    logger.info(f"Обработка /start от {chat_id}")
    
    keyboard = create_simple_keyboard()  # Начнем с простой клавиатуры
    
    message = (
        f"Привет, {user_name}! 👋\n\n"
        "🎮 *Arrows Pro Ultra*\n\n"
        "Нажмите кнопку ниже для запуска игры!\n\n"
        f"🆘 Поддержка: {SUPPORT_BOT}"
    )
    
    result = send_message(chat_id, message, keyboard)
    
    if result:
        logger.info(f"Сообщение отправлено пользователю {chat_id}")
        return True
    else:
        logger.error(f"Не удалось отправить сообщение пользователю {chat_id}")
        return False

def handle_callback(callback_query):
    """Обработка callback кнопок"""
    try:
        query_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query["data"]
        
        # Отвечаем на callback
        answer_callback_query(query_id)
        
        if data == "stats":
            send_message(chat_id, "📊 Статистика игры...")
        elif data == "help":
            send_message(chat_id, "❓ Помощь по игре...")
            
    except Exception as e:
        logger.error(f"Error in handle_callback: {e}")

# ====================== ОСНОВНОЙ ЦИКЛ ======================

def test_connection():
    """Тест соединения с Telegram API"""
    print("🔍 Тестируем соединение с Telegram API...")
    
    try:
        # Проверяем доступность API
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_name = data["result"]["username"]
                print(f"✅ Соединение успешно! Бот: @{bot_name}")
                return True
            else:
                print(f"❌ Ошибка Telegram API: {data}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
    
    return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("🤖 ЗАПУСК ARROWS PRO ULTRA BOT")
    print("=" * 60)
    
    # Тест соединения
    if not test_connection():
        print("⚠️ Проверьте токен бота и интернет соединение")
        return
    
    print(f"🎮 Игра: {GAME_URL}")
    print(f"🆘 Поддержка: {SUPPORT_BOT}")
    print("=" * 60)
    print("⏳ Ожидание сообщений...")
    print("=" * 60)
    
    last_update_id = 0
    error_count = 0
    
    while True:
        try:
            # Получаем обновления
            updates = get_updates(last_update_id, timeout=25)
            
            if updates.get("ok"):
                error_count = 0  # Сброс счетчика ошибок
                
                for update in updates["result"]:
                    last_update_id = update["update_id"] + 1
                    
                    # Обработка callback
                    if "callback_query" in update:
                        handle_callback(update["callback_query"])
                    
                    # Обработка сообщений
                    elif "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        
                        if "text" in message:
                            text = message["text"]
                            user_name = message["chat"].get("first_name", "Игрок")
                            
                            if text == "/start":
                                print(f"📨 Получен /start от {user_name} ({chat_id})")
                                
                                # Пробуем отправить ответ
                                if handle_start(chat_id, user_name):
                                    print(f"✅ Ответ отправлен {user_name}")
                                else:
                                    print(f"❌ Не удалось отправить ответ {user_name}")
                            
                            elif text == "/test":
                                send_message(chat_id, "✅ Бот работает!")
                            
                            elif text.startswith("/"):
                                send_message(chat_id, f"Команда '{text}' не распознана. Используйте /start")
            
            else:
                error_count += 1
                print(f"⚠️ Ошибка получения обновлений #{error_count}")
                
                if error_count > 10:
                    print("🔄 Перезапуск через 30 секунд...")
                    time.sleep(30)
                    error_count = 0
            
            # Небольшая пауза
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Бот остановлен пользователем")
            break
            
        except Exception as e:
            error_count += 1
            print(f"⚠️ Ошибка в основном цикле: {e}")
            time.sleep(5)

# ====================== ТЕСТОВАЯ ФУНКЦИЯ ======================

def send_test_message():
    """Отправка тестового сообщения самому себе"""
    print("\n🧪 Тестовая отправка сообщения...")
    
    # Получаем ID бота
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            bot_id = data["result"]["id"]
            
            # Отправляем сообщение самому себе
            test_data = {
                "chat_id": bot_id,
                "text": "✅ Тестовое сообщение от бота!\n\nЕсли вы это видите, бот работает корректно.",
                "parse_mode": "Markdown"
            }
            
            result = telegram_api("sendMessage", test_data)
            if result:
                print("✅ Тестовое сообщение отправлено!")
                return True
    
    print("❌ Не удалось отправить тестовое сообщение")
    return False

# ====================== ЗАПУСК ======================

if __name__ == "__main__":
    # Проверяем наличие библиотеки requests
    try:
        import requests
        print("✅ Библиотека requests доступна")
    except ImportError:
        print("❌ Установите библиотеку: pip install requests")
        exit(1)
    
    # Запускаем тест
    send_test_message()
    
    # Запускаем бота
    main()

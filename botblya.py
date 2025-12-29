#!/usr/bin/env python3
import requests
import json
import time
import logging
from flask import Flask, request, jsonify
import threading
import os
from datetime import datetime

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
GAME_URL = "https://ваш-ник.pythonanywhere.com/"  # Замените на ваш URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# База данных
DATA_FILE = "users_data.json"

def load_data():
    """Загрузка данных из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Data loaded successfully. Users: {len(data.get('users', {}))}")
                return data
        logger.info("No data file found, creating new database")
        return {"users": {}, "leaderboard": [], "shop_items": initialize_shop()}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {"users": {}, "leaderboard": [], "shop_items": initialize_shop()}

def save_data(data):
    """Сохранение данных в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Data saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def initialize_shop():
    """Инициализация магазина"""
    return {
        "arrow_skins": [
            {"id": "default", "name": "Classic", "price": 0},
            {"id": "fire", "name": "Fire", "price": 100},
            {"id": "ice", "name": "Ice", "price": 150},
            {"id": "gold", "name": "Golden", "price": 300},
            {"id": "neon", "name": "Neon", "price": 200},
            {"id": "rainbow", "name": "Rainbow", "price": 500}
        ]
    }

def get_display_name(user_data):
    """Получение отображаемого имени пользователя"""
    user_id = user_data.get('id', '')
    
    # Пробуем получить username
    username = user_data.get('username')
    if username:
        return f"@{username}"
    
    # Или комбинацию имени и фамилии
    first_name = user_data.get('first_name', '')
    last_name = user_data.get('last_name', '')
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        # Если ничего нет, используем ID
        return f"Player{str(user_id)[-4:]}"

# API для игры
@app.route('/api/get_user_data', methods=['POST'])
def get_user_data():
    """Получение данных пользователя для игры"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username')
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        logger.info(f"Getting user data for ID: {user_id_str}")
        
        if user_id_str in db["users"]:
            user_data = db["users"][user_id_str]
            
            # Обновляем username если он изменился
            if username and username != user_data.get("username"):
                user_data["username"] = username
                save_data(db)
                logger.info(f"Updated username for user {user_id_str}: {username}")
            
            return jsonify({
                "success": True,
                "coins": user_data.get("coins", 0),
                "max_level": user_data.get("max_level", 1),
                "username": user_data.get("username", username or "Player"),
                "skins": user_data.get("skins", ["default"]),
                "selected_skin": user_data.get("selected_skin", "default"),
                "shop_items": db["shop_items"]
            })
        
        logger.info(f"User {user_id_str} not found in database")
        return jsonify({"success": False, "error": "User not found"}), 404
        
    except Exception as e:
        logger.error(f"Error in get_user_data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/register_user', methods=['POST'])
def register_user():
    """Регистрация нового пользователя"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        # Создаем отображаемое имя
        display_name = username or get_display_name({
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        })
        
        if user_id_str not in db["users"]:
            db["users"][user_id_str] = {
                "username": display_name,
                "coins": 100,  # Начальный бонус
                "max_level": 1,
                "skins": ["default"],
                "selected_skin": "default",
                "first_name": first_name,
                "last_name": last_name,
                "created_at": time.time(),
                "last_active": time.time()
            }
            
            logger.info(f"Registered new user: {user_id_str} - {display_name}")
            
            # Добавляем в лидерборд
            db["leaderboard"].append({
                "user_id": user_id_str,
                "username": display_name,
                "score": 1,
                "coins": 100,
                "updated_at": time.time()
            })
            
            save_data(db)
            
            return jsonify({
                "success": True,
                "message": "User registered successfully",
                "username": display_name,
                "coins": 100
            })
        else:
            logger.info(f"User {user_id_str} already exists")
            return jsonify({"success": False, "error": "User already exists"}), 400
            
    except Exception as e:
        logger.error(f"Error in register_user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update_score', methods=['POST'])
def update_score():
    """Обновление счета пользователя"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username')
        new_level = data.get('level', 1)
        coins_earned = data.get('coins_earned', 20)
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        logger.info(f"Updating score for user {user_id_str}: level={new_level}, coins={coins_earned}")
        
        if user_id_str not in db["users"]:
            # Автоматически регистрируем пользователя если его нет
            display_name = username or f"Player{str(user_id)[-4:]}"
            db["users"][user_id_str] = {
                "username": display_name,
                "coins": coins_earned,
                "max_level": new_level,
                "skins": ["default"],
                "selected_skin": "default",
                "created_at": time.time(),
                "last_active": time.time()
            }
            
            # Добавляем в лидерборд
            db["leaderboard"].append({
                "user_id": user_id_str,
                "username": display_name,
                "score": new_level,
                "coins": coins_earned,
                "updated_at": time.time()
            })
            
            logger.info(f"Auto-registered user {user_id_str} during score update")
        else:
            user = db["users"][user_id_str]
            
            # Обновляем username если он изменился
            if username and username != user.get("username"):
                user["username"] = username
                logger.info(f"Updated username for user {user_id_str}: {username}")
            
            # Обновляем монеты и уровень
            user["coins"] = user.get("coins", 0) + coins_earned
            if new_level > user.get("max_level", 1):
                user["max_level"] = new_level
            
            user["last_active"] = time.time()
        
        # Обновляем лидерборд
        update_leaderboard(db, user_id_str, username or db["users"][user_id_str]["username"], 
                          db["users"][user_id_str]["max_level"])
        
        save_data(db)
        
        return jsonify({
            "success": True, 
            "coins": db["users"][user_id_str]["coins"],
            "max_level": db["users"][user_id_str]["max_level"]
        })
        
    except Exception as e:
        logger.error(f"Error in update_score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров"""
    try:
        db = load_data()
        
        # Сортируем лидерборд по score (уровню), затем по coins
        leaderboard = sorted(
            db["leaderboard"],
            key=lambda x: (x["score"], x.get("coins", 0)),
            reverse=True
        )
        
        # Берем топ-20
        top_20 = leaderboard[:20]
        
        logger.info(f"Returning leaderboard with {len(top_20)} entries")
        
        return jsonify({
            "success": True, 
            "leaderboard": top_20,
            "total_players": len(db["users"])
        })
        
    except Exception as e:
        logger.error(f"Error in get_leaderboard: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def update_leaderboard(db, user_id, username, score):
    """Обновление лидерборда"""
    try:
        # Ищем пользователя в лидерборде
        user_found = False
        for entry in db["leaderboard"]:
            if entry["user_id"] == user_id:
                if score > entry["score"]:
                    entry["score"] = score
                # Обновляем username если нужно
                if username and username != entry.get("username"):
                    entry["username"] = username
                entry["updated_at"] = time.time()
                entry["coins"] = db["users"][user_id].get("coins", 0)
                user_found = True
                break
        
        if not user_found:
            db["leaderboard"].append({
                "user_id": user_id,
                "username": username or f"Player{str(user_id)[-4:]}",
                "score": score,
                "coins": db["users"][user_id].get("coins", 0),
                "updated_at": time.time()
            })
        
        # Сортируем лидерборд
        db["leaderboard"].sort(key=lambda x: (x["score"], x.get("coins", 0)), reverse=True)
        
        # Оставляем только топ-50
        if len(db["leaderboard"]) > 50:
            db["leaderboard"] = db["leaderboard"][:50]
            
        logger.info(f"Updated leaderboard for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in update_leaderboard: {e}")

# Telegram бот функции
def send_telegram_message(chat_id, text, keyboard=None):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    if keyboard:
        payload["reply_markup"] = keyboard
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def handle_telegram_update(update):
    """Обработка обновлений Telegram"""
    try:
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            user = message["from"]
            
            # Получаем отображаемое имя пользователя
            display_name = get_display_name(user)
            user_id_str = str(user["id"])
            
            logger.info(f"Telegram message from {user_id_str} ({display_name}): {text}")
            
            # Загружаем или создаем пользователя в базе
            db = load_data()
            
            if user_id_str not in db["users"]:
                # Регистрируем нового пользователя
                db["users"][user_id_str] = {
                    "username": display_name,
                    "coins": 100,  # Стартовый бонус
                    "max_level": 1,
                    "skins": ["default"],
                    "selected_skin": "default",
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "telegram_username": user.get("username"),
                    "created_at": time.time(),
                    "last_active": time.time()
                }
                
                # Добавляем в лидерборд
                db["leaderboard"].append({
                    "user_id": user_id_str,
                    "username": display_name,
                    "score": 1,
                    "coins": 100,
                    "updated_at": time.time()
                })
                
                save_data(db)
                logger.info(f"Registered new Telegram user: {user_id_str} - {display_name}")
            
            # Обработка команд
            if text == "/start":
                keyboard = {
                    "inline_keyboard": [[
                        {"text": "🎮 НАЧАТЬ ИГРУ", "web_app": {"url": GAME_URL}}
                    ]]
                }
                
                welcome_text = f"""
Привет, {user.get('first_name', 'Игрок')}! 👋

🎮 *Arrows Pro Ultra* - теперь с:
• Автоматическим сохранением прогресса
• Реальной таблицей лидеров
• Системой монет и скинов
• Ваш никнейм: *{display_name}*

*Начните играть прямо сейчас!* 🚀

🏆 *Ваш прогресс будет автоматически синхронизирован*
                """
                
                send_telegram_message(chat_id, welcome_text, keyboard)
            
            elif text == "/stats":
                # Получаем статистику пользователя
                if user_id_str in db["users"]:
                    user_data = db["users"][user_id_str]
                    
                    # Находим позицию в лидерборде
                    position = 1
                    sorted_leaderboard = sorted(
                        db["leaderboard"],
                        key=lambda x: (x["score"], x.get("coins", 0)),
                        reverse=True
                    )
                    
                    for entry in sorted_leaderboard:
                        if entry["user_id"] == user_id_str:
                            break
                        position += 1
                    
                    stats_text = f"""
📊 *ВАША СТАТИСТИКА:*

👤 *Никнейм:* {display_name}
🏆 *Уровень:* {user_data['max_level']}
💰 *Монеты:* {user_data['coins']} 🪙
🥇 *Место в рейтинге:* #{position}
🎨 *Скинов:* {len(user_data.get('skins', ['default']))}

*Играйте больше чтобы подняться выше!* 🚀
                    """
                    
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": "🎮 ПРОДОЛЖИТЬ ИГРУ", "web_app": {"url": GAME_URL}}
                        ]]
                    }
                    send_telegram_message(chat_id, stats_text, keyboard)
            
            elif text == "/leaderboard":
                db = load_data()
                
                if not db["leaderboard"]:
                    send_telegram_message(chat_id, "Таблица лидеров пока пуста. Будьте первым! 🏆")
                    return
                
                # Сортируем лидерборд
                sorted_lb = sorted(
                    db["leaderboard"],
                    key=lambda x: (x["score"], x.get("coins", 0)),
                    reverse=True
                )
                
                leader_text = "🏆 *ТОП-10 ИГРОКОВ:*\n\n"
                for i, entry in enumerate(sorted_lb[:10], 1):
                    medal = ""
                    if i == 1: medal = " 👑"
                    elif i == 2: medal = " 🥈"
                    elif i == 3: medal = " 🥉"
                    
                    leader_text += f"{i}. {entry['username']} - Уровень {entry['score']}{medal}\n"
                
                # Находим позицию текущего пользователя
                position = 1
                user_found = False
                for entry in sorted_lb:
                    if entry["user_id"] == user_id_str:
                        user_found = True
                        break
                    position += 1
                
                if user_found:
                    leader_text += f"\n*Ваше место:* #{position}"
                else:
                    leader_text += f"\n*Вы еще не в таблице лидеров*"
                
                keyboard = {
                    "inline_keyboard": [[
                        {"text": "🎮 ИГРАТЬ", "web_app": {"url": GAME_URL}}
                    ]]
                }
                
                send_telegram_message(chat_id, leader_text, keyboard)
                
    except Exception as e:
        logger.error(f"Error handling Telegram update: {e}")

def telegram_polling():
    """Поллинг Telegram бота"""
    offset = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result"):
                    for update in data["result"]:
                        offset = update["update_id"] + 1
                        handle_telegram_update(update)
            
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error in polling: {e}")
            time.sleep(5)

# Запуск Flask и Telegram бота
def run_flask():
    """Запуск Flask сервера"""
    try:
        # Для PythonAnywhere нужно использовать другой порт
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting Flask server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Error starting Flask: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🤖 ARROWS PRO ULTRA - БОТ С АВТОМАТИЧЕСКИМ НИКНЕЙМОМ")
    print("="*60)
    print(f"🎮 Игра: {GAME_URL}")
    print("📊 API: /api/")
    print("="*60)
    
    # Создаем файл данных если его нет
    if not os.path.exists(DATA_FILE):
        save_data({"users": {}, "leaderboard": [], "shop_items": initialize_shop()})
        print("✅ Создан файл данных")
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Даем Flask время на запуск
    time.sleep(2)
    
    # Запускаем Telegram бота
    print("🚀 Запуск Telegram бота...")
    print("🤖 Бот готов к работе!")
    print("="*60)
    
    try:
        telegram_polling()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")

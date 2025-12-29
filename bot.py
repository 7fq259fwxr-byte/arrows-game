#!/usr/bin/env python3
"""
Arrows Game Bot - Полная версия с API и игрой
Для развертывания на PythonAnywhere
"""

import os
import json
import time
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# ========== НАСТРОЙКИ ==========
app = Flask(__name__)
CORS(app)  # Разрешаем запросы со всех доменов

# Пути к файлам
BASE_DIR = os.path.expanduser('~')
DATA_FILE = os.path.join(BASE_DIR, 'arrows_data.json')
LOG_FILE = os.path.join(BASE_DIR, 'arrows_log.txt')

# Токен бота Telegram (замените на свой)
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"

# ========== ФУНКЦИИ ДЛЯ ДАННЫХ ==========

def log_message(msg):
    """Логирование сообщений"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {msg}\n")
        print(f"📝 {msg}")
    except:
        print(f"❌ Ошибка логирования: {msg}")

def load_data():
    """Загрузка данных из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                user_count = len(data.get('users', {}))
                log_message(f"Данные загружены: {user_count} пользователей")
                return data
        log_message("Файл данных не найден, создаю новый")
        return {
            "users": {},
            "leaderboard": [],
            "shop_items": {
                "arrow_skins": [
                    {"id": "default", "name": "Классический", "price": 0},
                    {"id": "fire", "name": "Огненный", "price": 100},
                    {"id": "ice", "name": "Ледяной", "price": 150},
                    {"id": "gold", "name": "Золотой", "price": 300},
                    {"id": "neon", "name": "Неоновый", "price": 200},
                    {"id": "rainbow", "name": "Радужный", "price": 500}
                ]
            }
        }
    except Exception as e:
        log_message(f"Ошибка загрузки данных: {e}")
        return {"users": {}, "leaderboard": []}

def save_data(data):
    """Сохранение данных в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log_message("Данные сохранены")
        return True
    except Exception as e:
        log_message(f"Ошибка сохранения данных: {e}")
        return False

def get_display_name(user_info):
    """Получение отображаемого имени пользователя"""
    username = user_info.get('username')
    first_name = user_info.get('first_name', '')
    last_name = user_info.get('last_name', '')
    user_id = user_info.get('user_id', '0000')
    
    if username:
        return f"@{username}"
    elif first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        return f"Player{str(user_id)[-4:]}"

def update_leaderboard(db, user_id, username, level, coins):
    """Обновление таблицы лидеров"""
    user_id_str = str(user_id)
    
    # Ищем пользователя в лидерборде
    user_found = False
    for entry in db["leaderboard"]:
        if entry["user_id"] == user_id_str:
            if level > entry["score"]:
                entry["score"] = level
            entry["username"] = username
            entry["coins"] = coins
            entry["updated_at"] = time.time()
            user_found = True
            break
    
    if not user_found:
        db["leaderboard"].append({
            "user_id": user_id_str,
            "username": username,
            "score": level,
            "coins": coins,
            "updated_at": time.time()
        })
    
    # Сортируем по уровню (по убыванию)
    db["leaderboard"].sort(key=lambda x: x["score"], reverse=True)
    
    # Оставляем топ-50
    if len(db["leaderboard"]) > 50:
        db["leaderboard"] = db["leaderboard"][:50]
    
    return db

# ========== API ЭНДПОИНТЫ ==========

@app.route('/')
def index():
    """Главная страница с игрой"""
    log_message("Запрос главной страницы")
    try:
        return render_template('index.html')
    except:
        # Если нет шаблона, возвращаем простую страницу
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Arrows Pro Ultra</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #f4f6f9; }
                .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
                h1 { color: #003366; }
                .btn { display: inline-block; padding: 15px 30px; background: #003366; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 10px; }
                .telegram-btn { background: #0088cc; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎮 Arrows Pro Ultra</h1>
                <p>Игра в стрелки с системой монет и лидербордом</p>
                <p>Для полного доступа запустите игру через Telegram бота</p>
                
                <h3>🚀 Быстрый старт:</h3>
                <a href="https://t.me/arrows_pro_bot" class="btn telegram-btn" target="_blank">📱 Открыть в Telegram</a>
                <a href="/play" class="btn">🎮 Играть в браузере</a>
                
                <h3 style="margin-top: 30px;">📊 Статистика сервера:</h3>
                <p><a href="/api/stats">Просмотр статистики</a></p>
                <p><a href="/api/leaderboard">Таблица лидеров</a></p>
            </div>
        </body>
        </html>
        """

@app.route('/play')
def play():
    """Страница игры"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arrows Game</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; padding: 0; overflow: hidden; background: #f4f6f9; }
            #game-frame { width: 100vw; height: 100vh; border: none; }
        </style>
    </head>
    <body>
        <iframe id="game-frame" src="https://7fq259fwxr-byte.github.io/arrows-game/" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
        </iframe>
        <script>
            // Автоматический ресайз iframe
            function resizeIframe() {
                const iframe = document.getElementById('game-frame');
                iframe.style.width = window.innerWidth + 'px';
                iframe.style.height = window.innerHeight + 'px';
            }
            window.addEventListener('resize', resizeIframe);
            resizeIframe();
        </script>
    </body>
    </html>
    """

@app.route('/api/get_user', methods=['POST', 'GET'])
def get_user():
    """Получить или создать пользователя"""
    log_message("Запрос get_user")
    
    try:
        if request.method == 'GET':
            # Для тестирования через браузер
            test_user = {
                "user_id": 123456,
                "username": "TestPlayer",
                "coins": 100,
                "level": 1,
                "skins": ["default"]
            }
            return jsonify({"success": True, "user": test_user, "message": "Тестовый режим"})
        
        # Получаем данные из запроса
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Нет данных"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if not user_id:
            return jsonify({"success": False, "error": "Нет user_id"}), 400
        
        # Создаем имя пользователя
        user_info = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        display_name = get_display_name(user_info)
        
        db = load_data()
        user_id_str = str(user_id)
        
        if user_id_str in db["users"]:
            # Пользователь уже существует
            user = db["users"][user_id_str]
            log_message(f"Пользователь найден: {user['username']}")
            
            # Обновляем имя если изменилось
            if display_name != user.get("username"):
                user["username"] = display_name
                save_data(db)
            
            response = {
                "success": True,
                "user": {
                    "id": user_id_str,
                    "username": user["username"],
                    "coins": user.get("coins", 0),
                    "level": user.get("max_level", 1),
                    "skins": user.get("skins", ["default"]),
                    "selected_skin": user.get("selected_skin", "default"),
                    "created_at": user.get("created_at", time.time())
                }
            }
        else:
            # Создаем нового пользователя
            log_message(f"Создаю нового пользователя: {display_name}")
            
            new_user = {
                "username": display_name,
                "coins": 100,  # Стартовый бонус
                "max_level": 1,
                "skins": ["default"],
                "selected_skin": "default",
                "created_at": time.time(),
                "last_active": time.time()
            }
            
            db["users"][user_id_str] = new_user
            
            # Добавляем в лидерборд
            db = update_leaderboard(db, user_id, display_name, 1, 100)
            save_data(db)
            
            response = {
                "success": True,
                "user": {
                    "id": user_id_str,
                    "username": display_name,
                    "coins": 100,
                    "level": 1,
                    "skins": ["default"],
                    "selected_skin": "default",
                    "created_at": time.time()
                },
                "message": "Новый пользователь создан"
            }
        
        return jsonify(response)
        
    except Exception as e:
        log_message(f"Ошибка в get_user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update_score', methods=['POST'])
def update_score():
    """Обновить счет пользователя"""
    log_message("Запрос update_score")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Нет данных"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username', 'Player')
        level = data.get('level', 1)
        coins_earned = data.get('coins_earned', 20)
        
        if not user_id:
            return jsonify({"success": False, "error": "Нет user_id"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        if user_id_str not in db["users"]:
            # Создаем пользователя если его нет
            db["users"][user_id_str] = {
                "username": username,
                "coins": coins_earned,
                "max_level": level,
                "skins": ["default"],
                "selected_skin": "default",
                "created_at": time.time(),
                "last_active": time.time()
            }
            log_message(f"Автосоздание пользователя: {username}")
        else:
            # Обновляем существующего пользователя
            user = db["users"][user_id_str]
            user["coins"] = user.get("coins", 0) + coins_earned
            
            if level > user.get("max_level", 1):
                user["max_level"] = level
            
            if username and username != user.get("username"):
                user["username"] = username
            
            user["last_active"] = time.time()
            log_message(f"Обновлен пользователь: {user['username']}, монеты: {user['coins']}, уровень: {user['max_level']}")
        
        # Обновляем лидерборд
        db = update_leaderboard(db, user_id, 
                               username or db["users"][user_id_str]["username"],
                               db["users"][user_id_str]["max_level"],
                               db["users"][user_id_str]["coins"])
        
        save_data(db)
        
        return jsonify({
            "success": True,
            "coins": db["users"][user_id_str]["coins"],
            "level": db["users"][user_id_str]["max_level"],
            "username": db["users"][user_id_str]["username"]
        })
        
    except Exception as e:
        log_message(f"Ошибка в update_score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получить таблицу лидеров"""
    log_message("Запрос leaderboard")
    
    try:
        db = load_data()
        
        # Сортируем и берем топ-20
        leaderboard = sorted(
            db.get("leaderboard", []),
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:20]
        
        # Добавляем ранги
        for i, player in enumerate(leaderboard):
            player["rank"] = i + 1
        
        return jsonify({
            "success": True,
            "leaderboard": leaderboard,
            "total_players": len(db.get("users", {})),
            "updated_at": time.time()
        })
        
    except Exception as e:
        log_message(f"Ошибка в leaderboard: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получить статистику сервера"""
    db = load_data()
    
    stats = {
        "total_players": len(db.get("users", {})),
        "total_games": sum(1 for user in db.get("users", {}).values() if user.get("max_level", 0) > 1),
        "total_coins": sum(user.get("coins", 0) for user in db.get("users", {}).values()),
        "server_uptime": int(time.time() - os.path.getctime(DATA_FILE)) if os.path.exists(DATA_FILE) else 0,
        "active_today": sum(1 for user in db.get("users", {}).values() 
                           if time.time() - user.get("last_active", 0) < 86400)
    }
    
    return jsonify({
        "success": True,
        "stats": stats,
        "timestamp": time.time()
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    """Тестовый эндпоинт"""
    return jsonify({
        "success": True,
        "message": "API работает нормально!",
        "server_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "version": "1.0.0",
        "endpoints": [
            "/api/get_user - Получить данные пользователя (POST)",
            "/api/update_score - Обновить счет (POST)",
            "/api/leaderboard - Таблица лидеров (GET)",
            "/api/stats - Статистика сервера (GET)",
            "/api/test - Тестовый эндпоинт (GET)"
        ]
    })

# ========== ЗАПУСК СЕРВЕРА ==========

if __name__ == '__main__':
    log_message("=" * 50)
    log_message("🚀 Запуск Arrows Game Bot")
    log_message(f"📁 Данные: {DATA_FILE}")
    log_message(f"📝 Логи: {LOG_FILE}")
    log_message("=" * 50)
    
    # Создаем начальные файлы если их нет
    if not os.path.exists(DATA_FILE):
        initial_data = load_data()  # Это создаст начальную структуру
        save_data(initial_data)
    
    print("\n" + "="*60)
    print("🎮 ARROWS PRO ULTRA - БОТ И API СЕРВЕР")
    print("="*60)
    print(f"🌐 Веб-сайт: https://7fq259fwxr.pythonanywhere.com/")
    print(f"🎮 Игра: https://7fq259fwxr-byte.github.io/arrows-game/")
    print(f"📊 API: https://7fq259fwxr.pythonanywhere.com/api/test")
    print("="*60)
    print("✅ Сервер готов к работе!")
    print("\nДля остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    # Запускаем Flask (на PythonAnywhere это сделает WSGI)
    app.run(debug=False)

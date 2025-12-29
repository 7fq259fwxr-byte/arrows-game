import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# Создаем приложение
app = Flask(__name__)
CORS(app)  # Разрешаем запросы отовсюду

print("✅ Flask приложение создано")

# Путь к файлу данных
DATA_FILE = os.path.join(os.path.expanduser('~'), 'users_data.json')
print(f"📁 Файл данных: {DATA_FILE}")

def load_data():
    """Загрузка данных из файла"""
    try:
        if os.path.exists(DATA_FILE):
            print("📂 Загружаю данные из файла...")
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Данные загружены: {len(data.get('users', {}))} пользователей")
                return data
        print("📂 Файла данных нет, создаю новый")
        return {"users": {}, "leaderboard": []}
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return {"users": {}, "leaderboard": []}

def save_data(data):
    """Сохранение данных в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 Данные сохранены")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

@app.route('/')
def home():
    print("🏠 Кто-то зашел на главную страницу")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arrows Game API</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f4f6f9;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            h1 {
                color: #003366;
                text-align: center;
            }
            .status {
                color: green;
                font-weight: bold;
                text-align: center;
                font-size: 1.2em;
            }
            .endpoints {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
            }
            code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Arrows Game API Server</h1>
            <p class="status">✅ Сервер работает нормально</p>
            <p>Это API сервер для игры Arrows Pro Ultra.</p>
            
            <div class="endpoints">
                <h3>📡 Доступные эндпоинты:</h3>
                <ul>
                    <li><code>POST /api/get_user_data</code> - Получить данные пользователя</li>
                    <li><code>POST /api/update_score</code> - Обновить счет</li>
                    <li><code>GET /api/leaderboard</code> - Получить таблицу лидеров</li>
                </ul>
            </div>
            
            <p style="margin-top: 30px; text-align: center; color: #666;">
                Игра доступна по адресу: 
                <a href="https://7fq259fwxr-byte.github.io/arrows-game/" target="_blank">
                    https://7fq259fwxr-byte.github.io/arrows-game/
                </a>
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/api/get_user_data', methods=['POST'])
def get_user_data():
    print("📥 Получен запрос get_user_data")
    try:
        # Разрешаем запросы отовсюду
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Нет данных"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username', 'Player')
        
        print(f"👤 User ID: {user_id}, Username: {username}")
        
        if not user_id:
            return jsonify({"success": False, "error": "Нужен user_id"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        if user_id_str in db["users"]:
            user_data = db["users"][user_id_str]
            print(f"✅ Пользователь найден: {user_data.get('username')}")
            
            return jsonify({
                "success": True,
                "coins": user_data.get("coins", 0),
                "max_level": user_data.get("max_level", 1),
                "username": user_data.get("username", username),
                "skins": user_data.get("skins", ["default"]),
                "selected_skin": user_data.get("selected_skin", "default")
            })
        
        # Создаем нового пользователя
        print(f"🆕 Создаю нового пользователя: {username}")
        db["users"][user_id_str] = {
            "username": username,
            "coins": 100,
            "max_level": 1,
            "skins": ["default"],
            "selected_skin": "default",
            "created_at": time.time()
        }
        
        db["leaderboard"].append({
            "user_id": user_id_str,
            "username": username,
            "score": 1,
            "coins": 100,
            "updated_at": time.time()
        })
        
        save_data(db)
        
        return jsonify({
            "success": True,
            "coins": 100,
            "max_level": 1,
            "username": username,
            "skins": ["default"],
            "selected_skin": "default",
            "message": "Новый пользователь создан"
        })
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    """Тестовый эндпоинт для проверки"""
    print("🧪 Тестовый запрос получен")
    return jsonify({
        "success": True,
        "message": "API работает!",
        "timestamp": time.time(),
        "data_file": DATA_FILE,
        "file_exists": os.path.exists(DATA_FILE)
    })

if __name__ == '__main__':
    print("🚀 Запуск сервера...")
    app.run(debug=True)

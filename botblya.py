import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с GitHub Pages

# Путь к файлу данных
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users_data.json')

def load_data():
    """Загрузка данных из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"users": {}, "leaderboard": []}
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"users": {}, "leaderboard": []}

def save_data(data):
    """Сохранение данных в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

@app.route('/')
def index():
    return "Arrows Game API Server is running!"

@app.route('/api/get_user_data', methods=['POST'])
def get_user_data():
    """Получение данных пользователя"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username', 'Player')
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        print(f"Getting user data for ID: {user_id_str}, username: {username}")
        
        if user_id_str in db["users"]:
            user_data = db["users"][user_id_str]
            
            # Обновляем username если нужно
            if username != user_data.get("username", "Player"):
                user_data["username"] = username
                save_data(db)
            
            return jsonify({
                "success": True,
                "coins": user_data.get("coins", 0),
                "max_level": user_data.get("max_level", 1),
                "username": user_data.get("username", username),
                "skins": user_data.get("skins", ["default"]),
                "selected_skin": user_data.get("selected_skin", "default")
            })
        
        # Создаем нового пользователя
        print(f"Creating new user: {user_id_str} - {username}")
        db["users"][user_id_str] = {
            "username": username,
            "coins": 100,
            "max_level": 1,
            "skins": ["default"],
            "selected_skin": "default",
            "created_at": time.time(),
            "last_active": time.time()
        }
        
        # Добавляем в лидерборд
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
            "selected_skin": "default"
        })
        
    except Exception as e:
        print(f"Error in get_user_data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update_score', methods=['POST'])
def update_score():
    """Обновление счета пользователя"""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        username = data.get('username', 'Player')
        new_level = data.get('level', 1)
        coins_earned = data.get('coins_earned', 20)
        
        if not user_id:
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        db = load_data()
        user_id_str = str(user_id)
        
        print(f"Updating score for user {user_id_str}: level={new_level}, coins={coins_earned}")
        
        if user_id_str not in db["users"]:
            # Создаем нового пользователя
            db["users"][user_id_str] = {
                "username": username,
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
                "username": username,
                "score": new_level,
                "coins": coins_earned,
                "updated_at": time.time()
            })
            
            print(f"Auto-created user {user_id_str}")
        else:
            user = db["users"][user_id_str]
            user["coins"] = user.get("coins", 0) + coins_earned
            
            if new_level > user.get("max_level", 1):
                user["max_level"] = new_level
            
            if username != user.get("username", "Player"):
                user["username"] = username
            
            user["last_active"] = time.time()
        
        # Обновляем лидерборд
        update_leaderboard(db, user_id_str, username, db["users"][user_id_str]["max_level"])
        
        save_data(db)
        
        return jsonify({
            "success": True, 
            "coins": db["users"][user_id_str]["coins"],
            "max_level": db["users"][user_id_str]["max_level"]
        })
        
    except Exception as e:
        print(f"Error in update_score: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Получение таблицы лидеров"""
    try:
        db = load_data()
        
        # Сортируем по score (уровню)
        leaderboard = sorted(
            db["leaderboard"],
            key=lambda x: x["score"],
            reverse=True
        )[:20]
        
        print(f"Returning leaderboard with {len(leaderboard)} entries")
        
        return jsonify({
            "success": True, 
            "leaderboard": leaderboard
        })
        
    except Exception as e:
        print(f"Error in get_leaderboard: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def update_leaderboard(db, user_id, username, score):
    """Обновление лидерборда"""
    # Ищем пользователя в лидерборде
    for entry in db["leaderboard"]:
        if entry["user_id"] == user_id:
            if score > entry["score"]:
                entry["score"] = score
            entry["username"] = username
            entry["updated_at"] = time.time()
            entry["coins"] = db["users"][user_id].get("coins", 0)
            break
    else:
        # Если не нашли - добавляем
        db["leaderboard"].append({
            "user_id": user_id,
            "username": username,
            "score": score,
            "coins": db["users"][user_id].get("coins", 0),
            "updated_at": time.time()
        })
    
    # Сортируем
    db["leaderboard"].sort(key=lambda x: x["score"], reverse=True)
    
    # Оставляем топ-50
    if len(db["leaderboard"]) > 50:
        db["leaderboard"] = db["leaderboard"][:50]

if __name__ == '__main__':
    app.run(debug=True)

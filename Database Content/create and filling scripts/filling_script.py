import psycopg2
import json
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    "dbname": "kiwidb",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def clear_database(cur):
    cur.execute("""
        TRUNCATE TABLE 
            tasks, versions, slides, chats, jsons, csvs, users, metrics 
        RESTART IDENTITY CASCADE;
    """)

def populate_database():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        clear_database(cur)
        
        user_ids = []
        for i in range(5):
            departments = [
                "Отдел продаж", "Отдел планирования", "Отдел приколов", "Отдел плоскогубцев",
                "Отдел отделов"
            ]
            cur.execute("INSERT INTO users (department) VALUES (%s) RETURNING userID;", (departments[i],))
            user_ids.append(cur.fetchone()[0])
        
        csv_ids = []
        for i in range(5):
            content = f"id,name,value\n{i},Item_{i},{i*100}".encode('utf-8')
            cur.execute("INSERT INTO csvs (file) VALUES (%s) RETURNING csvID;", (content,))
            csv_ids.append(cur.fetchone()[0])

        json_ids = []
        for i in range(5):
            data = {"theme": "dark" if i%2==0 else "light", "index": i, "active": True}
            cur.execute("INSERT INTO jsons (file) VALUES (%s) RETURNING jsonID;", (json.dumps(data),))
            json_ids.append(cur.fetchone()[0])

        metric_ids = []
        for name in ["Accuracy", "F1-Score", "Precision", "Recall"]:
            cur.execute("INSERT INTO metrics (name) VALUES (%s) RETURNING metricID;", (name,))
            metric_ids.append(cur.fetchone()[0])
      
        chat_ids = []
        chat_titles = [
            "Анализ продаж Q1", "Отчет по маркетингу", 
            "Финансовые показатели", "HR метрики", "Прогноз на год"
        ]
        
        for i in range(5):
            cur.execute("""
                INSERT INTO chats (userID, csvID, jsonID, title, prompt) 
                VALUES (%s, %s, %s, %s, %s) RETURNING chatID;
            """, (
                user_ids[i % len(user_ids)], 
                csv_ids[i % len(csv_ids)], 
                json_ids[i % len(json_ids)], 
                chat_titles[i], 
                f"Сгенерируй презентацию для {chat_titles[i].lower()}"
            ))
            chat_ids.append(cur.fetchone()[0])

        slides_data = []
        for chat_id in chat_ids:
            for num in range(1, 7):
                metric_id = random.choice(metric_ids)
                
                cur.execute("""
                    INSERT INTO slides (chatID, metricID, num) 
                    VALUES (%s, %s, %s) RETURNING slideID;
                """, (chat_id, metric_id, num))
                
                slide_id = cur.fetchone()[0]
                slides_data.append((slide_id, chat_id))
       
        versions_data = [] 
        base_time = datetime.now()
        
        for slide_id, chat_id in slides_data:
            num_drafts = random.randint(3, 5)
            for v in range(num_drafts):
                json_data = {"iteration": v + 1, "status": "draft",
                             "changes": f"Правка {v+1}"}
                created = base_time + timedelta(minutes=v * 10)
                cur.execute("""
                    INSERT INTO versions (slideID, json, prompt, created_at, is_final)
                    VALUES (%s, %s, %s, %s, %s) RETURNING versionID;
                """, (slide_id, json.dumps(json_data),
                      f"Что-то сделать", created, False))
                ver_id = cur.fetchone()[0]
                versions_data.append((ver_id, chat_id))
                
            # ровно 1 final ver    
            final_json = {"status": "final", "approved": True, "version": "1.0"}
            cur.execute("""
                INSERT INTO versions (slideID, json, prompt, is_final) 
                VALUES (%s, %s, %s, %s) RETURNING versionID;
            """, (slide_id, json.dumps(final_json), "Заменить график на гистограмму", True))
            
            final_ver_id = cur.fetchone()[0]
            versions_data.append((final_ver_id, chat_id))

        
        versions_by_chat = {}
        for ver_id, chat_id in versions_data:
            versions_by_chat.setdefault(chat_id, []).append(ver_id)
            
        for chat_id in chat_ids:
            chat_versions = versions_by_chat[chat_id]
            
            # Выбираем ровно ОДНУ версию для создания единственной задачи
            selected_version = random.choice(chat_versions) 
            
            status = random.randint(0, 2)
            task_type = random.randint(1, 3)
            
            cur.execute("""
                INSERT INTO tasks (chatID, versionID, type, prompt, status) 
                VALUES (%s, %s, %s, %s, %s);
            """, (chat_id, selected_version, task_type, f"Обработать версию {selected_version} для чата {chat_id}", status))

        conn.commit()

    except psycopg2.Error as e:
        print(f"\nОшибка: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"\nОшибка: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    populate_database()
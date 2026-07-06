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
            tasks, versions, slides, chats, jsons, csvs, users 
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
                cur.execute("""
                    INSERT INTO slides (chatID, num) 
                    VALUES (%s, %s) RETURNING slideID;
                """, (chat_id, num))
                
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
            
            num_tasks = random.randint(2, 5)
            
            for i in range(num_tasks):
                status = random.randint(0, 3)
                task_type = random.randint(0, 2)
                
                if random.random() < 0.3:
                    ver_id = None
                    prompt_text = f"Задача для чата {chat_id}"
                else:
                    ver_id = random.choice(chat_versions)
                    prompt_text = f"Обработать версию {ver_id} для чата {chat_id}"

                if status == 3:
                    error_message = f"Провал"
                else:
                    error_message = None

                cur.execute("""
                    INSERT INTO tasks (chatID, versionID, type, prompt, status, error_message) 
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (chat_id, ver_id, task_type, prompt_text, status, error_message))

                

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
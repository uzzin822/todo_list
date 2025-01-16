from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# MySQL 연결 설정
db_config = {
    'host': '10.0.66.14',
    'user': 'sejong',
    'password': '1234',
    'database': 'todo_db'
}

# 데이터베이스 연결 함수
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 테이블 생성 쿼리 (due_date 필드 추가)
create_table_query = """
CREATE TABLE IF NOT EXISTS todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# 테이블 생성
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()
except Exception as e:
    print(f"Error creating table: {e}")
finally:
    cursor.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# CREATE - 할일 추가
@app.route('/api/todos', methods=['POST'])
def add_todo():
    title = request.json.get('title')
    due_date = request.json.get('due_date')
    
    if not title:
        return jsonify({'error': '제목은 필수입니다'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (title, due_date) VALUES (%s, %s)", (title, due_date))
        conn.commit()
        todo_id = cursor.lastrowid
        
        return jsonify({
            'id': todo_id,
            'title': title,
            'completed': False,
            'due_date': due_date,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# READ - 할일 목록 조회
@app.route('/api/todos', methods=['GET'])
def get_todos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT *, DATE_FORMAT(due_date, '%Y-%m-%d') as due_date_formatted FROM todos ORDER BY due_date ASC, created_at DESC")
        todos = cursor.fetchall()
        return jsonify(todos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# UPDATE - 할일 상태 변경
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    completed = request.json.get('completed')
    title = request.json.get('title')
    due_date = request.json.get('due_date')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        update_values = []
        
        if title is not None:
            update_fields.append("title = %s")
            update_values.append(title)
        if completed is not None:
            update_fields.append("completed = %s")
            update_values.append(completed)
        if due_date is not None:
            update_fields.append("due_date = %s")
            update_values.append(due_date)
            
        if update_fields:
            query = "UPDATE todos SET " + ", ".join(update_fields) + " WHERE id = %s"
            update_values.append(todo_id)
            cursor.execute(query, tuple(update_values))
            conn.commit()
        
        return jsonify({'message': '업데이트 성공'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# DELETE - 할일 삭제
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        conn.commit()
        return jsonify({'message': '삭제 성공'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5002,debug=True)
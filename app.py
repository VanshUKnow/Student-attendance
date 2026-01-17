from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root1234'
app.config['MYSQL_DB'] = 'student_attendance'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM students ORDER BY roll_number")
        students = cursor.fetchall()
        cursor.close()
        return jsonify(students)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    try:
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO students (name, roll_number) VALUES (%s, %s)", 
                      (data['name'], data['roll_number']))
        mysql.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return jsonify({'id': new_id, 'message': 'Student added'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.json
        date = data['date']
        present_ids = set(data['present_ids']) 
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT id FROM students")
        all_students = cursor.fetchall()
        
        for student in all_students:
            s_id = student['id']
            is_present = 1 if s_id in present_ids else 0
            
            cursor.execute("""
                INSERT INTO attendance (student_id, attendance_date, is_present)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE is_present = %s
            """, (s_id, date, is_present, is_present))
            
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Attendance saved'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/<date>', methods=['GET'])
def get_attendance(date):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
            SELECT s.id, s.name, s.roll_number, a.is_present 
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id AND a.attendance_date = %s
            ORDER BY s.roll_number
        """
        cursor.execute(query, (date,))
        records = cursor.fetchall()
        cursor.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

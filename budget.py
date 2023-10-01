from flask import Flask, request, jsonify, send_file
import sqlite3
from flask_cors import CORS
from PIL import Image
import io
import os
from io import BytesIO

app = Flask(__name__)
CORS(app)
CORS(app, origins=["http://127.0.0.1:8050", "https://api3.datadude.dev"])

def create_table():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                 serial_number TEXT,
                 date TEXT,
                 amount REAL,
                 company_name TEXT,
                 location TEXT,
                 description TEXT,
                 payment_type TEXT,
                 photo BLOB)''')
    conn.commit()
    conn.close()

def generate_serial_number():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM expenses")
    count = c.fetchone()[0]
    serial_number = f"EX{count + 1:07d}"
    conn.close()
    return serial_number

@app.route('/api/v1/add_expense', methods=['POST'])
def add_expense():
    if request.content_type == 'application/json':
        data = request.json
        serial_number = generate_serial_number()
        date = data.get('date')
        amount = data.get('amount')
        company_name = data.get('company_name')
        location = data.get('location')
        description = data.get('description')
        payment_type = data.get('payment_type')
        photo = None
    elif request.content_type.startswith('multipart/form-data'):
        data = request.form.to_dict()
        serial_number = generate_serial_number()
        date = data.get('date')
        amount = data.get('amount')
        company_name = data.get('company_name')
        location = data.get('location')
        description = data.get('description')
        payment_type = data.get('payment_type')
        photo = request.files.get('photo')
        if photo:
            photo = photo.read()
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415

    if payment_type not in ['CC', 'BT', 'WT', 'ET', 'CA']:
        return jsonify({'error': 'Invalid payment type'}), 400

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (serial_number, date, amount, company_name, location, description, payment_type, photo))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Expense with serial number {serial_number} has been added.'})

@app.route('/api/v1/list_expenses', methods=['GET'])
def list_expenses():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM expenses ORDER BY date DESC, amount, company_name, location, description, payment_type")
    
    expenses = []
    for row in c.fetchall():
        expenses.append({
            'SerialNumber': row[0],
            'Date': row[1],
            'Amount': f"${row[2]:.2f}",
            'Company': row[3],
            'Location': row[4],
            'Description': row[5],
            'Pay Type': row[6],
            'PhotoExists': bool(row[7])  # Assuming the 8th column is the photo
        })
        
    conn.close()
    return jsonify(expenses)


@app.route('/api/v1/calculate_total', methods=['GET'])
def calculate_total():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses")
    
    total_amount = c.fetchone()[0]
    if total_amount is None:
        total_amount = 0.0
    
    conn.close()
    return jsonify({'Total Amount to be Reimbursed': f"${total_amount:.2f}"})

@app.route('/api/v1/remove_expense', methods=['POST'])
def remove_expense():
    data = request.json
    serial_number = data.get('serial_number')
    
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE serial_number = ?", (serial_number,))
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({'error': f'No expense found with serial number {serial_number}'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': f'Expense with serial number {serial_number} has been removed.'})

@app.route('/api/v1/get_photo/<serial_number>', methods=['GET'])
def get_photo(serial_number):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT photo FROM expenses WHERE serial_number = ?", (serial_number,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return send_file(row[0], as_attachment=True, download_name=f"{serial_number}.png", mimetype='image/png')
    else:
        return jsonify({'error': 'Photo not found'}), 404


if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0', port=5050)

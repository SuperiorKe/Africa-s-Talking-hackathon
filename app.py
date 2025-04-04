from flask import Flask, request, jsonify, send_from_directory
import os
from dotenv import load_dotenv
from supabase import create_client, Client

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# API Routes
@app.route('/api/records', methods=['GET'])
def get_records():
    try:
        response = supabase.table('tasks').select('*').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<id>', methods=['GET'])
def get_record(id):
    try:
        response = supabase.table('tasks').select('*').eq('id', id).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/records', methods=['POST'])
def create_record():
    try:
        data = request.json
        if not all(k in data for k in ['title', 'completed', 'created_at']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        task_data = {
            'title': data.get('title'),
            'completed': data.get('completed'),
            'created_at': data.get('created_at'),
            'user_id': 'abb6bcb5-436d-4a2d-90be-da08e2c6cfcb'
        }
        response = supabase.table('tasks').insert(task_data).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<id>', methods=['PUT'])
def update_record(id):
    try:
        data = request.json
        if not any(k in data for k in ['title', 'completed', 'created_at']):
            return jsonify({'error': 'No fields to update'}), 400
            
        task_data = {}
        if 'title' in data:
            task_data['title'] = data.get('title')
            if 'completed' in data:
                task_data['completed'] = data.get('completed')
        if 'created_at' in data:
            task_data['created_at'] = data.get('created_at')
            
        response = supabase.table('tasks').update(task_data).eq('id', id).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<id>', methods=['DELETE'])
def delete_record(id):
    try:
        # Fixed: Changed 'users' to 'tasks'
        response = supabase.table('tasks').delete().eq('id', id).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

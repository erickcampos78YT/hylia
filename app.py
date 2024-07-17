from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Verifica se os diretórios necessários existem e os cria se não existirem
os.makedirs('static/data/fotos', exist_ok=True)

if not os.path.exists('users.json'):
    with open('users.json', 'w') as f:
        json.dump([], f)
if not os.path.exists('messages.json'):
    with open('messages.json', 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    with open('messages.json', 'r') as f:
        messages = json.load(f)
        
    return render_template('index.html', user=session['user'], messages=messages)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        photo = request.files['photo']
        photo_path = os.path.join('static', 'data', 'fotos', photo.filename)
        photo.save(photo_path)
        
        user = {
            'name': name,
            'email': email,
            'password': password,
            'age': age,
            'photo': photo.filename,
            'banner': ''
        }
        
        with open('users.json', 'r') as f:
            users = json.load(f)
            
        users.append(user)
        
        with open('users.json', 'w') as f:
            json.dump(users, f)
        
        session['user'] = user
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = user
                return redirect(url_for('index'))
                
        return 'Invalid credentials'
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/messages', methods=['POST'])
def messages():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    message = request.form['message']
    image = request.files.get('image')
    image_filename = None
    
    if image:
        image_filename = image.filename
        image_path = os.path.join('static', 'data', 'fotos', image_filename)
        image.save(image_path)
    
    new_message = {
        'username': session['user']['name'],
        'message': message,
        'photo': session['user']['photo'],
        'image': image_filename
    }
    
    with open('messages.json', 'r') as f:
        messages = json.load(f)
    
    messages.append(new_message)
    
    with open('messages.json', 'w') as f:
        json.dump(messages, f)
    
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    user = next((user for user in users if user['name'] == username), None)
    
    if user is None:
        return 'User not found'
    
    with open('messages.json', 'r') as f:
        messages = json.load(f)
    
    user_messages = [message for message in messages if message['username'] == username]
    
    return render_template('profile.html', user=user, messages=user_messages)

@app.route('/customize', methods=['GET', 'POST'])
def customize():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        banner = request.files['banner']
        banner_path = os.path.join('static', 'data', 'fotos', banner.filename)
        banner.save(banner_path)
        
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['email'] == session['user']['email']:
                user['banner'] = banner.filename
                session['user']['banner'] = banner.filename
                break
        
        with open('users.json', 'w') as f:
            json.dump(users, f)
        
        return redirect(url_for('profile', username=session['user']['name']))
    
    return render_template('customize.html')

if __name__ == '__main__':
    app.run(debug=True)

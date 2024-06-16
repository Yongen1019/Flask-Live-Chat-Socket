from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

def create_app():
    # create a flask instance
    app = Flask(__name__)
    # secret key
    app.config['SECRET_KEY'] = 'fdsi12fer32f28h6sgfw2gt75'
    socketio = SocketIO(app)

    rooms = {}

    def generate_unique_code(length):
        while True:
            code = ''
            for i in range(length):
                code += random.choice(ascii_uppercase)

            if code not in rooms:
                break

        return code

    @app.route('/', methods=['GET', 'POST'])
    def home():
        # user cant get back the room using url after navigate to home page
        session.clear()
        if request.method == 'POST':
            name = request.form.get('name')
            code = request.form.get('code')
            # set default value as False if not receive join and create
            join = request.form.get('join', False)
            create = request.form.get('create', False)

            if not name:
                context = {
                    'error': 'Please enter a name', 
                    'code': code,
                    'name': name
                }
                return render_template('home.html', **context)
            
            if join != False and not code:
                context = {
                    'error': 'Please enter a room code', 
                    'code': code,
                    'name': name
                }
                return render_template('home.html', **context)
            
            room = code
            if create != False:
                room = generate_unique_code(4)
                rooms[room] = {'members': 0, 'messages': []}
            elif code not in rooms:
                context = {
                    'error': 'Room does not exist', 
                    'code': code,
                    'name': name
                }
                return render_template('home.html', **context)
            
            session['room'] = room
            session['name'] = name
            return redirect(url_for('room'))

        return render_template('home.html')
    
    @app.route('/room')
    def room():
        room = session.get('room')
        if room is None or session.get('name') is None or room not in rooms:
            return redirect(url_for('home'))
        
        context = {
            'room': room,
            'messages': rooms[room]['messages']
        }
        return render_template('room.html', **context)
    
    @socketio.on('connect')
    def connect(auth):
        room = session.get('room')
        name = session.get('name')
        if not room or not name:
            return
        if room not in rooms:
            leave_room(room)
            return 
        
        join_room(room)
        # send new member joined to specific room
        send({'name': name, 'message': 'has entered the room'}, to=room)
        rooms[room]['members'] += 1

    @socketio.on('message')
    def message(data):
        room = session.get('room')
        if room not in rooms:
            return
        
        content = {
            'name': session.get('name'),
            'message': data['data']
        }
        send(content, to=room)
        rooms[room]['messages'].append(content)

    @socketio.on('disconnect')
    def disconnect():
        room = session.get('room')
        name = session.get('name')
        leave_room(room)

        if room in rooms:
            rooms[room]['members'] -= 1
            if rooms[room]['members'] <= 0:
                del rooms[room]

        send({'name': name, 'message': 'has left the room'}, to=room)

    return app
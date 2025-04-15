from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import socket

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins='*')

waiting_player = None
rooms = {}      # player_sid -> room_id
partners = {}   # player_sid -> partner_sid

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"[连接] {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[断开] {request.sid}")
    cleanup_user(request.sid)

def cleanup_user(sid):
    if sid in rooms:
        room = rooms[sid]
        emit('partner_left', room=room)
        for k in list(rooms):
            if rooms[k] == room:
                del rooms[k]
        for k in list(partners):
            if partners[k] == sid or k == sid:
                del partners[k]

@socketio.on('match')
def handle_match():
    global waiting_player
    if waiting_player is None:
        waiting_player = request.sid
        emit('status', '等待匹配中...')
    else:
        room_id = f"room_{waiting_player}_{request.sid}"
        join_room(room_id)
        socketio.server.enter_room(waiting_player, room_id)

        rooms[request.sid] = room_id
        rooms[waiting_player] = room_id
        partners[request.sid] = waiting_player
        partners[waiting_player] = request.sid

        emit('matched', {'partner_id': waiting_player}, room=request.sid)
        emit('matched', {'partner_id': request.sid}, room=waiting_player)
        waiting_player = None

@socketio.on('send_message')
def handle_send(data):
    msg = data['message']
    sender_id = request.sid
    room_id = rooms.get(sender_id)
    if room_id:
        emit('receive_message', {
            'from': sender_id,
            'message': msg
        }, room=room_id)

@socketio.on('video_offer')
def handle_video_offer(data):
    partner_id = data['partner_id']
    offer = data['offer']
    emit('video_offer', {'offer': offer, 'partner_id': request.sid}, room=partner_id)

@socketio.on('video_answer')
def handle_video_answer(data):
    partner_id = data['partner_id']
    answer = data['answer']
    emit('video_answer', {'answer': answer, 'partner_id': request.sid}, room=partner_id)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    partner_id = data['partner_id']
    candidate = data['candidate']
    emit('ice_candidate', {'candidate': candidate}, room=partner_id)

@socketio.on('logout')
def handle_logout():
    cleanup_user(request.sid)
    leave_room(rooms.get(request.sid, ''))

if __name__ == '__main__':
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    portNum = 6789
    print(f"✅ 服务器已启动：http://{ip}:{portNum}")
    print(f"✅ 服务器已启动：http://localhost:{portNum}")
    socketio.run(app, host='0.0.0.0', port=portNum, debug=True)

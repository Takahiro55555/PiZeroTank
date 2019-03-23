'''
    クライアントとWebSocketで通信し、操作を受け付ける
    Raspberry Pi Zero W で動作確認
    Author : Takahiro55555
'''
from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect

from modules.motor_controller import MotorController
mtr_ctrl = MotorController()

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


@app.route('/')
def index():
    return render_template('controller.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    if "data" in message:
        print(message)
        return

    if message['b'] == 1:
        mtr_ctrl.apply_brake()
        print("breake")
    else:
        mtr_ctrl.apply_operation(message['x'], message['y'])

    emit('my_response',
         {'x': message['x'], 'y': message['y'], 'b': message['b']})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response',
         {'data': 'Disconnected!', 'count': "???"})
    disconnect()


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

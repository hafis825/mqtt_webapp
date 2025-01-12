from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import eventlet

# ใช้ eventlet เป็น asynchronous mode
eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = '9f92f8d7642a4b2b9d63e15e2f4d8f9b'  # ควรเปลี่ยนเป็นค่าที่ปลอดภัย
socketio = SocketIO(app)

# ตัวแปร global สำหรับ MQTT
mqtt_client = None
mqtt_connected = False
subscribed_topic = ""
received_messages = []

# Callback ฟังก์ชันสำหรับ MQTT
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print("Connected to MQTT Broker!")
        client.subscribe(subscribed_topic)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message} on topic: {msg.topic}")
    received_messages.append(message)
    
    # ส่งข้อความไปยัง frontend ผ่าน SocketIO
    socketio.emit('new_message', {'message': message})

# ฟังก์ชันเริ่มต้น MQTT Client
def init_mqtt(broker, port, username, password):
    global mqtt_client
    mqtt_client = mqtt.Client()
    if username and password:
        mqtt_client.username_pw_set(username, password)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker, port, 60)
    mqtt_client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['GET', 'POST'])
def connect_broker():
    global subscribed_topic
    if request.method == 'POST':
        broker = request.form['broker']
        port = int(request.form['port'])
        username = request.form['username']
        password = request.form['password']
        subscribed_topic = request.form['topic']
        
        try:
            init_mqtt(broker, port, username, password)
            flash('Connected to MQTT Broker successfully!', 'success')
            return redirect(url_for('subscribe_publish'))
        except Exception as e:
            flash(f'Failed to connect to MQTT Broker: {e}', 'danger')
            return redirect(url_for('connect_broker'))
    
    return render_template('connect.html')

@app.route('/subscribe_publish', methods=['GET', 'POST'])
def subscribe_publish():
    if request.method == 'POST':
        topic = request.form['topic']
        message = request.form['message']
        
        if mqtt_client and mqtt_connected:
            mqtt_client.publish(topic, message)
            flash(f'Published message to {topic}', 'success')
        else:
            flash('MQTT client is not connected.', 'danger')
            return redirect(url_for('subscribe_publish'))
    
    return render_template('subscribe_publish.html', messages=received_messages)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)

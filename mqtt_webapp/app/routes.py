from flask import Blueprint, render_template, jsonify, request
from app.mqtt_client import mqtt_client
from flask_socketio import emit

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('connect.html')

@main.route('/connect', methods=['POST'])
def connect():
    data = request.json
    try:
        mqtt_client.connect(
            data['broker'],
            int(data['port']),
            data['client_id']
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/disconnect', methods=['POST'])
def disconnect():
    mqtt_client.disconnect()
    return jsonify({'success': True})

@main.route('/subscribe', methods=['POST'])
def subscribe():
    topic = request.json['topic']
    success = mqtt_client.subscribe(topic)
    return jsonify({'success': success})

@main.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    topic = request.json['topic']
    mqtt_client.unsubscribe(topic)
    return jsonify({'success': True})

@main.route('/publish', methods=['POST'])
def publish():
    data = request.json
    mqtt_client.publish(data['topic'], data['message'])
    return jsonify({'success': True})
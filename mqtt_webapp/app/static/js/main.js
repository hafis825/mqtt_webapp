const socket = io();
let subscribedTopics = new Set();

function connectBroker() {
    const broker = document.getElementById('broker').value;
    const port = document.getElementById('port').value;
    const clientId = document.getElementById('client-id').value;

    fetch('/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ broker, port, clientId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/main';
        } else {
            alert('Connection failed: ' + data.error);
        }
    });
}

function disconnect() {
    fetch('/disconnect', {
        method: 'POST'
    })
    .then(() => {
        window.location.href = '/';
    });
}

function subscribeTopic() {
    const topic = document.getElementById('subscribe-topic').value;
    if (topic && !subscribedTopics.has(topic)) {
        fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                subscribedTopics.add(topic);
                updateTopicsList();
                document.getElementById('subscribe-topic').value = '';
            }
        });
    }
}

function unsubscribeTopic() {
    const select = document.getElementById('topics');
    const topic = select.value;
    if (topic) {
        fetch('/unsubscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic })
        })
        .then(() => {
            subscribedTopics.delete(topic);
            updateTopicsList();
        });
    }
}

function publishMessage() {
    const topic = document.getElementById('publish-topic').value;
    const message = document.getElementById('publish-message').value;
    
    fetch('/publish', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, message })
    })
    .then(() => {
        document.getElementById('publish-message').value = '';
    });
}

function updateTopicsList() {
    const select = document.getElementById('topics');
    select.innerHTML = '';
    [...subscribedTopics].sort().forEach(topic => {
        const option = document.createElement('option');
        option.value = topic;
        option.textContent = topic;
        select.appendChild(option);
    });
}

function clearMessages() {
    document.getElementById('received-messages').innerHTML = '';
}

function addMessage(topic, message) {
    const messagesDiv = document.getElementById('received-messages');
    const timestamp = new Date().toLocaleTimeString();
    const messageHtml = `
        <div class="message">
            <strong>[${timestamp}] Topic:</strong> ${topic}<br>
            <strong>Message:</strong> ${message}
        </div>
    `;
    messagesDiv.innerHTML += messageHtml;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Socket.IO event handlers
socket.on('mqtt_connected', () => {
    const status = document.getElementById('connection-status');
    if (status) {
        status.textContent = '● Connected';
        status.className = 'connected';
    }
});

socket.on('mqtt_error', (data) => {
    const status = document.getElementById('connection-status');
    if (status) {
        status.textContent = '● Disconnected';
        status.className = 'disconnected';
    }
    alert(data.message);
});

socket.on('mqtt_message', (data) => {
    addMessage(data.topic, data.message);
});
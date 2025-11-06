import { PipecatClient } from '@pipecat-ai/client-js';
import { WebSocketTransport } from '@pipecat-ai/websocket-transport';

console.log('Pipecat client initializing...');

const startView = document.getElementById('startView');
const chatView = document.getElementById('chatView');
const startBtn = document.getElementById('startBtn');
const endBtn = document.getElementById('endBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const messagesContainer = document.getElementById('messagesContainer');
const speakingIndicator = document.getElementById('speakingIndicator');

let client = null;
let isConnected = false;
let currentUserMessage = null;
let currentAgentMessage = null;

function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function addMessage(text, type, isStreaming = false) {
    const message = document.createElement('div');
    message.className = `message ${type}`;
    const icon = type === 'user' ? '' : '';
    const label = type === 'user' ? 'You' : 'Agent';
    message.innerHTML = `<div class="message-header"><span class="message-icon">${icon}</span><span>${label}</span></div><div class="message-bubble ${isStreaming ? 'streaming' : ''}">${text}</div><div class="timestamp">${formatTime()}</div>`;
    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return message;
}

function updateMessage(messageElement, text, isStreaming = false) {
    const bubble = messageElement.querySelector('.message-bubble');
    bubble.textContent = text;
    bubble.className = `message-bubble ${isStreaming ? 'streaming' : ''}`;
    messageElement.querySelector('.timestamp').textContent = formatTime();
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateStatus(connected) {
    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

startBtn.addEventListener('click', async () => {
    try {
        startBtn.disabled = true;
        startBtn.textContent = 'Connecting...';
        const transport = new WebSocketTransport();
        client = new PipecatClient(transport, {
            onUserTranscript: (text) => {
                console.log(' User:', text);
                if (!currentUserMessage) {
                    currentUserMessage = addMessage(text, 'user', true);
                } else {
                    updateMessage(currentUserMessage, text, true);
                }
            },
            onBotTranscript: (text) => {
                console.log(' Bot:', text);
                if (!currentAgentMessage) {
                    currentAgentMessage = addMessage(text, 'agent', true);
                } else {
                    updateMessage(currentAgentMessage, text, true);
                }
            },
            onUserStartedSpeaking: () => {
                console.log(' User speaking');
                speakingIndicator.classList.add('active');
                if (currentUserMessage) {
                    currentUserMessage.querySelector('.message-bubble').classList.remove('streaming');
                }
                currentUserMessage = null;
            },
            onUserStoppedSpeaking: () => {
                console.log(' User stopped');
                speakingIndicator.classList.remove('active');
                if (currentUserMessage) {
                    currentUserMessage.querySelector('.message-bubble').classList.remove('streaming');
                }
                currentAgentMessage = null;
            }
        });
        await client.connect({ ws_url: 'ws://localhost:8000/ws' });
        isConnected = true;
        updateStatus(true);
        startView.classList.add('hidden');
        chatView.classList.remove('hidden');
        console.log(' Connected');
    } catch (error) {
        console.error(' Error:', error);
        startBtn.disabled = false;
        startBtn.textContent = 'Start Session';
        alert(`Connection error: ${error.message}`);
    }
});

endBtn.addEventListener('click', async () => {
    if (client && isConnected) {
        try {
            await client.disconnect();
            client = null;
            isConnected = false;
            updateStatus(false);
            chatView.classList.add('hidden');
            startView.classList.remove('hidden');
            messagesContainer.innerHTML = '';
            currentUserMessage = null;
            currentAgentMessage = null;
            speakingIndicator.classList.remove('active');
            startBtn.disabled = false;
            startBtn.textContent = 'Start Session';
            console.log(' Disconnected');
        } catch (error) {
            console.error(' Disconnect error:', error);
        }
    }
});

window.addEventListener('beforeunload', () => {
    if (client && isConnected) {
        client.disconnect();
    }
});

console.log(' Client ready');

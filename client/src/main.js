import { PipecatClient } from '@pipecat-ai/client-js';
import { WebSocketTransport } from '@pipecat-ai/websocket-transport';

const statusDiv = document.getElementById('status');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const logDiv = document.getElementById('log');

function log(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logDiv.appendChild(entry);
    logDiv.scrollTop = logDiv.scrollHeight;
}

function updateStatus(status, text) {
    statusDiv.className = `status ${status}`;
    statusDiv.textContent = text;
}

// Create Pipecat client
const pcClient = new PipecatClient({
    transport: new WebSocketTransport(),
    enableMic: true,
    enableCam: false,
    callbacks: {
        onConnected: () => {
            log('WebSocket connected', 'success');
            updateStatus('connected', 'Connected');
        },
        onDisconnected: () => {
            log('Disconnected');
            updateStatus('disconnected', 'Disconnected');
            connectBtn.disabled = false;
            disconnectBtn.disabled = true;
        },
        onTransportStateChanged: (state) => {
            log(`State: ${state}`);
            if (state === 'ready') {
                updateStatus('ready', 'Ready - Speak!');
            }
        },
        onBotReady: () => {
            log('Bot ready!', 'success');
            updateStatus('ready', 'Bot Ready');
        },
        onUserTranscript: (data) => {
            log(`🎤 YOU: ${data.text}`, 'success');
        },
        onBotTranscript: (data) => {
            log(`🤖 BOT: ${data.text}`, 'info');
        },
        onUserStartedSpeaking: () => {
            log('🎙️ Listening...', 'info');
        },
        onUserStoppedSpeaking: () => {
            log('🎙️ Processing...', 'info');
        },
        onError: (error) => {
            log(`Error: ${error.message}`, 'error');
        },
    },
});

connectBtn.addEventListener('click', async () => {
    try {
        updateStatus('connecting', 'Connecting...');
        log('Initializing...');
        
        await pcClient.initDevices();
        log('Devices OK', 'success');
        
        const wsUrl = `ws://localhost:8000/ws`;
        log(`Connecting to ${wsUrl}...`);
        
        await pcClient.connect({ ws_url: wsUrl });  // Use ws_url parameter
        
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
    } catch (error) {
        log(`Failed: ${error.message}`, 'error');
        updateStatus('disconnected', 'Failed');
        connectBtn.disabled = false;
    }
});

disconnectBtn.addEventListener('click', async () => {
    await pcClient.disconnect();
});

log('Client ready');

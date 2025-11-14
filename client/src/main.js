import { PipecatClient, RTVIEvent } from '@pipecat-ai/client-js';
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
let botAudio = null;
let lastUserText = '';  // Track last user text to prevent duplicates

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

function setupAudioTrack(track) {
    console.log('🔊 Setting up audio track');
    if (!botAudio) {
        botAudio = document.createElement('audio');
        botAudio.autoplay = true;
        document.body.appendChild(botAudio);
    }
    
    if (botAudio.srcObject) {
        const oldTrack = botAudio.srcObject.getAudioTracks()[0];
        if (oldTrack?.id === track.id) return;
    }
    botAudio.srcObject = new MediaStream([track]);
}

function setupMediaTracks() {
    if (!client) return;
    const tracks = client.tracks();
    console.log('📻 Available tracks:', tracks);
    if (tracks.bot?.audio) {
        setupAudioTrack(tracks.bot.audio);
    }
}

startBtn.addEventListener('click', async () => {
    try {
        startBtn.disabled = true;
        startBtn.textContent = 'Connecting...';
        
        client = new PipecatClient({
            transport: new WebSocketTransport(),
            enableCam: false,
            enableMic: true,
        callbacks: {
            onBotLlmText: (data) => {
                const text = data.text || '';
                console.log('🤖 LLM:', text, 'session:', data.session_id?.substring(0, 8));
                
                if (text) {
                    // Stream LLM text - accumulate in one message
                    if (!currentAgentMessage) {
                        currentAgentMessage = addMessage(text, 'agent', true);
                    } else {
                        const currentText = currentAgentMessage.querySelector('.message-bubble').textContent;
                        updateMessage(currentAgentMessage, currentText + ' ' + text, true);
                    }
                }
            },
            
            onUserTranscript: (data) => {
                const text = data.text || '';
                const isFinal = data.final || false;
                
                if (!text) return;
                
                // Console log for user transcripts
                if (!isFinal) {
                    console.log('👤 User (streaming):', text, 'session:', data.session_id?.substring(0, 8));
                }
                
                // Skip all final transcripts - we finalize on UserStoppedSpeaking
                if (isFinal) {
                    return;
                }
                
                // Only show partial/streaming transcripts
                if (!currentUserMessage) {
                    // Only create new message if text is different from last completed message
                    if (text !== lastUserText) {
                        currentUserMessage = addMessage(text, 'user', true);
                    }
                } else {
                    updateMessage(currentUserMessage, text, true);
                }
            },
            onBotTranscript: (data) => {
                // Not used
            },
            onBotTtsText: (data) => {
                // Just log TTS events, LLM streaming handles display
                console.log('🔊 TTS:', data.text, 'session:', data.session_id?.substring(0, 8));
            },
                onUserStartedSpeaking: () => {
                    speakingIndicator.classList.add('active');
                },
                onUserStoppedSpeaking: () => {
                    speakingIndicator.classList.remove('active');
                    if (currentUserMessage) {
                        const bubble = currentUserMessage.querySelector('.message-bubble');
                        bubble.classList.remove('streaming');
                        lastUserText = bubble.textContent;  // Save final text
                        currentUserMessage = null;
                    } else {
                        // Even if no message was created, clear lastUserText for next turn
                        // This ensures a new user turn creates a fresh message
                        lastUserText = '';
                    }
                },
                onBotStartedSpeaking: () => {
                    // Bot is speaking (audio playing)
                },
                onBotStoppedSpeaking: () => {
                    if (currentAgentMessage) {
                        currentAgentMessage.querySelector('.message-bubble').classList.remove('streaming');
                        currentAgentMessage = null;
                    }
                },
                onConnected: () => {
                    updateStatus(true);
                    isConnected = true;
                    startView.classList.add('hidden');
                    chatView.classList.remove('hidden');
                    startBtn.disabled = false;
                    startBtn.textContent = 'Start Session';
                },
                onDisconnected: () => {
                    console.log('❌ Disconnected');
                    updateStatus(false);
                },
                onBotReady: (data) => {
                    console.log('🤖 Bot ready:', data);
                    setupMediaTracks();
                },
                onError: (error) => {
                    console.error('❗ Error:', error);
                }
            }
        });
        
        // Set up track listeners
        client.on(RTVIEvent.TrackStarted, (track, participant) => {
            if (!participant?.local && track.kind === 'audio') {
                setupAudioTrack(track);
            }
        });
        

        
        // Initialize devices first
        console.log('🎙️ Initializing devices...');
        await client.initDevices();
        
        // Connect to WebSocket
        console.log('🔌 Connecting to WebSocket...');
        await client.connect({ wsUrl: 'ws://localhost:8000/ws' });
        // UI updates happen in onConnected callback
        console.log('Connection request sent');
    } catch (error) {
        console.error('❌ Error:', error);
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
            lastUserText = '';  // Reset duplicate tracker
            speakingIndicator.classList.remove('active');
            startBtn.disabled = false;
            startBtn.textContent = 'Start Session';
            
            // Clean up audio
            if (botAudio?.srcObject) {
                botAudio.srcObject.getAudioTracks().forEach(track => track.stop());
                botAudio.srcObject = null;
            }
            
            console.log('✅ Disconnected');
        } catch (error) {
            console.error('❌ Disconnect error:', error);
        }
    }
});

window.addEventListener('beforeunload', () => {
    if (client && isConnected) {
        client.disconnect();
    }
});

console.log(' Client ready');

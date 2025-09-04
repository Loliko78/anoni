// Голосовые сообщения
class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.startTime = null;
        this.recordingTimer = null;
        this.maxDuration = 60; // Максимальная длительность в секундах
    }

    async init() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            return true;
        } catch (error) {
            console.error('Ошибка доступа к микрофону:', error);
            showNotification('Нет доступа к микрофону', 'error');
            return false;
        }
    }

    startRecording() {
        if (!this.mediaRecorder || this.isRecording) return false;
        
        this.audioChunks = [];
        this.isRecording = true;
        this.startTime = Date.now();
        
        this.mediaRecorder.start();
        this.startTimer();
        
        // Показываем интерфейс записи
        this.showRecordingInterface();
        
        return true;
    }

    stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        this.mediaRecorder.stop();
        this.stopTimer();
        
        // Скрываем интерфейс записи
        this.hideRecordingInterface();
    }

    cancelRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        this.mediaRecorder.stop();
        this.stopTimer();
        this.audioChunks = [];
        
        // Скрываем интерфейс записи
        this.hideRecordingInterface();
    }

    startTimer() {
        const timerElement = document.getElementById('recordingTimer');
        let seconds = 0;
        
        this.recordingTimer = setInterval(() => {
            seconds++;
            if (timerElement) {
                timerElement.textContent = this.formatTime(seconds);
            }
            
            // Автоматически останавливаем запись при достижении максимальной длительности
            if (seconds >= this.maxDuration) {
                this.stopRecording();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    async processRecording() {
        if (this.audioChunks.length === 0) return;
        
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const duration = Math.floor((Date.now() - this.startTime) / 1000);
        
        // Проверяем минимальную длительность (1 секунда)
        if (duration < 1) {
            showNotification('Слишком короткая запись', 'warning');
            return;
        }
        
        await this.uploadVoiceMessage(audioBlob, duration);
    }

    async uploadVoiceMessage(audioBlob, duration) {
        const formData = new FormData();
        formData.append('voice', audioBlob, 'voice.webm');
        formData.append('duration', duration);
        
        try {
            const response = await fetch('/upload_voice', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Отправляем голосовое сообщение через SocketIO
                if (typeof io !== 'undefined' && currentChatId) {
                    const socket = io();
                    socket.emit('voice_message', {
                        chat_id: currentChatId,
                        file_id: result.file_id,
                        duration: result.duration
                    });
                }
                showNotification('Голосовое сообщение отправлено', 'success');
            } else {
                showNotification('Ошибка отправки голосового сообщения', 'error');
            }
        } catch (error) {
            console.error('Ошибка загрузки голосового сообщения:', error);
            showNotification('Ошибка отправки голосового сообщения', 'error');
        }
    }

    showRecordingInterface() {
        const recordingInterface = document.getElementById('recordingInterface');
        const voiceButton = document.getElementById('voiceButton');
        
        if (recordingInterface) {
            recordingInterface.style.display = 'flex';
        }
        
        if (voiceButton) {
            voiceButton.classList.add('recording');
        }
    }

    hideRecordingInterface() {
        const recordingInterface = document.getElementById('recordingInterface');
        const voiceButton = document.getElementById('voiceButton');
        
        if (recordingInterface) {
            recordingInterface.style.display = 'none';
        }
        
        if (voiceButton) {
            voiceButton.classList.remove('recording');
        }
    }
}

// Глобальный экземпляр рекордера
let voiceRecorder = null;

// Инициализация голосовых сообщений
async function initVoiceMessages() {
    voiceRecorder = new VoiceRecorder();
    const initialized = await voiceRecorder.init();
    
    if (initialized) {
        setupVoiceControls();
    }
}

// Настройка элементов управления
function setupVoiceControls() {
    const voiceButton = document.getElementById('voiceButton');
    const stopButton = document.getElementById('stopRecording');
    const cancelButton = document.getElementById('cancelRecording');
    
    if (voiceButton) {
        voiceButton.addEventListener('click', toggleVoiceRecording);
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', () => {
            if (voiceRecorder) {
                voiceRecorder.stopRecording();
            }
        });
    }
    
    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            if (voiceRecorder) {
                voiceRecorder.cancelRecording();
            }
        });
    }
}

// Переключение записи голосового сообщения
function toggleVoiceRecording() {
    if (!voiceRecorder) return;
    
    if (voiceRecorder.isRecording) {
        voiceRecorder.stopRecording();
    } else {
        voiceRecorder.startRecording();
    }
}

// Воспроизведение голосового сообщения
function playVoiceMessage(fileId, button) {
    const audio = new Audio(`/voice/${fileId}`);
    const playIcon = button.querySelector('.play-icon');
    const pauseIcon = button.querySelector('.pause-icon');
    const progressBar = button.parentElement.querySelector('.voice-progress');
    
    // Останавливаем все другие аудио
    document.querySelectorAll('audio').forEach(a => {
        if (a !== audio) {
            a.pause();
            a.currentTime = 0;
        }
    });
    
    // Сбрасываем все кнопки воспроизведения
    document.querySelectorAll('.voice-play-btn').forEach(btn => {
        btn.classList.remove('playing');
    });
    
    audio.addEventListener('loadstart', () => {
        button.classList.add('loading');
    });
    
    audio.addEventListener('canplay', () => {
        button.classList.remove('loading');
    });
    
    audio.addEventListener('play', () => {
        button.classList.add('playing');
        if (playIcon) playIcon.style.display = 'none';
        if (pauseIcon) pauseIcon.style.display = 'inline';
    });
    
    audio.addEventListener('pause', () => {
        button.classList.remove('playing');
        if (playIcon) playIcon.style.display = 'inline';
        if (pauseIcon) pauseIcon.style.display = 'none';
    });
    
    audio.addEventListener('ended', () => {
        button.classList.remove('playing');
        if (playIcon) playIcon.style.display = 'inline';
        if (pauseIcon) pauseIcon.style.display = 'none';
        if (progressBar) progressBar.style.width = '0%';
    });
    
    audio.addEventListener('timeupdate', () => {
        if (progressBar && audio.duration) {
            const progress = (audio.currentTime / audio.duration) * 100;
            progressBar.style.width = `${progress}%`;
        }
    });
    
    audio.addEventListener('error', () => {
        button.classList.remove('loading', 'playing');
        showNotification('Ошибка воспроизведения', 'error');
    });
    
    if (audio.paused) {
        audio.play().catch(error => {
            console.error('Ошибка воспроизведения:', error);
            showNotification('Ошибка воспроизведения', 'error');
        });
    } else {
        audio.pause();
    }
}

// Добавление голосового сообщения в чат
function addVoiceMessage(messageData, animate = true) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${messageData.sender_id == currentUserId ? 'sent' : 'received'}`;
    messageDiv.dataset.messageId = messageData.id;
    
    if (animate) {
        messageDiv.style.animation = 'messageSlideIn 0.3s ease';
    }
    
    const isOwnMessage = messageData.sender_id == currentUserId;
    const duration = messageData.duration || 0;
    
    let messageHTML = '';
    
    if (!isOwnMessage) {
        messageHTML += `
            <div class="message-avatar">
                <div class="mini-avatar">
                    <span>${messageData.sender_name ? messageData.sender_name[0].toUpperCase() : 'U'}</span>
                </div>
            </div>
        `;
    }
    
    messageHTML += `
        <div class="message-content">
            <div class="voice-message">
                <button class="voice-play-btn" onclick="playVoiceMessage(${messageData.file_id}, this)">
                    <span class="play-icon">▶️</span>
                    <span class="pause-icon" style="display: none;">⏸️</span>
                </button>
                <div class="voice-waveform">
                    <div class="voice-progress"></div>
                </div>
                <span class="voice-duration">${formatDuration(duration)}</span>
            </div>
            <div class="message-time">${formatTime(messageData.timestamp)}</div>
        </div>
    `;
    
    if (isOwnMessage) {
        messageHTML += `
            <div class="message-actions">
                <button class="btn btn-delete" onclick="deleteMessage(${messageData.id})" title="Удалить">🗑️</button>
            </div>
        `;
    }
    
    messageDiv.innerHTML = messageHTML;
    messagesContainer.appendChild(messageDiv);
    
    scrollToBottom();
}

// Форматирование длительности
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Получение ID текущего чата
let currentChatId = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Получаем ID чата из URL
    const pathParts = window.location.pathname.split('/');
    if (pathParts.includes('chat')) {
        const chatIndex = pathParts.indexOf('chat');
        if (chatIndex !== -1 && pathParts[chatIndex + 1]) {
            currentChatId = parseInt(pathParts[chatIndex + 1]);
        }
    }
    
    // Проверяем поддержку MediaRecorder
    if (typeof MediaRecorder !== 'undefined') {
        initVoiceMessages();
    } else {
        console.warn('MediaRecorder не поддерживается в этом браузере');
    }
});
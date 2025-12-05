const API_BASE_URL = 'http://localhost:5000/api';

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const talkButton = document.getElementById('talkButton');
const statusDiv = document.getElementById('status');
const conversationArea = document.getElementById('conversationArea');
const messagesList = document.getElementById('messagesList');
const tasksList = document.getElementById('tasksList');
const notesList = document.getElementById('notesList');
const caregiverAlert = document.getElementById('caregiverAlert');
const alertMessage = document.getElementById('alertMessage');
const messageInput = document.getElementById('messageInput');
const typingIndicator = document.getElementById('typingIndicator');
const themeToggle = document.getElementById('themeToggle');
const currentTime = document.getElementById('currentTime');

document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadNotes();
    loadConversationHistory();
    checkCaregiverAlerts();
    updateClock();
    
    setInterval(checkCaregiverAlerts, 60000);
    setInterval(updateClock, 1000);
});

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

if (messageInput) {
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendTextMessage();
        }
    });
}

talkButton.addEventListener('mousedown', startRecording);
talkButton.addEventListener('mouseup', stopRecording);
talkButton.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startRecording();
});
talkButton.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopRecording();
});

function updateClock() {
    if (!currentTime) return;
    const now = new Date();
    const hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    currentTime.textContent = `${displayHours}:${minutes} ${ampm}`;
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        statusDiv.textContent = 'Listening...';
        talkButton.classList.add('recording');
        
    } catch (error) {
        console.error('Microphone error:', error);
        statusDiv.textContent = 'Microphone access denied';
    }
}

async function stopRecording() {
    if (!isRecording || !mediaRecorder) return;
    
    mediaRecorder.stop();
    isRecording = false;
    
    statusDiv.textContent = 'Processing...';
    talkButton.classList.remove('recording');
    
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        await sendAudioToServer(audioBlob);
        
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    };
}

async function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    if (typingIndicator) typingIndicator.classList.remove('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('Response received:', data);
        
        if (typingIndicator) typingIndicator.classList.add('hidden');
        
        displayMessage(data.transcript, 'user');
        displayMessage(data.response, 'agent');
        
        if (data.audio) {
            await playAudioResponse(data.audio);
        } else {
            console.error('No audio in response');
            statusDiv.textContent = 'Hold microphone to speak';
        }
        
        loadTasks();
        loadNotes();
        
    } catch (error) {
        console.error('Error:', error);
        if (typingIndicator) typingIndicator.classList.add('hidden');
        statusDiv.textContent = 'Error - Ready to try again';
        setTimeout(() => {
            statusDiv.textContent = 'Hold microphone to speak';
        }, 2000);
    }
}

function displayMessage(text, type) {
    const target = messagesList || conversationArea;
    if (!target) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = type === 'user' ? 'U' : 'K';
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble">${text}</div>
        </div>
    `;
    
    target.appendChild(messageDiv);
    
    requestAnimationFrame(() => {
        if (conversationArea) {
            conversationArea.scrollTo({
                top: conversationArea.scrollHeight,
                behavior: 'smooth'
            });
        }
    });
}

async function playAudioResponse(audioBase64) {
    return new Promise((resolve, reject) => {
        try {
            const audioBlob = base64ToBlob(audioBase64, 'audio/mpeg');
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            statusDiv.textContent = 'Speaking...';
            
            audio.play().catch(err => {
                console.error('Audio play error:', err);
                statusDiv.textContent = 'Hold microphone to speak';
                reject(err);
            });
            
            audio.onended = () => {
                statusDiv.textContent = 'Hold microphone to speak';
                URL.revokeObjectURL(audioUrl);
                resolve();
            };
            
            audio.onerror = (err) => {
                console.error('Audio error:', err);
                statusDiv.textContent = 'Hold microphone to speak';
                URL.revokeObjectURL(audioUrl);
                reject(err);
            };
            
        } catch (error) {
            console.error('Error creating audio:', error);
            statusDiv.textContent = 'Hold microphone to speak';
            reject(error);
        }
    });
}

function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
}

async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks`);
        const tasks = await response.json();
        
        if (!tasksList) return;
        
        if (tasks.length === 0) {
            tasksList.innerHTML = '<p class="empty-state">No tasks yet</p>';
            return;
        }
        
        tasksList.innerHTML = '';
        
        tasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = `task-item ${task.completed ? 'completed' : ''}`;
            taskDiv.onclick = () => toggleTask(task.id, !task.completed);
            
            const taskName = task.task_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            taskDiv.innerHTML = `
                <div class="task-content">
                    <span class="task-name">${taskName}</span>
                    <span class="task-time">${task.scheduled_time}</span>
                </div>
                <span class="task-status">${task.completed ? '✓' : ''}</span>
            `;
            
            tasksList.appendChild(taskDiv);
        });
        
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

async function toggleTask(id, newStatus) {
    try {
        await fetch(`${API_BASE_URL}/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: newStatus })
        });
        
        loadTasks(); 
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

async function loadNotes() {
    try {
        const response = await fetch(`${API_BASE_URL}/notes`);
        const notes = await response.json();
        
        if (!notesList) return;
        
        if (notes.length === 0) {
            notesList.innerHTML = '<p class="empty-state">No memories yet</p>';
            return;
        }
        
        notesList.innerHTML = '';
        
        notes.slice(0, 10).forEach(note => {
            const noteDiv = document.createElement('div');
            noteDiv.className = 'note-item';
            
            const createdAt = new Date(note.created_at).toLocaleString('en-IN', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            noteDiv.innerHTML = `
                <div class="note-text">${note.note_text}</div>
                <span class="note-time">${createdAt}</span>
            `;
            
            notesList.appendChild(noteDiv);
        });
        
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

async function checkCaregiverAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/caregiver-alert`);
        const data = await response.json();
        
        if (!caregiverAlert || !alertMessage) return;
        
        if (data.alert) {
            alertMessage.textContent = data.alert;
            caregiverAlert.classList.remove('hidden');
        } else {
            caregiverAlert.classList.add('hidden');
        }
        
    } catch (error) {
        console.error('Error checking alerts:', error);
    }
}

async function loadConversationHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        const history = await response.json();
        
        if (history.length === 0) return;
        
        const target = messagesList || conversationArea;
        if (target) target.innerHTML = '';
        
        history.forEach(chat => {
            displayMessage(chat.user_message, 'user');
            displayMessage(chat.agent_response, 'agent');
        });
        
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function sendTextMessage() {
    if (!messageInput) return;
    
    const text = messageInput.value.trim();
    if (!text) return;

    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    displayMessage(text, 'user');
    statusDiv.textContent = 'Thinking...';
    
    if (typingIndicator) typingIndicator.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        if (typingIndicator) typingIndicator.classList.add('hidden');

        displayMessage(data.response, 'agent');

        if (data.audio) {
            await playAudioResponse(data.audio);
        } else {
            statusDiv.textContent = 'Hold microphone to speak';
        }
        
        loadTasks();
        loadNotes();

    } catch (error) {
        console.error('Error:', error);
        if (typingIndicator) typingIndicator.classList.add('hidden');
        statusDiv.textContent = 'Error sending message';
        displayMessage("I'm having trouble connecting right now.", 'agent');
    }
}

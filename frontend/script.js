const API_BASE_URL = 'http://localhost:5000/api';

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const talkButton = document.getElementById('talkButton');
const statusDiv = document.getElementById('status');
const conversationArea = document.getElementById('conversationArea');
const tasksList = document.getElementById('tasksList');
const notesList = document.getElementById('notesList');
const caregiverAlert = document.getElementById('caregiverAlert');
const alertMessage = document.getElementById('alertMessage');

document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadNotes();
    checkCaregiverAlerts();
    
    setInterval(checkCaregiverAlerts, 60000);
});

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
        talkButton.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
        
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
    talkButton.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        await sendAudioToServer(audioBlob);
        
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    };
}

async function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
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
        
        displayMessage(data.transcript, 'user');
        displayMessage(data.response, 'agent');
        
        if (data.audio) {
            await playAudioResponse(data.audio);
        } else {
            console.error('No audio in response');
            statusDiv.textContent = 'Ready to listen';
        }
        
        loadTasks();
        loadNotes();
        
    } catch (error) {
        console.error('Error:', error);
        statusDiv.textContent = 'Error - Ready to try again';
        setTimeout(() => {
            statusDiv.textContent = 'Ready to listen';
        }, 2000);
    }
}

function displayMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = text;
    
    conversationArea.appendChild(messageDiv);
    conversationArea.scrollTop = conversationArea.scrollHeight;
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
                statusDiv.textContent = 'Audio play failed - Ready to listen';
                reject(err);
            });
            
            audio.onended = () => {
                statusDiv.textContent = 'Ready to listen';
                URL.revokeObjectURL(audioUrl);
                resolve();
            };
            
            audio.onerror = (err) => {
                console.error('Audio error:', err);
                statusDiv.textContent = 'Ready to listen';
                URL.revokeObjectURL(audioUrl);
                reject(err);
            };
            
        } catch (error) {
            console.error('Error creating audio:', error);
            statusDiv.textContent = 'Ready to listen';
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
        
        tasksList.innerHTML = '';
        
        tasks.forEach(task => {
            const taskDiv = document.createElement('div');
            // Add 'completed' class if task.completed is true
            taskDiv.className = `task-item ${task.completed ? 'completed' : ''}`;
        
            taskDiv.onclick = () => toggleTask(task.id, !task.completed);
            
            // Format the name 
            const taskName = task.task_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            taskDiv.innerHTML = `
                <span class="task-name">${taskName}</span>
                <span class="task-time">${task.scheduled_time}</span>
                <span class="task-status">${task.completed ? '✅' : '⏰'}</span>
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
        
        // Reload list to show the update
        loadTasks(); 
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

async function loadNotes() {
    try {
        const response = await fetch(`${API_BASE_URL}/notes`);
        const notes = await response.json();
        
        notesList.innerHTML = '';
        
        if (notes.length === 0) {
            notesList.innerHTML = '<p style="color: #999; text-align: center;">No notes yet</p>';
            return;
        }
        
        notes.forEach(note => {
            const noteDiv = document.createElement('div');
            noteDiv.className = 'note-item';
            
            const createdAt = new Date(note.created_at).toLocaleString('en-IN', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            noteDiv.innerHTML = `
                <div>${note.note_text}</div>
                <div class="note-time">${createdAt}</div>
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

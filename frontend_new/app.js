// Configuration
const API_URL = '/api';

// DOM Elements
const chatView = document.getElementById('chat-view');
const libraryView = document.getElementById('library-view');
const libraryBtn = document.getElementById('library-btn');
const backToChatBtn = document.getElementById('back-to-chat-btn');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const fileInput = document.getElementById('file-input');
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const browseBtn = document.getElementById('browse-btn');
const dropZone = document.getElementById('drop-zone');
const uploadStatus = document.getElementById('upload-status');
const documentsTableBody = document.getElementById('documents-table-body');
const newChatBtn = document.getElementById('new-chat-btn');

// Theme Handling
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'light') {
    document.body.classList.add('light-mode');
    themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
} else {
    // Default to dark mode if no theme saved or saved as dark
    themeToggleBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
}

themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    const isLight = document.body.classList.contains('light-mode');
    themeToggleBtn.innerHTML = isLight ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
});

// State
let conversations = JSON.parse(localStorage.getItem('conversations') || '{}');
let currentConversationId = localStorage.getItem('currentConversationId') || Date.now().toString();

// Initialize
renderConversationsList();
if (conversations[currentConversationId]) {
    loadConversation(currentConversationId);
} else {
    startNewChat();
}

// Navigation
libraryBtn.addEventListener('click', () => {
    chatView.classList.add('hidden');
    libraryView.classList.remove('hidden');
    loadDocuments();
});

backToChatBtn.addEventListener('click', () => {
    libraryView.classList.add('hidden');
    chatView.classList.remove('hidden');
});

// Chat Logic
function ensureCurrentConversation() {
    if (!conversations[currentConversationId]) {
        conversations[currentConversationId] = {
            id: currentConversationId,
            title: 'Nouvelle conversation',
            messages: [],
            timestamp: Date.now()
        };
        saveConversations();
    }
}

function saveConversations() {
    localStorage.setItem('conversations', JSON.stringify(conversations));
    localStorage.setItem('currentConversationId', currentConversationId);
    renderConversationsList();
}

function renderConversationsList() {
    const list = document.getElementById('conversations-list');
    if (!list) return;

    list.innerHTML = '';

    // Sort by newest first
    const sorted = Object.values(conversations).sort((a, b) => b.timestamp - a.timestamp);

    sorted.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
        item.innerHTML = `
            <i class="fa-regular fa-message"></i>
            <span class="conv-title">${conv.title}</span>
            <button class="delete-conv" onclick="deleteConversation(event, '${conv.id}')">
                <i class="fa-solid fa-trash"></i>
            </button>
        `;
        item.onclick = (e) => {
            if (!e.target.closest('.delete-conv')) {
                loadConversation(conv.id);
            }
        };
        list.appendChild(item);
    });
}

function loadConversation(id) {
    currentConversationId = id;
    localStorage.setItem('currentConversationId', currentConversationId);

    chatMessages.innerHTML = '';

    const conv = conversations[id];
    if (conv && conv.messages.length > 0) {
        conv.messages.forEach(msg => renderMessageToUI(msg.content, msg.isUser));
    } else {
        // Show welcome message if empty
        showWelcomeMessage();
    }
    renderConversationsList();
}

window.deleteConversation = function (e, id) {
    e.stopPropagation();
    if (confirm('Supprimer cette conversation ? / حذف هذه المحادثة؟')) {
        delete conversations[id];
        if (id === currentConversationId) {
            startNewChat();
        } else {
            saveConversations();
        }
    }
}

function startNewChat() {
    currentConversationId = Date.now().toString();
    localStorage.setItem('currentConversationId', currentConversationId);
    showWelcomeMessage();
    renderConversationsList();
}

function showWelcomeMessage() {
    chatMessages.innerHTML = `
        <div class="message system-message">
            <div class="message-content">
                <div class="welcome-card">
                    <i class="fa-solid fa-robot pulse-icon"></i>
                    <h2>Bienvenue sur NIBRASSE</h2>
                    <h2 class="arabic-text">مرحباً بكم في نبــراس</h2>
                    <p>Je suis votre assistant IA. Posez-moi des questions sur vos documents.</p>
                    <p class="arabic-text">أنا مساعدك الذكي. اسألني عن مستنداتك.</p>
                </div>
            </div>
        </div>
    `;
}

function renderMessageToUI(content, isUser) {
    // Remove welcome message if it exists and we are adding a user message
    const welcomeCard = chatMessages.querySelector('.welcome-card');
    if (welcomeCard && isUser) {
        // Don't remove it immediately, let the flow handle it, or clear if it's the first message
        if (chatMessages.children.length === 1) {
            chatMessages.innerHTML = '';
        }
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    let formattedContent = content.replace(/\n/g, '<br>');

    // Create content wrapper
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-wrapper';
    contentWrapper.innerHTML = `<div class="message-content">${formattedContent}</div>`;

    // Add actions for bot messages
    if (!isUser) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'message-actions';

        // Copy Button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'action-btn';
        copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copier / نسخ';
        copyBtn.onclick = () => copyToClipboard(content, copyBtn);

        // Summarize Button
        const summarizeBtn = document.createElement('button');
        summarizeBtn.className = 'action-btn';
        summarizeBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Résumer / تلخيص';
        summarizeBtn.onclick = () => summarizeMessage(content);

        actionsDiv.appendChild(copyBtn);
        actionsDiv.appendChild(summarizeBtn);
        contentWrapper.appendChild(actionsDiv);
    }

    messageDiv.appendChild(contentWrapper);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function copyToClipboard(text, btn) {
    try {
        await navigator.clipboard.writeText(text);
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Copié!';
        btn.classList.add('success');
        setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.classList.remove('success');
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

async function summarizeMessage(text) {
    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    loadingDiv.innerHTML = '<div class="message-content"><i class="fa-solid fa-circle-notch fa-spin"></i> Génération du résumé... / جاري التلخيص...</div>';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        chatMessages.removeChild(loadingDiv);

        if (!response.ok) throw new Error('Summarization failed');

        const data = await response.json();
        addMessage(`**Résumé / ملخص:**\n\n${data.summary}`);

    } catch (error) {
        if (loadingDiv.parentNode) chatMessages.removeChild(loadingDiv);
        console.error(error);
        alert("Erreur lors du résumé / خطأ في التلخيص");
    }
}

function addMessage(content, isUser = false) {
    // 1. Render to UI
    renderMessageToUI(content, isUser);

    // 2. Save to State
    ensureCurrentConversation();
    conversations[currentConversationId].messages.push({ content, isUser });

    // Update title if first user message
    if (isUser && conversations[currentConversationId].messages.length === 1) {
        conversations[currentConversationId].title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
    }
    conversations[currentConversationId].timestamp = Date.now();

    saveConversations();
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, true);
    userInput.value = '';
    userInput.style.height = 'auto';

    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    loadingDiv.innerHTML = '<div class="message-content"><i class="fa-solid fa-circle-notch fa-spin"></i> Réflexion en cours...</div>';
    chatMessages.appendChild(loadingDiv);

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: text }),
        });

        chatMessages.removeChild(loadingDiv);

        if (!response.ok) throw new Error('Erreur réseau');

        const data = await response.json();
        addMessage(data.answer);

    } catch (error) {
        chatMessages.removeChild(loadingDiv);
        addMessage("Désolé, une erreur est survenue. Veuillez vérifier que le backend est lancé. / عذراً، حدث خطأ. يرجى التأكد من تشغيل الخادم.", false);
        console.error(error);
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// New Chat
newChatBtn.addEventListener('click', startNewChat);

// File Upload Logic
browseBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', handleFiles);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    handleFiles({ target: { files } });
});

async function handleFiles(e) {
    const files = e.target.files;
    if (!files.length) return;

    uploadStatus.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Téléchargement en cours... / جاري التحميل...';

    for (const file of files) {
        // Client-side validation
        if (!file.name.toLowerCase().endsWith('.txt')) {
            uploadStatus.innerHTML = `<span style="color: var(--error-color)"><i class="fa-solid fa-triangle-exclamation"></i> Format non supporté: ${file.name}. Utilisez .txt uniquement. <br> صيغة غير مدعومة. يرجى استخدام ملفات .txt فقط.</span>`;
            // Clear after 5 seconds
            setTimeout(() => { uploadStatus.innerHTML = ''; }, 5000);
            continue;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                uploadStatus.innerHTML = `<span style="color: var(--success-color)"><i class="fa-solid fa-check"></i> ${file.name} téléchargé avec succès! / تم التحميل بنجاح</span>`;
                loadDocuments(); // Refresh list
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || 'Upload failed';
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error(error);
            let displayError = `Erreur lors du téléchargement de ${file.name}`;
            if (error.message.includes('Only .txt files')) {
                displayError = `Format non supporté: ${file.name}. Utilisez .txt uniquement.`;
            }
            uploadStatus.innerHTML = `<span style="color: var(--error-color)"><i class="fa-solid fa-xmark"></i> ${displayError} <br> خطأ في التحميل</span>`;
        }
    }

    // Reset status after 3 seconds (if success)
    setTimeout(() => {
        if (uploadStatus.innerHTML.includes('succès')) {
            uploadStatus.innerHTML = '';
        }
    }, 3000);
}

// Load Documents
async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/documents`);
        if (!response.ok) throw new Error('Failed to fetch documents');

        const data = await response.json();
        renderDocuments(data.documents);
    } catch (error) {
        console.error('Error loading documents:', error);
        documentsTableBody.innerHTML = '<tr><td colspan="4">Erreur de chargement / خطأ في التحميل</td></tr>';
    }
}

function renderDocuments(documents) {
    documentsTableBody.innerHTML = '';

    if (!documents || documents.length === 0) {
        documentsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Aucun document trouvé / لا توجد مستندات</td></tr>';
        return;
    }

    documents.forEach(doc => {
        const row = document.createElement('tr');
        const date = new Date(doc.upload_date || Date.now()).toLocaleDateString('fr-FR');

        row.innerHTML = `
            <td><i class="fa-regular fa-file-lines"></i> ${doc.filename}</td>
            <td>${date}</td>
            <td>${doc.total_chunks ? doc.total_chunks + ' chunks' : '-'}</td>
            <td><span style="color: var(--success-color)">Traité / معالج</span></td>
        `;
        documentsTableBody.appendChild(row);
    });
}

const projectId = window.location.pathname.split('/')[2];
const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '';
const chatMessages = document.getElementById('chat-messages');
let lastId = Number(chatMessages?.dataset.lastId ?? 0);
let isPolling = false;

function scrollToLatest(behavior = 'smooth') {
    chatMessages?.scrollTo({
        top: chatMessages.scrollHeight,
        behavior,
    });
}

function appendMessage(message) {
    if (!chatMessages) return;

    chatMessages.querySelector('.project-chat-empty')?.remove();

    const article = document.createElement('article');
    article.className = `chat-message ${message.is_mine ? 'is-mine' : 'is-other'}`;

    if (!message.is_mine) {
        const sender = document.createElement('strong');
        sender.className = 'chat-message__sender';
        sender.textContent = message.sender;
        article.appendChild(sender);
    }

    const row = document.createElement('div');
    row.className = 'chat-message__row';

    const bubble = document.createElement('div');
    bubble.className = 'chat-message__bubble';
    bubble.textContent = message.content;

    const time = document.createElement('time');
    time.className = 'chat-message__time';
    time.textContent = message.sent_at;

    row.append(bubble, time);
    article.appendChild(row);
    chatMessages.appendChild(article);
}

async function fetchMessages() {
    if (isPolling) return;
    isPolling = true;

    try {
        const response = await fetch(
            `/projects/${projectId}/chat/messages/?last_id=${lastId}`,
        );
        if (!response.ok) return;

        const data = await response.json();
        data.messages.forEach((message) => {
            appendMessage(message);
            lastId = message.id;
        });

        if (data.messages.length > 0) scrollToLatest();
    } finally {
        isPolling = false;
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const content = input.value.trim();
    if (!content) return;

    input.disabled = true;

    try {
        const response = await fetch(`/projects/${projectId}/chat/send/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `content=${encodeURIComponent(content)}`,
        });

        if (!response.ok) return;

        input.value = '';
        await fetchMessages();
    } finally {
        input.disabled = false;
        input.focus();
    }
}

setInterval(fetchMessages, 3000);

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'chat-input') {
        e.preventDefault();
        sendMessage();
    }
});

requestAnimationFrame(() => scrollToLatest('auto'));
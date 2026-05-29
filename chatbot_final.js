/* FitAI — StyleBot Chatbot JS */

const messagesContainer = document.getElementById('messagesContainer');
let isTyping = false;

// ── Auto-resize textarea ───────────────────────────────────────────────────
window.autoResize = function (el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
};

// ── Handle Enter key ───────────────────────────────────────────────────────
window.handleChatKey = function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

// ── Send prompt from sidebar ───────────────────────────────────────────────
window.sendPrompt = function (text) {
  const input = document.getElementById('chatInput');
  if (input) { input.value = text; autoResize(input); }
  sendMessage();
};

// ── Clear chat ─────────────────────────────────────────────────────────────
window.clearChat = function () {
  messagesContainer.innerHTML = `
    <div class="message bot-message">
      <div class="msg-avatar">✦</div>
      <div class="msg-bubble">
        <p>Chat cleared! I'm ready to help with your fashion questions. What are you looking to wear? 👗</p>
      </div>
      <div class="msg-time">Just now</div>
    </div>`;
};

// ── Send message ───────────────────────────────────────────────────────────
window.sendMessage = async function () {
  if (isTyping) return;
  const input = document.getElementById('chatInput');
  const msg   = input?.value.trim();
  if (!msg) return;

  // Append user message
  appendMessage('user', msg);
  input.value = '';
  input.style.height = 'auto';

  // Show typing
  isTyping = true;
  const typingEl = showTyping();
  setTypingVisible(true);

  try {
    const res  = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    });
    const data = await res.json();

    typingEl.remove();
    setTypingVisible(false);

    if (data.success) {
      appendMessage('bot', data.reply);
    } else {
      appendMessage('bot', 'Sorry, I ran into an issue. Please try again!');
    }
  } catch {
    typingEl.remove();
    setTypingVisible(false);
    appendMessage('bot', 'Network error. Please check your connection and try again.');
  } finally {
    isTyping = false;
  }
};

function appendMessage(role, text) {
  const isBot = role === 'bot';
  const div   = document.createElement('div');
  div.className = `message ${isBot ? 'bot-message' : 'user-message'}`;

  const now  = new Date();
  const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Format paragraphs
  const formatted = text.split('\n').filter(Boolean)
    .map(line => `<p>${line}</p>`).join('');

  div.innerHTML = `
    <div class="msg-avatar">${isBot ? '✦' : '👤'}</div>
    <div>
      <div class="msg-bubble">${formatted}</div>
      <div class="msg-time">${time}</div>
    </div>`;

  div.style.opacity = '0';
  div.style.transform = 'translateY(10px)';
  messagesContainer.appendChild(div);
  scrollToBottom();

  requestAnimationFrame(() => {
    div.style.transition = 'opacity .3s, transform .3s';
    div.style.opacity    = '1';
    div.style.transform  = 'none';
  });
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'message bot-message typing-msg';
  div.innerHTML = `
    <div class="msg-avatar">✦</div>
    <div class="msg-bubble">
      <span class="typing-indicator" style="display:flex">
        <span></span><span></span><span></span>
      </span>
    </div>`;
  messagesContainer.appendChild(div);
  scrollToBottom();
  return div;
}

function setTypingVisible(visible) {
  const el = document.getElementById('typingIndicator');
  const status = document.getElementById('botStatus');
  if (el) el.style.display = visible ? 'flex' : 'none';
  if (status) status.style.display = visible ? 'none' : 'block';
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

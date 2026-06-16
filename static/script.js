/**
 * FAQ NLP Chatbot - Frontend Script
 * Handles input listeners, web API requests, typing animations, and DOM updates.
 */
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBody = document.getElementById('chat-body');
    const sendButton = document.getElementById('send-button');
    const clearChatBtn = document.getElementById('clear-chat-btn');

    // Auto-focus input on page load
    userInput.focus();

    // Handle form submit (Send button or Enter key)
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleUserMessageSend();
    });

    // Clear Chat history action
    clearChatBtn.addEventListener('click', () => {
        const suggestions = document.getElementById('suggestions-container');
        const suggestionsHtml = suggestions ? suggestions.outerHTML : '';

        const welcomeHtml = `
            <div class="message-row bot-row animate-in">
                <div class="message-bubble">
                    <div class="message-text">
                        Hello! I'm your NLP-powered FAQ assistant. Ask me anything about our services, orders, refunds, or account settings!
                    </div>
                    <span class="message-time">Just now</span>
                </div>
            </div>
        `;
        
        chatBody.innerHTML = welcomeHtml;
        
        if (suggestionsHtml) {
            chatBody.insertAdjacentHTML('beforeend', suggestionsHtml);
            bindSuggestionPillEvents();
        }
        
        userInput.focus();
        scrollToBottom();
    });

    /**
     * Set up event listeners on quick action pills
     */
    function bindSuggestionPillEvents() {
        const pills = document.querySelectorAll('.suggestion-pill');
        pills.forEach(pill => {
            pill.addEventListener('click', () => {
                const questionText = pill.getAttribute('data-question');
                if (questionText) {
                    userInput.value = questionText;
                    handleUserMessageSend();
                }
            });
        });
    }

    // Bind suggestion pills on initial load
    bindSuggestionPillEvents();

    /**
     * Standard message sender function
     */
    async function handleUserMessageSend() {
        const rawMessageText = userInput.value;
        const messageText = rawMessageText.trim();
        
        if (!messageText) return;

        // Clear input element immediately
        userInput.value = '';

        // 1. Append User Bubble to body
        appendMessageBubble(messageText, 'user');
        scrollToBottom();

        // 2. Render Bot Typing Anim
        const typingElement = renderTypingIndicator();
        scrollToBottom();

        try {
            // Send payload to Flask chat endpoint
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: messageText })
            });

            // Remove typing bubble
            typingElement.remove();

            if (!response.ok) {
                const errorPayload = await response.json();
                appendMessageBubble(errorPayload.error || 'Server error: unable to resolve query.', 'error');
            } else {
                const data = await response.json();
                appendMessageBubble(data.response, 'bot');
            }
        } catch (error) {
            // Remove typing bubble
            typingElement.remove();
            console.error('Fetch error details:', error);
            appendMessageBubble('Connection error. Please confirm that the backend server is running.', 'error');
        }

        scrollToBottom();
        userInput.focus();
    }

    /**
     * Create and insert message bubble nodes in the DOM
     */
    function appendMessageBubble(text, senderType) {
        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row', 'animate-in');
        
        if (senderType === 'user') {
            messageRow.classList.add('user-row');
        } else if (senderType === 'error') {
            messageRow.classList.add('bot-row', 'error-row');
        } else {
            messageRow.classList.add('bot-row');
        }

        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble');

        const textDiv = document.createElement('div');
        textDiv.classList.add('message-text');
        textDiv.textContent = text;
        
        const timeSpan = document.createElement('span');
        timeSpan.classList.add('message-time');
        timeSpan.textContent = getFormattedTime();

        bubble.appendChild(textDiv);
        bubble.appendChild(timeSpan);
        messageRow.appendChild(bubble);

        // Keep suggestions always at the absolute bottom of scrollable feed
        const suggestions = document.getElementById('suggestions-container');
        if (suggestions && chatBody.contains(suggestions)) {
            chatBody.insertBefore(messageRow, suggestions);
        } else {
            chatBody.appendChild(messageRow);
        }
    }

    /**
     * Create and insert dynamic typing bubble
     */
    function renderTypingIndicator() {
        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row', 'bot-row', 'animate-in');
        
        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble', 'typing-bubble');
        bubble.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        
        messageRow.appendChild(bubble);

        const suggestions = document.getElementById('suggestions-container');
        if (suggestions && chatBody.contains(suggestions)) {
            chatBody.insertBefore(messageRow, suggestions);
        } else {
            chatBody.appendChild(messageRow);
        }
        
        return messageRow;
    }

    /**
     * Get local system time formatted as "HH:MM AM/PM"
     */
    function getFormattedTime() {
        const date = new Date();
        let hours = date.getHours();
        let minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // 0 hours should be 12
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return `${hours}:${minutes} ${ampm}`;
    }

    /**
     * Scroll the message stream to the bottom
     */
    function scrollToBottom() {
        chatBody.scrollTop = chatBody.scrollHeight;
    }
});

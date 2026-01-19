document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const toggleSidebar = document.getElementById('toggleSidebar');
    const mainContent = document.getElementById('mainContent');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const chatArea = document.getElementById('chatArea');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const actionCards = document.querySelectorAll('.action-card');
    const chatItems = document.querySelectorAll('.chat-item');
    const deleteButtons = document.querySelectorAll('.delete-chat-btn');
    const navCollapseBtns = document.querySelectorAll('.nav-collapse-btn');

    // 1. TOGGLE SIDEBAR BUTTON (Chevron inside sidebar)
    toggleSidebar.addEventListener('click', function() {
        if (window.innerWidth >= 1200) {
            // Desktop: toggle between collapsed/expanded
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Show/hide mobile menu button
            updateMobileButtonVisibility();
        } else {
            // Mobile: just close sidebar
            sidebar.classList.remove('mobile-open');
        }
    });

    // 2. MOBILE MENU BUTTON (Bars icon in header)
    mobileMenuBtn.addEventListener('click', function() {
        if (window.innerWidth >= 1200) {
            // DESKTOP: If sidebar is hidden, make it visible
            if (sidebar.classList.contains('collapsed')) {
                // Remove collapsed class to make sidebar visible
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
            }
            // If clicking bars button when sidebar is already visible, do nothing
        } else {
            // MOBILE: Toggle mobile menu
            sidebar.classList.toggle('mobile-open');
        }
    });

    // 3. Update mobile button visibility function
    function updateMobileButtonVisibility() {
        if (window.innerWidth >= 1200) {
            if (sidebar.classList.contains('collapsed')) {
                mobileMenuBtn.classList.add('show-on-desktop');
            } else {
                mobileMenuBtn.classList.remove('show-on-desktop');
            }
        }
    }

    // 4. CLOSE SIDEBAR WHEN CLICKING OUTSIDE (MOBILE ONLY)
    document.addEventListener('click', function(event) {
        if (window.innerWidth < 1200) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnMobileMenu = mobileMenuBtn.contains(event.target);
            
            if (!isClickInsideSidebar && !isClickOnMobileMenu) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });

    // 5. WINDOW RESIZE HANDLER
    function handleResize() {
        if (window.innerWidth >= 1200) {
            // Desktop
            sidebar.classList.remove('mobile-open');
            updateMobileButtonVisibility();
        } else {
            // Mobile
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('expanded');
            mobileMenuBtn.classList.remove('show-on-desktop');
            mobileMenuBtn.style.display = 'flex';
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize(); // Initial check

    // 6. NAVIGATION SECTION COLLAPSE/EXPAND
    navCollapseBtns.forEach(btn => {
        btn.addEventListener('click', function(event) {
            event.stopPropagation();
            const navSection = this.closest('.nav-section');
            navSection.classList.toggle('collapsed');
        });
    });





    
    // Function to add a message to the chat
    function addMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatArea.appendChild(messageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatArea.appendChild(typingDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
    }
    
    // Function to hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
  

    
    // Add chat to history
    function addChatToHistory(title, preview) {
        const chatHistory = document.querySelector('.chat-history');
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        chatItem.innerHTML = `
            <div class="chat-icon">
                <i class="fas fa-message"></i>
            </div>
            <div class="chat-info">
                <div class="chat-title">${title}</div>
                <div class="chat-preview">${preview}</div>
            </div>
        `;
        
        // Add click event to the new chat item
        chatItem.addEventListener('click', function() {
            updateActiveChat();
            // In a real app, you would load the chat history here
            chatArea.innerHTML = `
                <div class="message bot-message">
                    <p>Hello! I'm your SSUET Assistant. How can I help you today?</p>
                </div>
                <div class="quick-actions">
                    <div class="action-card" data-action="courses">
                        <div class="action-icon">
                            <i class="fas fa-book"></i>
                        </div>
                        <span>Course Outline</span>
                    </div>
                    <div class="action-card" data-action="exams">
                        <div class="action-icon">
                            <i class="fas fa-calendar-alt"></i>
                        </div>
                        <span>Exam Schedule</span>
                    </div>
                    <div class="action-card" data-action="contact">
                        <div class="action-icon">
                            <i class="fas fa-phone-alt"></i>
                        </div>
                        <span>Contact Department</span>
                    </div>
                    <div class="action-card" data-action="map">
                        <div class="action-icon">
                            <i class="fas fa-map-marker-alt"></i>
                        </div>
                        <span>Campus Map</span>
                    </div>
                </div>
            `;
            
            // Reattach event listeners to action cards
            document.querySelectorAll('.action-card').forEach(card => {
                card.addEventListener('click', handleActionCardClick);
            });
            
            // Close sidebar on mobile after selection
            if (window.innerWidth < 1200) {
                sidebar.classList.remove('mobile-open');
            }
        });
        
        chatHistory.insertBefore(chatItem, chatHistory.firstChild);
        
        // Limit the number of chat history items
        if (chatHistory.children.length > 10) {
            chatHistory.removeChild(chatHistory.lastChild);
        }
    }
    
    // Update active chat in sidebar
    function updateActiveChat() {
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });
        if (document.querySelector('.chat-item')) {
            document.querySelector('.chat-item').classList.add('active');
        }
    }
    
    // Update chat preview
    function updateChatPreview(message) {
        const activeChat = document.querySelector('.chat-item.active');
        if (activeChat) {
            const preview = activeChat.querySelector('.chat-preview');
            if (preview) {
                preview.textContent = message.length > 30 ? message.substring(0, 30) + '...' : message;
            }
        }
    }
    
    // // Handle action card clicks
    // function handleActionCardClick() {
    //     const action = this.getAttribute('data-action');
    //     let message = '';
        
    //     switch(action) {
    //         case 'courses':
    //             message = 'Show me course outlines';
    //             break;
    //         case 'exams':
    //             message = 'What is the exam schedule?';
    //             break;
    //         case 'contact':
    //             message = 'Contact information for departments';
    //             break;
    //         case 'map':
    //             message = 'Show me the campus map';
    //             break;
    //     }
        
    //     addMessage(message, true);
    //     botResponse(message);
    // }
    




    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Action card click handlers
    actionCards.forEach(card => {
        card.addEventListener('click', handleActionCardClick);
    });
    
    // Chat item click handlers
    chatItems.forEach(item => {
        item.addEventListener('click', function() {
            chatItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Close sidebar on mobile after selection
            if (window.innerWidth < 1200) {
                sidebar.classList.remove('mobile-open');
            }
        });
    });
    
    // Initialize with a sample chat history
    addChatToHistory("Welcome Chat", "Hello! I'm your SSUET Assistant");
});



// Collapsible navigation sections
document.addEventListener('DOMContentLoaded', function() {
const navSections = document.querySelectorAll('.nav-section');

navSections.forEach(section => {
const header = section.querySelector('.nav-section-header');
const collapseBtn = section.querySelector('.nav-collapse-btn');

// Set initial state - all sections expanded by default
section.classList.remove('collapsed');

// Calculate and set initial height
const itemsContainer = section.querySelector('.nav-items-container');
itemsContainer.style.maxHeight = itemsContainer.scrollHeight + 'px';

// Toggle collapse on header click
header.addEventListener('click', function(e) {
    // Don't trigger if clicking the button directly (handled separately)
    if (e.target.closest('.nav-collapse-btn')) return;
    
    toggleSectionCollapse(section);
});

// Toggle collapse on button click
if (collapseBtn) {
    collapseBtn.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent header click event
        toggleSectionCollapse(section);
    });
}
});

function toggleSectionCollapse(section) {
const itemsContainer = section.querySelector('.nav-items-container');

if (section.classList.contains('collapsed')) {
    // Expand
    section.classList.remove('collapsed');
    itemsContainer.style.maxHeight = itemsContainer.scrollHeight + 'px';
    
    // After transition completes, remove max-height for fluid content changes
    setTimeout(() => {
        if (!section.classList.contains('collapsed')) {
            itemsContainer.style.maxHeight = 'none';
        }
    }, 300);
} else {
    // Collapse
    itemsContainer.style.maxHeight = itemsContainer.scrollHeight + 'px';
    // Force reflow
    itemsContainer.offsetHeight;
    section.classList.add('collapsed');
    itemsContainer.style.maxHeight = '0';
}
}

// Handle window resize to recalculate heights
window.addEventListener('resize', function() {
navSections.forEach(section => {
    if (!section.classList.contains('collapsed')) {
        const itemsContainer = section.querySelector('.nav-items-container');
        itemsContainer.style.maxHeight = 'none';
        const height = itemsContainer.scrollHeight;
        itemsContainer.style.maxHeight = height + 'px';
    }
});
});
});



// Chatbot call 

function addMessage(text, isUser = false) {
    const chatArea = document.getElementById('chatArea');
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    div.innerHTML = `<p>${text}</p>`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
}


async function sendMessage() {
    const input = document.getElementById('messageInput');
    const msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, true);
    input.value = '';

    const chatArea = document.getElementById('chatArea');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `<span>Generating response...</span>`;
    chatArea.appendChild(typingDiv);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
        const res = await fetch('/get_reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg, 
                chat_id: CURRENT_CHAT_ID
                
            })
        });

        const data = await res.json();

        document.getElementById('typingIndicator')?.remove();
        addMessage(data.reply);

    } catch (err) {
        console.error(err);
        document.getElementById('typingIndicator')?.remove();
        addMessage("Server error. Please try again.");
    }
}


// Event listeners
const sendBtn = document.getElementById('sendButton');
if (sendBtn) sendBtn.addEventListener('click', sendMessage);

const messageInput = document.getElementById('messageInput');
if (messageInput) {
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}



    // Add close button to flash messages and auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flashes li');
    
    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'close-flash';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', function() {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => message.remove(), 300);
        });
        message.appendChild(closeBtn);
        
        // Auto-dismiss after 5 seconds (except for errors which are more important)
        if (!message.classList.contains('error')) {
            message.classList.add('auto-dismiss');
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 5000);
        }
    });
});



const newChatBtn = document.getElementById("newChatBtn");
const chatHistory = document.getElementById("chatHistory");

newChatBtn.addEventListener("click", () => {
    fetch("/new_chat", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            // Add new chat to sidebar
            const div = document.createElement("div");
            div.classList.add("chat-item");
            div.dataset.chatId = data.chat_id;
            div.innerHTML = `
                <div class="chat-icon"><i class="fas fa-message"></i></div>
                <div class="chat-info">
                    <div class="chat-title">${data.title}</div>
                </div>`;
            chatHistory.prepend(div);

            // Make this chat active
            loadChat(data.chat_id);
        });
});

// Load chat messages when clicking sidebar
chatHistory.addEventListener("click", (e) => {
    let item = e.target.closest(".chat-item");
    if (!item) return;
    const chat_id = item.dataset.chatId;
    loadChat(chat_id);
});

function loadChat(chat_id) {
    fetch(`/chat_messages/${chat_id}`)
        .then(res => res.json())
        .then(data => {
            const chatArea = document.getElementById("chatArea");
            chatArea.innerHTML = "";
            data.forEach(msg => {
                chatArea.innerHTML += `
                    <div class="message user-message"><p>${msg.user_message}</p></div>
                    <div class="message bot-message">${msg.bot_reply}</div>
                `;
            });
            sessionStorage.setItem("active_chat_id", chat_id);
        });
}

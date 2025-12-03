// --- TEMA DEĞİŞTİRME (Dark Mode) ---
const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const icon = themeToggle.querySelector('i');

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
});

// --- CHATBOT MANTIĞI ---
const API_URL = "https://betul-portfolio-backend.onrender.com"  ; // Backend API URL'si
// Chatbot'u Aç/Kapa
function toggleChat() {
    const chatWidget = document.getElementById('chat-widget');
    const toggleIcon = document.getElementById('toggle-icon');
    
    chatWidget.classList.toggle('closed');
    
    if (chatWidget.classList.contains('closed')) {
        toggleIcon.classList.remove('fa-chevron-down');
        toggleIcon.classList.add('fa-chevron-up');
    } else {
        toggleIcon.classList.remove('fa-chevron-up');
        toggleIcon.classList.add('fa-chevron-down');
    }
}

// "Chatbot'a Sor" butonuna basınca açılması için
function openChat() {
    const chatWidget = document.getElementById('chat-widget');
    if (chatWidget.classList.contains('closed')) {
        toggleChat();
    }
}

// Mesaj Gönderme İşlemi
async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const message = inputField.value.trim();

    if (message === "") return;

    addMessage(message, 'user-message');
    inputField.value = "";

    const loadingId = addMessage("Yanıt hazırlanıyor...", 'bot-message', true);

    try {
        // API'ye POST isteği gönder
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // Gövdeye soruyu JSON formatında ekle
            body: JSON.stringify({ question: message })
        });

        // Yükleniyor mesajını kaldır
        const loadingMsg = document.getElementById(loadingId);
        if(loadingMsg) loadingMsg.remove();
        
        if (!response.ok) {
            throw new Error(`HTTP Hata kodu: ${response.status}`);
        }

        const data = await response.json();
        
        // Gelen cevabı ekrana yazdır (data.answer)
        addMessage(data.answer, 'bot-message'); 

    } catch (error) {
        console.error("API Hatası:", error);
        const loadingMsg = document.getElementById(loadingId);
        if(loadingMsg) loadingMsg.remove();
        addMessage("API'ye ulaşılamıyor veya sunucu hatası oluştu. (Konsolu kontrol edin)", 'bot-message');
    }
}

// Enter tuşu ile gönderme
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Ekrana Mesaj Kutusu Ekleme Yardımcısı
function addMessage(text, className, isLoading = false) {
    const chatBody = document.getElementById('chat-body');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', className);
    messageDiv.innerText = text;
    
    // Yükleniyor mesajı için özel ID
    const uniqueId = 'msg-' + Date.now();
    if(isLoading) messageDiv.id = uniqueId;

    chatBody.appendChild(messageDiv);
    
    // Otomatik aşağı kaydırma
    chatBody.scrollTop = chatBody.scrollHeight;
    
    return uniqueId;
}
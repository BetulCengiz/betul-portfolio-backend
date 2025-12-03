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

    // 1. Kullanıcı mesajını ekrana ekle
    addMessage(message, 'user-message');
    inputField.value = "";

    // 2. "Yazıyor..." efekti (Simülasyon)
    const loadingId = addMessage("Yanıt hazırlanıyor...", 'bot-message', true);

    // --- BURASI DAHA SONRA PYTHON BACKEND'E BAĞLANACAK ---
    // Şimdilik sadece görsel test için gecikmeli sahte cevap veriyoruz.
    setTimeout(() => {
        // Yükleniyor mesajını kaldır
        const loadingMsg = document.getElementById(loadingId);
        if(loadingMsg) loadingMsg.remove();

        // Sahte cevap
        const mockResponse = "Şu anda Python arka yüzüme bağlı değilim, bu yüzden sadece görsel bir demoyum. Yakında RAG ve Gemini API ile gerçek cevaplar vereceğim!";
        addMessage(mockResponse, 'bot-message');
        
    }, 1500); 
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
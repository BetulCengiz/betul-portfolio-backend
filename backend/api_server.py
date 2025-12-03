# backend/api_server.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from rag_core import get_qa_chain
# --- Güvenlik ve Ayarlar ---


# ❗ Gemini API Anahtarını Ortam Değişkeninden Oku
# Canlı dağıtım için bu değişkenin Render/Cloud Run'da ayarlanması GEREKİR!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Pydantic Modeli (Veri Doğrulama) ---
class Query(BaseModel):
    """Ön yüzden gelecek JSON gövdesini (soruyu) tanımlar."""
    question: str

# --- FastAPI Uygulaması ve CORS Ayarları ---
app = FastAPI(title="Betül Cengiz AI Assistant API")

# Netlify'dan gelen isteklere izin vermek için CORS ayarı
# Canlıya almadan önce buraya Netlify URL'nizi ekleyebilirsiniz. 
# Şimdilik '*' (herkese açık) ile test edelim.
origins = [
    "*", # Geliştirme aşaması için
    # "https://betul-cengiz-portfolio.netlify.app", # CANLI URL'nizi buraya ekleyin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RAG Zinciri Kurulumu (Sunucu Başlarken Yüklenir) ---
# Global değişkenleri başlangıçta None olarak tanımlıyoruz.
retriever = None
rag_chain = None
llm = None

@app.on_event("startup")
async def startup_event():
    """
    Uygulama başladığında RAG çekirdeğini ve LLM'i yükler.
    Bu, her istekle tekrar yükleme yapılmasını engeller.
    """
    global retriever, llm, rag_chain
    
    print("API Sunucusu Başlatılıyor: RAG ve LLM yükleniyor...")
    
    # 1. RAG Retriever'ı Yükle
    try:
        retriever = get_qa_chain()
        print("RAG Retriever başarıyla yüklendi.")
    except Exception as e:
        print(f"RAG Yükleme Başarısız: {e}")
        # Uygulamanın başlamasına izin ver, ama hata durumunda kullanıcıyı bilgilendir.
        return 

    # 2. LLM Modelini Yükle (API Anahtarı Kontrolü)
    if not GEMINI_API_KEY:
        print("UYARI: GEMINI_API_KEY ortam değişkeni ayarlanmamış.")
        return 
        
    try:
        # Gemini 2.5 Flash, hızlı ve metin tabanlı RAG için idealdir.
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.1,
            api_key=GEMINI_API_KEY # Ortam değişkeninden alınan anahtarı kullan
        )
    except Exception as e:
        print(f"Gemini LLM yüklenirken hata: {e}")
        llm = None
        return

    # 3. Prompt Engineering Şablonu
    prompt_template = """
    Sen, Betül Cengiz'in profesyonel portföy chatbot'usun. 
    Aşağıda verilen 'Bağlam' (Context) içindeki bilgileri kullanarak, kullanıcının sorusuna AKICI, PROFESYONEL ve DOĞRU bir şekilde yanıt ver.
    Eğer 'Bağlam'da yeterli bilgi yoksa, kibarca bu bilgiyi özgeçmişinde bulamadığını, ancak diğer konularda yardımcı olabileceğini belirt. Asla uydurma bilgi verme.

    Bağlam:
    {context}

    Soru: {question}

    Cevap:
    """
    RAG_PROMPT = PromptTemplate.from_template(prompt_template)

    # 4. LangChain Zinciri (LCEL) Oluştur
    # Akış: Soru -> Retriever (Context) -> Prompt + Context + Soru -> LLM -> Cevap
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
    )
    print("RAG Zinciri hazırlandı ve API sunucusu kullanıma hazır.")

# --- API Uç Noktası ---

@app.post("/chat")
def chat_endpoint(query: Query):
    """Kullanıcı sorusunu alır ve LLM destekli yanıt üretir."""
    
    # Güvenlik ve Hazırlık Kontrolleri
    if not GEMINI_API_KEY:
         raise HTTPException(status_code=503, detail="API Anahtarı eksik. Lütfen GEMINI_API_KEY'i ayarlayın.")
    if retriever is None or rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG sistemi başlatılamadı veya LLM bağlantısı kurulamadı.")

    try:
        # LangChain zincirini çalıştır
        # query.question, Pydantic modeli sayesinde gelen JSON'dan alınan metindir.
        response = rag_chain.invoke(query.question)
        
        # Sadece modelin ürettiği metni (response.content) geri gönder
        return {"answer": response.content}
        
    except Exception as e:
        print(f"LLM Zinciri Çalıştırma Hatası: {e}")
        # Hata durumunda kullanıcıya genel bir mesaj gönder
        raise HTTPException(status_code=500, detail="Üzgünüm, yapay zeka yanıtı oluşturulurken bir hata oluştu.")
# backend/rag_core.py
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter 

# --- Sabitler ---
# CV metninin yolu (backend klasöründen bir üst klasöre ve data klasörüne çıkar)
# os.path.join kullanıyoruz ki işletim sistemine göre path ayracı değişse bile sorun olmasın.
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "betul_cv_data.txt")
# ChromaDB veritabanının kaydedileceği yol (backend klasöründe)
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
# Embedding Modeli (Hızlı ve etkili bir model, dağıtımda RAM dostudur)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_and_process_data():
    """
    Veriyi yükler, parçalar, vektörleştirir ve ChromaDB'de saklar.
    Veritabanı (CHROMA_DB_PATH) mevcutsa, baştan oluşturmak yerine yükler.
    """
    # 1. Embedding Modelini Yükle
    # Veritabanını kontrol etmeden önce model yüklenmeli, çünkü yükleme için de bu model lazım.
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    except Exception as e:
        print(f"HATA: Embedding modeli yüklenemedi: {e}")
        raise e
        
    # 2. Mevcut Veritabanını Kontrol Et ve Yükle
    if os.path.exists(CHROMA_DB_PATH) and len(os.listdir(CHROMA_DB_PATH)) > 0:
        print("ChromaDB veritabanı zaten mevcut. Yükleniyor...")
        # Mevcut veritabanını yükle (persist_directory'deki dosyalarla)
        return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

    print("--- Veri Yükleniyor ve İşleniyor (İlk Kurulum) ---")
    
    # 3. Veri Yükleme
    try:
        # Metin dosyasını yükle
        loader = TextLoader(DATA_PATH, encoding='utf-8')
        documents = loader.load()
    except FileNotFoundError:
        print(f"HATA: CV metin dosyası '{DATA_PATH}' bulunamadı.")
        print("Lütfen CV metninizi 'portfolio_rag/data/betul_cv_data.txt' içine kopyaladığınızdan emin olun.")
        raise FileNotFoundError(f"CV verisi maalesef bulunamadı: {DATA_PATH}")

    # 4. Parçalama (Chunking)
    # Metni 500 karakterlik parçalara ayır ve %10 (50 karakter) örtüşme sağla
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"Toplam {len(texts)} adet metin parçası oluşturuldu.")

    # 5. Veritabanına Kayıt (Vektörleştirme ve Kalıcı Kayıt)
    db = Chroma.from_documents(
        texts,
        embeddings,
        persist_directory=CHROMA_DB_PATH # Diske kaydet
    )
    db.persist() # Kaydetme işlemini tetikle
    print(f"Veri başarıyla işlendi ve '{CHROMA_DB_PATH}' konumunda saklandı.")
    
    return db

def get_qa_chain():
    """
    Vektör veritabanını yükler ve bir Retriever (Bilgi Çekme) nesnesi döndürür.
    Bu nesne, bir sorgu geldiğinde ilgili metinleri çeker.
    """
    vectorstore = load_and_process_data()
    # Retriever ayarları: k=3 en alakalı 3 adet metin parçasını çekecek
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

# --- Yerel Test Bloğu ---
if __name__ == "__main__":
    # Sanal ortamın etkin olduğundan emin olun!
    try:
        retriever = get_qa_chain()
        
        # Deneme Sorgusu
        query = "G2i'deki RLHF ve Prompt Engineering görevlerinde ana sorumluluklarım nelerdi?"
        relevant_docs = retriever.invoke(query)
        
        print("\n" + "="*50)
        print(f"SORGULANAN KELİMELER: {query}")
        print("--- Çekilen Alakalı Parçalar ---")
        
        for i, doc in enumerate(relevant_docs):
            print(f"[{i+1}] Alaka Düzeyi Yüksek Parça:")
            # Sadece metnin ilk 300 karakterini yazdır (Okunabilirlik için)
            print(doc.page_content[:300] + "...") 
            print("-" * 20)
            
    except Exception as e:
        print(f"\nKRİTİK HATA OLUŞTU: {e}")
        print("Lütfen sanal ortamın aktif olduğundan ve 'data/betul_cv_data.txt' dosyasının doğru yerde olduğundan emin olun.")
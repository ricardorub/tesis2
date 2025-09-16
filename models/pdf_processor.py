# models/pdf_processor.py

import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

class PDFProcessor:
    def __init__(self, pdf_path="tesis.pdf"):
        self.pdf_path = pdf_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Modelo ligero
        self.chunks = []
        self.embeddings = None
        self.index = None
        self._load_and_index_pdf()

    def _extract_text_from_pdf(self):
        text = ""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"Archivo {self.pdf_path} no encontrado.")
        
        with open(self.pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
        return text

    def _chunk_text(self, text, chunk_size=500):
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        return chunks

    def _load_and_index_pdf(self):
        print("🔍 Extrayendo texto del PDF...")
        text = self._extract_text_from_pdf()
        self.chunks = self._chunk_text(text)
        print(f"✅ Se extrajeron {len(self.chunks)} fragmentos.")

        if not self.chunks:
            print("⚠️  No se encontró texto en el PDF.")
            return

        print("🧠 Generando embeddings...")
        self.embeddings = self.model.encode(self.chunks)
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype(np.float32))
        print("✅ Índice FAISS creado.")

    def retrieve_relevant_chunks(self, query, k=3):
        if not self.index or len(self.chunks) == 0:
            return []
        
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        relevant_chunks = [self.chunks[i] for i in indices[0]]
        return relevant_chunks
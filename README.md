# document loading and RAG App

This project is a FastAPI-based application for document processing and question answering and interview booking. It supports two chunking strategies for document text and leverages PostgreSQL, Qdrant, and Redis for storing metadata, embeddings, and chat memory.

---

## Features

* **Document Upload**: Supports `.txt` and  pdf
* **Two Chunking Strategies**:

  * `sentences`: Split text by sentences.
  * `fixed`: Split text into fixed-size chunks.
* **Database**:

  * PostgreSQL stores document metadata and interview booking information.
* **Embeddings**:

  * Qdrant stores vector embeddings of document chunks.
* **Chat Memory**:

  * Redis stores session chat memory for contextual conversations.

---

## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/sudipmajkoti07/Chunking_rag.git
   cd Chunking_rag
   ```
get the groq api keys from here==https://console.groq.com/keys

2. **Create a `.env` file** with the following content:

   ```bash
   GROQ_API_KEY="your groq api"

   # PostgreSQL Configuration
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=documents_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432

   # Qdrant Configuration
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   QDRANT_COLLECTION=documents

   # Chunking Configuration
   FIXED_CHUNK_SIZE=500
   FIXED_CHUNK_OVERLAP=50

   # Embedding Configuration
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   EMBEDDING_DIMENSION=384

   # Redis Configuration
   REDIS_HOST=redis
   REDIS_PORT=6379
   ```

3. **Start services with Docker Compose**:

   ```bash
   docker-compose up
   ```

4. **Access FastAPI docs**:
   Open your browser and visit:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Usage

* **Upload a Document** via `/upload` endpoint and choose a chunking strategy (`sentences` or `fixed`).
* **Chat with the model** via `/chat` endpoint. It retrieves answers based on document chunks and maintains session memory using Redis and also suppoer interview booking.

---

## Notes

* Ensure your `.env` file contains valid API keys and database credentials.
* PostgreSQL is used for storing documents and bookings metadata.
* Qdrant stores vector embeddings for semantic search.
* Redis handles temporary chat memory for conversation context.

---

This setup allows running a **RAG-based agentic chatbot** with document retrieval and interview booking capabilities.

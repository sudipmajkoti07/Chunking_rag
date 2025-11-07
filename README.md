# Chunking RAG App with Interview Booking

This is a **FastAPI-based application** for document processing, RAG-based question answering, and interview booking. It uses PostgreSQL to store document metadata and bookings, Qdrant for document embeddings, and Redis for chat memory.
you need to have docker in your laptop
---

## Features

* **Document Upload**: Upload documents like txt and pdf
* **Chunking Strategies**:

  * `sentences`: Split text by sentences.
  * `fixed`: Split text into fixed-length chunks.
* **Retrieval-Augmented Generation (RAG)**:

  * Searches relevant document chunks in Qdrant.
  * Generates answers with context from documents and previous chat memory.
* **Interview Booking**:

  * Collects user details: name, email, date, time.
  * Saves confirmed bookings to PostgreSQL.
* **Chat Memory**:

  * Redis stores last conversations for contextual replies.

---

## Technologies Used

* **FastAPI** – backend API framework
* **PostgreSQL** – stores document metadata and interview bookings
* **Qdrant** – stores vector embeddings for RAG
* **Redis** – stores chat memory for session context
* **LangChain + ChatGroq** – LLM integration
* **Sentence Transformers** – embedding generation

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


## Usage

* **Upload Document**: Use `/upload` endpoint, choose `sentences` or `fixed` chunking.
* **Chat with the Bot**: Use `/chat` endpoint:

  * Bot identifies intent (`rag`, `interview`, `general`).
  * Routes user input to the corresponding handler:

    * `rag`: Retrieves document chunks from Qdrant for answers.
    * `interview`: Collects booking details and saves confirmed bookings to PostgreSQL.
    * `general`: Casual conversation stored in Redis for context.

---

## Notes

* Ensure `.env` contains valid credentials.
* PostgreSQL stores **documents and bookings**.
* Qdrant stores **vector embeddings** for semantic search.
* Redis stores **recent conversation memory** for chat context.
* Two chunking strategies allow flexibility for document processing.

---

This setup enables a **RAG-powered agentic chatbot** with document retrieval, conversational memory, and interactive interview booking.


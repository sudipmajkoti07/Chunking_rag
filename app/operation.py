# app/operation.py

import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
import redis
from dotenv import load_dotenv
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import init_chat_model
from typing import Literal
from pydantic import BaseModel, Field
from .database import Base, engine, SessionLocal
from .models import InterviewBooking_table


Base.metadata.create_all(bind=engine)

# Load environment variables from .env
load_dotenv()

# --------------------------
# Configuration
# --------------------------
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COLLECTION_NAME = "document_embeddings"
MAX_MEMORY = 10

# --------------------------
# Qdrant setup
# --------------------------
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------
# Groq LLM setup
# --------------------------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile"
)

# --------------------------
# Redis setup for chat memory
# --------------------------
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


# --------------------------
# Pydantic Models
# --------------------------
class IntentAnalysis(BaseModel):
    """
    Analyzes the user's input to determine whether a vector store retrieval is required.
    """
    intent: Literal['rag', 'interview', 'general'] = Field(
        description="Classified intent of the user's input: 'rag' for retrieval-augmented generation, 'interview' for interview booking, 'general' for casual conversation."
    )


class InterviewBooking(BaseModel):
    """
    Collects user details for booking an interview.
    """
    name: str = Field(description="Full name of the person booking the interview")
    email: str = Field(description="Email address of the person booking the interview")
    date: str = Field(description="Date of the interview like 2025-12-12 etc")
    time: str = Field(description="Time of the interview in HH:MM format like 12 pm etc")
    confirm: Literal['Yes', 'No'] = Field(
        description="Indicates whether the user confirms the booking. Use 'Yes' if user has confirmed it otherwise say 'No'."
    )


Intent_llm = llm.with_structured_output(IntentAnalysis)
Interview_llm = llm.with_structured_output(InterviewBooking)


# --------------------------
# Helper Functions
# --------------------------
def get_conversation_history(session_id):
    """Retrieve conversation history from Redis."""
    memory_key = f"chat:{session_id}"
    return r.lrange(memory_key, -MAX_MEMORY, -1)


def store_conversation(session_id, user_input, assistant_response):
    """Store conversation in Redis."""
    memory_key = f"chat:{session_id}"
    r.rpush(memory_key, f"User: {user_input}")
    r.rpush(memory_key, f"Assistant: {assistant_response}")
    # Set expiration to 24 hours
    r.expire(memory_key, 86400)


# --------------------------
# RAG Function
# --------------------------
def rag(user_input, top_k=3, session_id="default"):
    """
    Retrieve relevant documents and generate answer using RAG.
    """
    try:
        # 1. Search Qdrant for relevant chunks
        embedding = MODEL.encode([user_input]).tolist()[0]
        results = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=top_k
        )
        
        # Extract text from results
        chunks = [hit.payload.get("text", "") for hit in results if hit.payload.get("text")]
        
        if not chunks:
            chunks = ["No relevant information found in the knowledge base."]

        # 2. Get conversation history
        last_conversations = get_conversation_history(session_id)
        history_text = "\n".join(last_conversations) if last_conversations else "No previous conversation."

        # 3. Construct prompt
        prompt = f"""You are a helpful assistant. Use the information below to answer the user's question.

User Question:
{user_input}

Last Conversations (from memory):
{history_text}

Relevant Document Chunks:
{chr(10).join(chunks)}

Instructions:
- Use the last conversations and document chunks to answer.
- If information is insufficient, answer from your general knowledge but mention this.
- Be concise and accurate.
"""

        # 4. Prepare messages
        system_msg = SystemMessage(content="You are a helpful assistant.")
        human_msg = HumanMessage(content=prompt)
        messages = [system_msg, human_msg]

        # 5. Invoke LLM
        ai_response = llm.invoke(messages)
        answer = ai_response.content

        # 6. Store conversation in Redis
        store_conversation(session_id, user_input, answer)

        return answer
    
    except Exception as e:
        return f"I encountered an error while processing your request. Please try again."


# --------------------------
# Interview Booking Function
# --------------------------
def setup_interview(user_input, session_id="default"):
    """
    Handle interview booking process with conversation memory.
    """
    try:
        # 1. Get conversation history
        last_conversations = get_conversation_history(session_id)
        history_text = "\n".join(last_conversations) if last_conversations else "No previous conversation."

        # 2. Construct prompt
        prompt = f"""You are an interview booking agent.
You need these details to book: name, email, date like 2025-12-12 etc, time like 12 pm etc
do not ask about which interview it is for.

Process:
1. Collect missing information one at a time politely
2. After receiving all details, ask for confirmation
3. After user confirms, thank them for booking
4. Be concise and respond in short sentences
5. don't ask the reason of booking the interview
and once confirmed, save the details to the database.
and once confirmed it don't ask any more questions.

User Question:
{user_input}

Last Conversations (from memory):
{history_text}

Instructions:
- Be concise and accurate.
- Guide the user step by step.
make response short and precise
"""

        # 3. Prepare messages
        system_msg = SystemMessage(content="You are an interview booking agent.")
        human_msg = HumanMessage(content=prompt)
        messages = [system_msg, human_msg]

        # 4. Invoke LLM
        ai_response = llm.invoke(messages)
        answer = ai_response.content

        # 5. Try to extract structured booking data from conversation context
        try:
            # Combine history with current conversation for context
            full_context = f"{history_text}\nUser: {user_input}\nAssistant: {answer}"
            interview_details = Interview_llm.invoke(full_context)
            
            # 6. If confirmed, save to database
            if interview_details.confirm == 'Yes':
                name = interview_details.name
                email = interview_details.email
                date = interview_details.date
                time = interview_details.time

                db = SessionLocal()
                try:
                    # Save to Postgres
                    doc = InterviewBooking_table(name=name, email=email, date=date, time=time)
                    db.add(doc)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    return "There was an error saving your booking. Please try again."
                finally:
                    db.close()
        
        except Exception as e:
            # Not ready for booking yet (missing info or not confirmed)
            pass

        # 7. Store conversation in Redis
        store_conversation(session_id, user_input, answer)

        return answer
    
    except Exception as e:
        return "I encountered an error processing your booking request. Please try again."


# --------------------------
# General Conversation Function
# --------------------------
def general_conversation(user_input, session_id="default"):
    """
    Handle general conversation that doesn't require RAG or booking.
    """
    try:
        # Get conversation history
        last_conversations = get_conversation_history(session_id)
        history_text = "\n".join(last_conversations[-6:]) if last_conversations else "No previous conversation."
        
        # Construct prompt
        prompt = f"""You are a friendly and helpful assistant.

Conversation History:
{history_text}

User: {user_input}

Instructions:
- Respond naturally and helpfully
- Keep the conversation engaging
- Be concise
"""
        
        # Prepare messages
        system_msg = SystemMessage(content="You are a friendly and helpful assistant.")
        human_msg = HumanMessage(content=prompt)
        messages = [system_msg, human_msg]
        
        # Invoke LLM
        ai_response = llm.invoke(messages)
        answer = ai_response.content
        
        # Store conversation
        store_conversation(session_id, user_input, answer)
        
        return answer
    
    except Exception as e:
        return "I'm having trouble responding right now. Please try again."


# --------------------------
# Main Chatbot Query Function
# --------------------------
def query_chatbot(user_input, session_id="default"):
    """
    Main entry point for chatbot queries with intent classification.
    """
    # Validate input
    if not user_input or not user_input.strip():
        return "Please provide a valid question or request."
    
    try:
        # 1. Classify user intent
        intent_analysis = Intent_llm.invoke(user_input)
        
        # 2. Route to appropriate handler based on intent
        if intent_analysis.intent == 'interview':
            return setup_interview(user_input, session_id)
        elif intent_analysis.intent == 'rag':
            return rag(user_input, session_id=session_id)
        elif intent_analysis.intent == 'general':
            return general_conversation(user_input, session_id)
        else:
            return "Sorry, I couldn't understand your request. Could you please rephrase?"
    
    except Exception as e:
        return "I encountered an error. Please try again or rephrase your question."
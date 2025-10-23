# 📚 **Check-In: AI-based Smart Bookstore**

> A hybrid AI-powered online bookstore that integrates **Spring Boot** with an **LLM-based recommendation system**.  
> Provides a comprehensive shopping platform for users and admins, featuring an **AI chatbot** for intelligent, emotion-aware book recommendations.

---

## 🧭 Overview
This project combines a traditional bookstore backend with an AI microservice for personalized book discovery.  
The AI module uses **RAG (Retrieval-Augmented Generation)**, **LangChain**, and **ChromaDB** to deliver context-aware, emotion-sensitive recommendations.

### ✨ Key Features
- 🤖 **AI Book Recommendation Chatbot (RAG + LLM)**
- 🧠 **Emotion-aware personalized recommendations**
- 🔍 **Hybrid search engine (Vector + Keyword)**
- 🧩 **Multi-agent architecture** (Intent → Recommendation / Wiki / Default)
- ⚙️ **Session-based dialogue memory**

---

## 🛠 Tech Stack

### **Backend (Spring Boot)**
- Java 17, Spring Boot 3.3.1  
- Spring Data JPA, Hibernate  
- MySQL 8.0 (RDS-compatible)

### **AI Service (FastAPI)**
- Python 3.11+, FastAPI  
- LangChain for LLM orchestration  
- OpenAI GPT-4 for conversation generation  
- ChromaDB as vector database  
- OpenAI Embeddings for semantic similarity  

### **Development Tools**
- IntelliJ IDEA / VS Code  
- Maven, Git & GitHub  
- MySQL Workbench  
- REST API testing via Postman  

---

## ✨ Core AI Features

### 🤖 **Chatbot Capabilities**
- Emotion-based personalized book recommendations  
- Natural language understanding for flexible queries  
- Hybrid retrieval (semantic + keyword search)  
- Contextual RAG response generation  
- Intent classification & query analysis  
- Session-based memory for ongoing conversations  
- Real-time clarification and fallback handling  

---

## 🧠 AI Agent Modules

| Agent | Description | Key Files |
|--------|-------------|------------|
| 🧩 **Main Agent** | Handles session, intent classification, and routing | `main_agent.py`, `intent_router.py` |
| 💡 **Recommend Agent** | Emotion, genre, keyword-based retrieval; MMR reranking | `recommend_agent.py` |
| 📚 **Wiki Search Agent** | Fetches author & book metadata, structured responses | `wiki_search_agent.py` |

### 🧩 Example Workflow
```
User → /api/chat → Main Agent
           ↓
   ├── Recommend Agent (vector + keyword + MMR)
   ├── Wiki Agent (metadata query)
   └── Default LLM response
           ↓
       Contextual Answer (RAG)
```
---

## 🧩 API Reference

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|----------|-----------|
| POST | `/api/chat` | Send chat message | `{ "message": "I'm feeling down, any book recs?" }` | `{ "response": "Try 'The Power of Now' by Eckhart Tolle.", "success": true }` |
| GET | `/health` | Health check | - | `{ "status": "healthy" }` |

---

## 🧱 Architecture Diagram
```
┌───────────────────┐    ┌────────────────────┐
│   Spring Boot     │    │     FastAPI AI     │
│  (Main Service)   │──► │   (Microservice)   │
│                   │    │                    │
│ REST Controller   │    │  LangChain Agents  │
│ User Session Mgmt │    │  RAG + ChromaDB    │
└───────────────────┘    └────────────────────┘
```

---

## 🚀 Run Locally (AI Service)
```bash
cd ai-service
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
python main.py
```
### Environment Variables (.env)
```
OPENAI_API_KEY=your_api_key
CHROMA_DB_PATH=./data/chroma_db
COLLECTION_NAME=bookstore_collection
FAST_API_HOST=0.0.0.0
FAST_API_PORT=8000
```
```
Access:

AI API → http://localhost:8000/api/chat

Health Check → http://localhost:8000/health
```

## 📊 Retrieval & Reranking

Hybrid search: semantic (Chroma) + keyword (BM25)

MMR for diversity (k=3, λ=0.7)

Emotion weighting: +4 for mood keywords, +3 for genre relevance

Fallbacks: vector → keyword → default GPT answer

Caching: query response caching (TTL 30s)

---

## 📈 Results

- Improved retrieval precision through emotion-aware reranking
- Reliable response flow with fallback/retry logic


### 🖥️ Demo Example

Below is a real interaction with the **AI book recommendation chatbot**, demonstrating emotion-aware retrieval and natural-language response generation.

<img width="945" height="384" alt="CheckIn_Demo" src="https://github.com/user-attachments/assets/7b5c091c-7d3d-4089-8776-c1de02346aca" />

> **Figure 1.** The AI chatbot (FastAPI + LangChain + Chroma) responds to the Korean prompt *“자신감을 얻을 수 있는 책을 추천해줘”* by recommending *“You’re Trying Too Hard”* (래릿, 손명재) with an explanation focused on emotional resilience.
```
🗣️ **User input:**  
> 자신감을 얻을 수 있는 책을 추천해줘  

💬 **Chatbot response:**  
> 1. 당신은 너무 잘 살려고 한다 — 래릿(손명재)  
> 추천 이유: 이 책은 자신감을 키우고 불안, 우울, 후회, 무기력에 흔들리지 않는 멘탈을 관리하는 방법을 제시하고 있습니다.
```
This example illustrates the chatbot’s ability to interpret user emotion and provide contextual, meaningful book recommendations in natural language.



---

## 💡 Summary

Designed and implemented an AI multi-agent recommendation system with hybrid retrieval, emotion-based reranking, and robust fallback handling, forming the core of the AI Smart Bookstore.

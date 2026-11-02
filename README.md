<div align="center">

# 🤖 Portfolio-AI-Multi-Agent-RAG

### *Your Personal AI Career Representative — Recruiters Ask, AI Answers!* 💼🤖

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2-1C3C3C?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![RAG](https://img.shields.io/badge/RAG-Vector_Search-4285F4?logo=google&logoColor=white)](https://www.trychroma.com/)
[![Groq AI](https://img.shields.io/badge/Groq_AI-F5C542?logo=groq&logoColor=white)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?logo=chroma&logoColor=white)](https://www.trychroma.com/)

</div>

> 💬 **"Tell me about your strongest AI project."**  
> 🎯 *Supervisor: "Project deep-dive requested — routing to Project Agent..."*  
> 🔍 *RAG: Retrieving top 3 resume sections from the knowledge base...*  

**I've built this Portfolio Agent — an AI recruitment multi-agent system with RAG that represents a real job candidate. where a Supervisor routes every recruiter question to specialized agents: Recruiter, Technical, Project, and Career. A ChromaDB-powered RAG pipeline grounds every answer in real resume data. Recruiters and HR can explore qualifications, projects, and experience through natural conversation — instantly.**

<div align="center">

[![🚀 Live Demo](https://img.shields.io/badge/🚀_Try_The_AI_Recruiter-Click_Here-2ea44f?style=for-the-badge&logo=vercel&logoColor=white)](https://portfolio-ai-fullstack1.vercel.app/)

</div>

---

## 🧠 Why This Is a TRUE Multi-Agent RAG System

Most portfolio chatbots just stuff a resume into a prompt. This system uses **specialized agents + semantic retrieval** to answer like a real career representative:

| 🧠 Agent Capability | 💼 How This Agent Uses It |
|---------------------|---------------------------|
| 🎯 **Supervisor Orchestration** | A Supervisor agent reads the conversation and routes each question to the right specialist |
| 👔 **Recruiter Agent** | Handles introductions, availability, and general candidate questions |
| 🛠️ **Technical Skills Agent** | Deep-dives into tech stack, AI/ML experience, and engineering skills |
| 📂 **Project Agent** | Gives detailed walkthroughs of projects — architecture, tech, and outcomes |
| 🎓 **Career Agent** | Answers education, career goals, and contact questions |
| 🔍 **RAG Pipeline** | ChromaDB vector search retrieves only the most relevant resume chunks — no prompt stuffing |
| 💬 **Context Memory** | Multi-turn conversations with full context awareness |
| 🚦 **Smart Routing** | Conditional edges route questions based on intent — not hardcoded logic |

---

## ✨ Features

- 🤖 **Multi-Agent Architecture** — Supervisor + 4 specialist agents collaborating in real-time
- 🔍 **RAG-Powered Answers** — ChromaDB vector search over semantically chunked resume data
- 🧩 **Semantic Chunking** — Resume split into meaningful, self-contained knowledge chunks
- 🎯 **Intent-Aware Routing** — Questions routed to the right specialist agent automatically
- 💬 **Multi-Turn Conversations** — Full context memory across the entire chat session
- 📄 **Source-Backed Answers** — Responses grounded in retrieved resume sections
- 🚫 **Graceful Boundaries** — Politely handles off-topic questions
- ⚡ **Groq LLM Speed** — Lightning-fast inference with GPT-OSS-120B
- 🌐 **Full-Stack Experience** — FastAPI + LangGraph backend, React Vite glassy chat frontend
- 🔒 **Structured Outputs** — Pydantic models for reliable, parseable agent responses

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| 🤖 **AI Agents** | LangGraph, LangChain Core |
| 🧠 **LLM** | Groq AI (GPT-OSS-120B) |
| 🔍 **RAG** | ChromaDB, Sentence Transformers |
| ⚙️ **Backend** | Python, FastAPI, Uvicorn |
| 💻 **Frontend** | React 18, Vite, Tailwind CSS |
| 🔌 **API** | RESTful APIs, Axios |
| 🚀 **Deployment** | Vercel (Frontend), Render (Backend) |
| ✅ **Validation** | Pydantic, Structured Outputs |

---

## 🔄 Multi-Agent Workflow

```text
                    ┌─────────────────┐
                    │   Supervisor    │◀──────────────┐
                    │ (Orchestrator)  │               │
                    └────────┬────────┘               │
                             │                        │
        ┌────────────────────┼────────────────────┐   │
        ▼                    ▼                    ▼   │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Recruiter   │    │  Technical   │    │   Project    │
│    Agent     │    │ Skills Agent │    │    Agent     │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Career Agent   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   RAG Pipeline  │
                  │   (ChromaDB)    │
                  └────────┬────────┘
                           │
                           ▼
                         END
```

### 🧠 **The Supervisor is the Brain**

Every user question hits the Supervisor first. It reads the intent and routes to the right specialist:

> *"Is this a general intro question? → Recruiter Agent. A deep tech question? → Technical Skills Agent. A project walkthrough? → Project Agent. Career/contact info? → Career Agent."*

**That's what makes it a multi-agent system, not a chatbot.**

---

## 🔍 How RAG Works Here

```text
User: "Tell me about the AI projects"
        │
        ▼
┌──────────────┐
│ LLM Router   │──▶ RAG Pipeline
└──────────────┘        │
                        ▼
            ┌─────────────────────────┐
            │ 1. Chunk resume into    │
            │    meaningful sections  │
            │ 2. Embed + store in     │
            │    ChromaDB             │
            │ 3. Retrieve top 3       │
            │    relevant chunks      │
            │ 4. LLM answers with     │
            │    only that context    │
            └─────────────────────────┘
```

**No prompt stuffing. No hallucinations. Just precise, source-backed answers.**

---

## 🎬 See the Agents in Action

### 👔 **Recruiter Agent**
```text
🧑 "Tell me about yourself"
🤖 "I'm an AI Agent Full-Stack Developer with hands-on experience in Python, LangGraph, FastAPI, and React. I've built and deployed multiple AI agents including a Restaurant Order Agent and this Portfolio Assistant..."
```

### 🛠️ **Technical Skills Agent**
```text
🧑 "Explain your LangGraph experience"
🤖 "I use LangGraph StateGraph to build autonomous agent workflows with conditional edges, structured outputs via Pydantic, and LLM-managed retry logic — as demonstrated in my Restaurant Order Agent..."
```

### 📂 **Project Agent**
```text
🧑 "Walk me through the Restaurant Order Agent"
🤖 "The Restaurant Order Agent is a LangGraph-powered system with a full order lifecycle: user_input → llm → order_confirm → cook → serve. It features live inventory, fuzzy dish matching, partial order handling, and intelligent retry logic..."
```

### 🎓 **Career Agent**
```text
🧑 "What's your education background?"
🤖 "I have a strong foundation in computer science with hands-on expertise across AI, full-stack development, and cloud deployment..."
```

### 🚫 **Knows Its Boundaries**
```text
🧑 "What's the capital of France?"
🤖 "I'm an AI portfolio assistant — I can answer questions about skills, projects, and experience. What would you like to know?"
```

---

## 🧪 Test the Agents

Try these conversation flows:

```text
1. "Tell me about yourself"                    → Recruiter Agent
2. "What AI projects have you built?"          → Project Agent
3. "Explain your LangGraph experience"         → Technical Skills Agent
4. "What's your tech stack?"                   → Technical Skills Agent
5. "Walk me through the Restaurant Agent"      → Project Agent
6. "What are your career goals?"               → Career Agent
7. "How can I contact you?"                    → Career Agent
8. "What's the weather?"                       → Polite boundary
```

---

## 🧠 Key Concepts Demonstrated

- **LangGraph Multi-Agent Systems** — Supervisor + specialist agent orchestration
- **RAG Pipeline** — ChromaDB vector search with semantic chunking
- **Conditional Edges** — Dynamic routing driven by LLM decisions
- **Structured Outputs** — Pydantic models for reliable agent responses
- **Message Memory** — `add_messages` annotation for multi-turn conversations
- **Semantic Chunking** — Resume split into meaningful, self-contained knowledge chunks
- **Full-Stack Integration** — FastAPI + React connected via RESTful APIs

---

## 🚀 Deployment

### **Backend (Render)**
| Setting | Value |
|---------|-------|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn api:app --host 0.0.0.0 --port $PORT` |
| Environment Variable | `GROQ_API_KEY` |

### **Frontend (Vercel)**
| Setting | Value |
|---------|-------|
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Environment Variable | `VITE_API_URL=https://your-backend.onrender.com` |

---

## 🤝 Contributing

Contributions are welcome! 🎉

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔃 Open a Pull Request
---

## 👨‍💻 Author

**AssassinjackM4**  
🤖 AI Agent Full-Stack Developer

- 💼 [LinkedIn](https://www.linkedin.com/in/aniket-meshram-0515a3223)
- 💻 [GitHub](https://github.com/AssassinjackM4)
- 🌐 [Live Portfolio](https://portfolio-ai-fullstack1.vercel.app/)

---

<div align="center">

### 💼 *Recruiters Ask. AI Answers.* 🤖

**⭐ Star this repo if you found it helpful!**

Built with ❤️ using LangGraph, Groq AI, ChromaDB, FastAPI & React

</div>

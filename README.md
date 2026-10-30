# Summative Lab: Local RAG-Powered Knowledge Assistant
Example of a RAG-powered knowledge assistant, built for Flatiron SE-FND2-FT Module 32 Summative. README adapted from source README, with my responses to the questions.


## Tools and Resources

You will use:

- Python 3.10+
- Flask
- React + Vite
- Node.js and npm
- Chroma or the approved local vector store included in the starter
- Ollama or another approved local model service
- Git and GitHub
- A `.env` file for configuration

Recommended Ollama models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Project Structure

```text
summative-rag-knowledge-assistant-starter/
├── client/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
├── server/
│   ├── app.py
│   ├── config.py
│   ├── documents.py
│   ├── rag_service.py
│   ├── seed_knowledge_base.py
│   ├── vector_store.py
│   ├── requirements.txt
│   ├── Pipfile
│   ├── .env.example
│   └── knowledge_base/
│       ├── onboarding.txt
│       ├── product_support.txt
│       ├── security_guidelines.txt
│       └── workplace_faq.txt
└── README.md
```

---

#### Response: Problem Definition

The company needs an internal assistant that provides quick, source-backed responses to employee questions. This helps reduce the amount of work required from help desk associates, who may have to answer many repetitive, basic questions over and over again. This also enables employees to find answers on their own when they know it's already available in the documentation, but they aren't sure how to find it themselves.

---

#### Response: Design Notes

```text
User browser
→ React frontend
→ Flask /api/ask route
→ RAG workflow
→ Vector database retrieval
→ Model service
→ Answer and sources returned to frontend
```

---

#### Response: Sample Questions and Observations

| Sample Question | Was the Answer Relevant? | Were Useful Sources Returned? | Notes |
|---|---|---|---|
| What should I do if I cannot log into the product dashboard? | Yes. It gave ordered, clear instructions. | Yes. The sources directly cited were included. | The answer still included some unhelpful information at the end pertaining to if the customer was missing account information, which is not relevant to their ability to log in. |
| What should employees do with suspicious emails? | Yes. It gave direct instructions. | Yes. It returned multiple sources from the same document about security. | The model essentially repeated the instructions a second time, without numbering the steps, to fill out space. |
| What should a support agent do if the knowledge base does not answer a question? | Yes. It gives clear instructions. | Yes. It even specifies the sources in the answer text. | Slightly repetitive.  |

Overall, I think the prompt would benefit from being changed to guide the model to not repeat itself or add information to give a longer response. Given the short sources provided for this example lab, it doesn't have much information to work with.

---

## Setup Instructions

### 1. Start Ollama

In a terminal, confirm Ollama is running and pull the recommended models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
ollama run llama3.2 "Reply with one short sentence."
```

### 2. Set Up the Flask Backend

From the project root:

```bash
cd server
pipenv install
pipenv shell
cp .env.example .env
```

### 3. Seed the Knowledge Base

To initialize the database, run:

```bash
python seed_knowledge_base.py
```

This script loads the provided knowledge base files, chunks the text, creates embeddings, and stores the chunks in the vector database.

### 4. Run the Flask Backend

```bash
flask --app app run --debug --port 5555
```

You should be able to visit:

```text
http://localhost:5555/api/health
```

Expected response:

```json
{
  "message": "Backend is running.",
  "status": "ok"
}
```

### 5. Set Up and Run the React Frontend

Open a second terminal from the project root:

```bash
cd client
npm install
npm run dev
```

Open the local frontend URL shown in your terminal. It is usually:

```text
http://localhost:5173
```

---

## API Routes

### GET `/api/health`

Confirms that the backend is running.

Expected response:

```json
{
  "status": "ok",
  "message": "Backend is running."
}
```

### POST `/api/ask`

Receives a user question and returns an answer with sources.

Expected request body:

```json
{
  "question": "What should I do if I cannot log into the product dashboard?"
}
```

Expected response format:

```json
{
  "answer": "A helpful answer grounded in the knowledge base.",
  "sources": [
    {
      "title": "Product Support Guide",
      "source": "product_support.txt",
      "chunk_index": 0,
      "excerpt": "Relevant source excerpt..."
    }
  ]
}
```

---

## Environment Variables

Create your local `.env` file from `server/.env.example`.

| Variable | Purpose |
|---|---|
| `OLLAMA_BASE_URL` | URL for the local model service |
| `GENERATION_MODEL` | Model used to generate answers |
| `EMBEDDING_MODEL` | Model used to create embeddings |
| `CHROMA_PATH` | Local folder where Chroma stores vector data |
| `COLLECTION_NAME` | Name of the vector collection |
| `KNOWLEDGE_BASE_PATH` | Folder containing source documents |
| `TOP_K` | Number of chunks to retrieve |
| `TEMPERATURE` | Controls response variation |
| `CLIENT_ORIGIN` | Local frontend origin allowed by the backend |

Example values:

```text
OLLAMA_BASE_URL=http://localhost:11434
GENERATION_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text
CHROMA_PATH=./chroma_db
COLLECTION_NAME=knowledge_assistant
KNOWLEDGE_BASE_PATH=./knowledge_base
TOP_K=3
TEMPERATURE=0.2
CLIENT_ORIGIN=http://localhost:5173
```

---

## Knowledge Base Files

The starter app includes these source files:

- `server/knowledge_base/onboarding.txt`
- `server/knowledge_base/product_support.txt`
- `server/knowledge_base/security_guidelines.txt`
- `server/knowledge_base/workplace_faq.txt`

These files are the approved source content for the assistant. The RAG workflow should retrieve from these files and return sources that help users understand where the answer came from.

---

## RAG Workflow Description

The frontend sends a request to the Flask /api/ask route with the question in the JSON body.
The backend verifies the question and sends it to the RAG service.
The RAG service retrieves and formats relevant chunks from the vector database.
The chunks are combined with the user's question and system instructions to form a prompt.
The prompt, including chunks and question, is send to the model.
The backend accepts the model's answer and returns it, along with supporting sources, to the frontend.


# Natural Language Action Agent

An enterprise-grade, offline-first Python backend system built with **FastAPI** and **Pydantic v2** that converts natural language user instructions into structured JSON actions, validates them strictly through a **Device Registry**, and executes safe monitoring actions against an in-memory store.

---

## 1. Solution Approach

Directly connecting Large Language Models (LLMs) to system execution code poses severe security and reliability risks: LLMs can hallucinate non-existent hardware, attempt unverified actions, or succumb to prompt injection attacks.

To solve this, our application enforces a strict **separation of responsibilities**:

```
Natural Language Input
       │
       ▼
 ┌───────────┐
 │ LLM Layer │  ──► Intent Extraction Only (`understood_as`)
 └─────┬─────┘
       │ Candidate Structured JSON
       ▼
 ┌───────────┐
 │  Backend  │  ──► Pydantic Schema Validation
 │  Safety   │  ──► Device Registry Verification (`devices.json`)
 │ Validation│  ──► Prompt Injection & Boundary Checks
 └─────┬─────┘
       │ Validated Action
       ▼
 ┌───────────┐
 │ Execution │  ──► In-Memory Store & State Response
 └───────────┘
```

- **LLM Responsibility**: Translates English text into a candidate structured JSON action dictionary (`understood_as`).
- **Backend Application Responsibility**: Owns safety, schema validation, device registry verification, parameter bounds checking, prompt injection defense, and state execution.

---

## 2. Architecture

```
                    USER
                     │
                     ▼
             POST /command
                     │
                     ▼
          ┌─────────────────────┐
          │     FastAPI         │
          │   API Layer         │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Prompt Injection &  │
          │   Input Guard       │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Offline LLM Parser │
          │ (Ollama / Offline)  │
          └──────────┬──────────┘
                     │
          Candidate Structured Action (`understood_as`)
                     │
                     ▼
          ┌─────────────────────┐
          │ Pydantic Schema     │
          │   Validation        │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Device Registry     │
          │ Validation          │
          └──────────┬──────────┘
                     │
             ┌───────┴────────┐
             │                │
           VALID           INVALID
             │                │
             ▼                ▼
      ┌─────────────┐   Clear Error
      │ Action      │   Response
      │ Executor    │
      └──────┬──────┘
             │
             ▼
      In-Memory Store
             │
             ▼
          Response

GET /rules ──► Stored Alert Rules
```


## 3. LLM Integration

The application features an **Offline-First LLM Architecture** configured via `.env`:

- **Built-in Offline Parser (`LLM_PROVIDER=offline`)**: Default provider. Uses local pattern matching and slot extraction to parse natural language instructions 100% offline with zero external dependencies, making automated test suites fast and reproducible.
- **Ollama Local LLM (`LLM_PROVIDER=ollama`)**: Connects to a local Ollama daemon (`http://localhost:11434`) running models like `llama3.2` or `qwen2.5` using JSON output mode (`format="json"`). If Ollama is unreachable, it automatically falls back to the builtin offline parser.
- **OpenAI Provider (`LLM_PROVIDER=openai`)**: Optional online provider via `OPENAI_API_KEY`.

---

## 4. Testing & Running the Application

### 1. Run Automated Test Suite
Execute the full automated test suite using `pytest`:

```bash
py -m pytest -v
```

### 2. Start Application Server (Uvicorn)
Start the FastAPI application using the Uvicorn web server:

```bash
py -m uvicorn app.main:app --port 8000 --reload
```
- Open the visual web dashboard playground at `http://127.0.0.1:8000`.
- Access interactive OpenAPI docs at `http://127.0.0.1:8000/docs`.





## 5. Design Decisions

1. **Decoupled Architecture**: Strictly isolating LLM intent parsing from backend execution prevents hallucinated execution and unauthorized state changes.
2. **Offline-First Default**: Providing a built-in offline parser ensures zero-dependency execution, instant test suite completion (0.10s), and resilience against network timeouts.
3. **Thread-Safe In-Memory Store**: Uses `threading.Lock` for memory operations to ensure thread safety without requiring database setup overhead.
4. **Interactive Web Dashboard**: Serving a glassmorphism dark-mode UI at `/` provides single-click verification of all key test cases and real-time visualization of LLM parsing and backend validation outputs.

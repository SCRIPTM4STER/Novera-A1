# 🤖 Novera-A1

**Novera-A1** is a highly intelligent AI assistant engineered to understand natural human speech and respond with precise, context-aware answers. Designed for speed, emotional depth, and humanlike interaction, Novera-A1 transcends traditional AI systems by offering:

- Dynamic, flowing conversations  
- Rational decision-making  
- Real-time adaptability to user needs

It is your most intuitive and responsive digital companion — whether executing complex tasks, solving problems, or assisting with daily routines.

—

## ✨ Name & Vision

**Novera-A1**: “Novera” is derived from the Latin word “Nova” (new) and the English word “Era,” symbolizing a new era of intelligent assistance and innovation.

—

## ⚙️ Core Architecture

Novera-A1 operates through a modular **six-part architecture**, each designed to maximize a specific aspect of intelligence and interaction:

### 1. 🧠 Decision Core
Mimics human-like reasoning to interpret input and decide what to do next. It classifies user queries into actionable intents (e.g., `general`, `realtime`, `open`, `close`, `reminder`, etc.) without producing the final answer itself.

High-level flow:
- Receives raw user input
- Uses a reasoning model to classify/query-type decisions
- Emits normalized intents like: `general how are you?`, `open chrome`, `reminder 9:00pm 25th June business meeting`

See details in Decision Core section below.

### 2. 🗂️ Task Orchestrator (Router)
Parses Decision Core outputs, classifies them into task types (LLM, app control, media, generation, scheduler, system, search), and dispatches to the appropriate handler. This enables clean separation between intent detection and execution logic.

### 3. 📚 Knowledge Vault
Combines preloaded data, real-time retrieval, and fast-access caching. Can draw from APIs or internal embeddings.

### 4. 🧩 Context Engine
Maintains dialogue flow and (planned) emotional context, adapting tone and phrasing.

### 5. ⚡ Action Layer
Executes tasks and returns results via text, voice, or control logic with low latency.

### 6. 🔁 Feedback Loop
Learns from usage patterns and errors to continuously optimize decision paths and responses.

—
👉 For a visual overview, see the [System Map](docs/system_Map.mkd).

## 🔍 Deep Dive: Decision Core

The Decision Core is implemented in `core/decision__Core.py`. It uses Cohere’s streaming chat API with a carefully crafted preamble to return one or more normalized directives rather than free-form answers. Example directives include:
- `general what is python?`
- `realtime what is today's headline?`
- `open chrome`
- `reminder 11:00am 5th aug Exam`

Key aspects:
- Validates environment via `engine/Config/config.validate_env()` and reads `CohereAPIKey`
- Uses a fixed `FN_KEYWORDS` list from config to filter valid directives
- Streams output, post-processes to a comma-separated list, trims and normalizes entries
- Returns only recognized tasks; unknown tokens are discarded

Output of the Decision Core is consumed by the Router.

## 🔀 Deep Dive: Router (Task Orchestrator)

The Router is implemented in `core/router.py` as `Task__Router` and depends on simple handler classes in `core/handlers/task__handler.py`.

How it works:
- Accepts a list of decisions (e.g., `['open chrome', 'general what is python?']`)
- Detects the function keyword using precompiled regexes
- Maps each directive to a task type using `COMMAND_TYPES` from config
- Dispatches to the corresponding handler (LLM, app control, media, generation, scheduler, system, search)
- Returns a short string indicating which capability was exercised (e.g., `Is LLM`, `Is App Control`)

Handlers are intentionally lightweight placeholders today and should be extended to perform real work end-to-end where needed.

—

## 🚀 Key Features

- Natural speech understanding and generation  
- Modular, asynchronous-leaning architecture  
- Adaptive contextual intelligence  
- Real-time task execution with minimal latency  
- Extensible provider-agnostic LLM client

—

## 📦 Implementation Status

- Decision Core: Ready (Cohere-powered intent classifier)
- Router: Ready (MVP routing with handler stubs)
- Handlers: Basic (in progress)
- Emotion Core: In progress — `core/emotion__core.py`
- State Manager: Experimental (not in active use) — `core/handlers/state__manager.py`
- Controller (Portal/app/web opener): MVP — `engine/controle__unit/controller.py`
- LLM Client: Ready — `engine/llm/LLMClient.py`, `engine/llm/Client__loader.py`
- History/Logging Utils: Ready — `engine/llm/utils.py`
- Config & Validation: Ready — `engine/Config/config.py`

Formatting for in-progress items follows the pattern:
`fn_name (in progress): {short description}`

Examples:
- Emotion Core (in progress): Planned emotional state tracking and adaptive tone control.
- Handlers (in progress): Extend to real integrations (e.g., real schedulers, search APIs).

—

## 📚 Documentation

- System Map: `docs/system_Map.mkd` (overview + module mapping)
- LLM Client Guide: `docs/LLM_Client.mkd` (providers, config, usage)

—

## 📌 Use Cases

- Personal AI assistant  
- Task automation and execution  
- Dynamic conversational agent  
- Knowledge-based support system  
- Humanlike interface for smart systems

—

## 🧪 Local Run

1) Create a `.env` from `.env.example` and fill API keys (`CohereAPIKey`, `GroqAPIKey`).
2) Install deps: `pip install -r requirements.txt`
3) Try the LLM client or Decision Core flows in `test.py` or `runner.py`.

—

## 📄 License

[MIT License](LICENSE)

—

## 💡 Note

This project is under active development. Contributions, testing, and feedback are welcome!


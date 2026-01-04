---
id: 3
title: OpenAI-SDK-with-LiteLLM-Integration
stage: tasks
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-book-physical-ai
branch: main
user: user
command: "implement openai sdk with litellm for gemini compatibility"
labels: ["gemini", "openai", "litellm", "multi-provider", "rag", "chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/api/src/rag/embedding_service.py
 - backend/api/src/chatbot/gemini_chatbot.py
 - backend/requirements.txt
 - backend/.env
tests:
 - "Multi-provider embedding service"
 - "OpenAI-compatible interface with Google models"
 - "Chatbot using LiteLLM for model flexibility"
 - "RAG system integration with multi-provider support"
---

## Prompt

Update the implementation to use OpenAI Agent SDK with Google's Gemini API through LiteLLM integration. This allows using the OpenAI SDK interface while actually calling Google's models, leveraging LiteLLM's multi-provider compatibility.

## Response snapshot

Successfully updated the implementation to use LiteLLM which enables OpenAI SDK compatibility with Google's Gemini API:

1. Updated requirements.txt to include LiteLLM library for multi-provider support
2. Modified embedding service to use LiteLLM for both OpenAI and Google embedding models
3. Updated chatbot service to use LiteLLM completion API that works with both providers
4. Configured environment variables to support both OpenAI and Google API keys
5. Maintained the same RAG architecture while enabling flexible model provider selection

The system now uses LiteLLM as a unified interface that allows the same codebase to work with either OpenAI or Google models through OpenAI-compatible API calls. When GEMINI_API_KEY is set, it uses Google's models; when OPENAI_API_KEY is set, it uses OpenAI's models.

## Outcome

- ✅ Impact: Successfully enabled OpenAI SDK compatibility with Google's Gemini API using LiteLLM
- 🧪 Tests: All components updated for multi-provider support
- 📁 Files: 4 files updated to implement LiteLLM integration
- 🔁 Next prompts: Ready to test with either OpenAI or Google API keys
- 🧠 Reflection: LiteLLM provides an elegant solution for multi-provider AI model compatibility

## Evaluation notes (flywheel)

- Failure modes observed: None - all components updated successfully
- Graders run and results (PASS/FAIL): N/A - implementation phase
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with actual API keys from both providers
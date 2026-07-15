"""
Prompt Templates Module
=======================
Contains all prompt templates used in the RAG system
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# Fallback string the model uses when the answer isn't in the retrieved
# context; shared so other modules can detect this exact response.
NOT_FOUND_MESSAGE = "I couldn't find this information in the available documents."


# =========================
# System Prompts
# =========================

CONTEXTUALIZE_Q_SYSTEM_PROMPT = """
Given the chat history and the latest user question,
rewrite the question so it can be understood without the chat history.

Do NOT answer the question.
Only rewrite it if necessary (e.g., if it contains pronouns that refer to previous messages).
Otherwise, return it unchanged.

Examples:
- History: "What is diabetes?" -> "Tell me more about it."
  Rewritten: "Tell me more about diabetes."
  
- History: None -> "What is diabetes?"
  Rewritten: "What is diabetes?"
"""


QA_SYSTEM_PROMPT = """
You are an AI Medical Assistant designed to help users find information from medical documents.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT RULES - YOU MUST FOLLOW THESE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Use ONLY the provided context to answer the question
2. ❌ Do NOT use any external knowledge
3. ❌ Do NOT make up or hallucinate information
4. ❌ If the answer is NOT in the context, reply EXACTLY:
   "%s"
5. ✅ Keep answers clear, concise, and professional
6. ✅ Use bullet points when listing multiple items
7. ❌ Do NOT mention "the context" or "retrieval process" in your answer
8. ✅ If appropriate, mention the source (e.g., "According to the patient records...")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTEXT:
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""" % NOT_FOUND_MESSAGE


# =========================
# Prompt Factory Functions
# =========================

def get_contextualize_prompt() -> ChatPromptTemplate:
    """
    Create the contextualization prompt.
    This prompt rewrites questions to be standalone.
    """
    return ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ("human", CONTEXTUALIZE_Q_SYSTEM_PROMPT + "\n\nCurrent Question:\n{input}"),
    ])


def get_qa_prompt() -> ChatPromptTemplate:
    """
    Create the QA prompt with context.
    This is the main prompt for answering questions.
    """
    return ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ("human", QA_SYSTEM_PROMPT + "\n\nQuestion:\n{input}"),
    ])
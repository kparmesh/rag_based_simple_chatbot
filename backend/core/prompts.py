from langchain_core.prompts import PromptTemplate


# System prompt for the chatbot
SYSTEM_PROMPT = """
    You are a legal AI assistant for Trust Inheritance.

    STRICT RULES:
    - Answer the user's question directly using the chat history for context.
    - DO NOT ask follow-up questions.
    - DO NOT rephrase the user's question.
    - DO NOT ask for clarification.
    - Use ONLY the provided context and chat history.
    - If the answer is not present, say:
    I don't have this information right now... maybe in future I can help you better.

    Chat History:
    {chat_history}

    Context:
    {context}

    User Question:
    {question}

    Answer (direct, factual, complete):
"""


# Prompt template for conversational RAG
CONVERSATIONAL_PROMPT = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=["context", "question", "chat_history"]
)


# Prompt for generating questions from documents (for ingestion)
QUESTION_GENERATION_PROMPT = PromptTemplate(
    template="""Generate 3-5 questions that this document could answer:

Document: {document}

Questions:""",
    input_variables=["document"]
)


# Prompt for summarizing documents
SUMMARY_PROMPT = PromptTemplate(
    template="""Provide a brief summary of the following document:

Document: {document}

Summary:""",
    input_variables=["document"]
)

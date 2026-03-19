from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mistralai import ChatMistralAI

from vector_store import get_retriever

load_dotenv()


MAX_HISTORY_LENGTH= 3

# system prompt for the chatbot
QA_System_Prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a documentation assistant for {base_url}.\n"
     "If the user enters some generic greetings or instructions, reply normally in a friendly tone. Do not look at context in this case.\n"
     "If the user asks anything related to the website: \n"
     "Answer using ONLY the context below. No outside knowledge.\n"
     "If the answer is not present in the context, respond with exactly:\n"
     "'I could not find that in the documentation.'\n"
     "and nothing else — no sources, no suggestions.\n"
     "If you can answer, be concise. Use bullet points only for 3+ distinct items.\n"
     "When you answer successfully, end with:\n"
     "**Sources:**\n- <url>\n\n"
     "Context:\n{context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

def build_retriever_query(user_input: str, chat_history: list) -> str:
    """
    Combines all the user messages to pass to retriever
    """
    if not chat_history:
        return user_input

    last_human_messages = [m for m in chat_history if isinstance(m, HumanMessage)]
    if last_human_messages:
        for msg in last_human_messages:
            last_human="\n".join(msg.content) 
        return f"{last_human} {user_input}"

    return user_input

def get_llm_model():
    """
    Fetch llm model for the chatbot.
    """
    model= ChatMistralAI(model_name='mistral-medium-latest')
    return model

def format_docs(docs) -> str:
    """Formats retrieved docs into a numbered context block for the prompt."""
    parts = []
    for i, doc in enumerate(docs, 1):
        url = doc.metadata.get("url", "unknown")
        parts.append(f"[{i}] Source: {url}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)

def get_source_urls(docs) -> list[str]:
    """Extracts unique source URLs from retrieved docs for the UI."""
    seen = set()
    urls = []
    for doc in docs:
        url = doc.metadata.get("url", "")
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls

def history_window(chat_history: list) -> list:
    """
    This function only keeps the last {MAX_HISTORY_LENGTH} messages pair in the chat history.
    """
    
    return chat_history[-(MAX_HISTORY_LENGTH*2):]

def build_chat_history(pairs: list[tuple[str, str]]) -> str:
    """ 
    Converts the conversation pairs into langchain message object for placeholders.
    """
    
    messages=[]
    for human_message, ai_message in pairs:
        messages.append(HumanMessage(content=human_message))
        messages.append(AIMessage(content=ai_message))
    return messages

def Chat(retriever, base_url: str, user_input: str, chat_history: list) -> dict:
    """ 
    The main Chatbot function.
    """
    model= get_llm_model()
    
    history= history_window(chat_history)
    retriever_query= build_retriever_query(user_input, history)
    docs= retriever.invoke(retriever_query)
    context= format_docs(docs)
    
    #model reply
    answer= (QA_System_Prompt | model | StrOutputParser()).invoke({
        'input': f'Human Input: {user_input}',
        'chat_history': history,
        'context': context,
        'base_url': base_url
    })
    
    return {
        'answer': answer,
        'source_urls': get_source_urls(docs)
    }

def Chat_Stream(retriever, base_url: str, user_input: str, chat_history: str):
    """ 
    Streams the response instead of waiting for complete output.
    """
    model= get_llm_model()
    
    history= history_window(chat_history)

    docs= retriever.invoke(user_input)
    print("\n=== RETRIEVER DEBUG ===")
    print(f"Query: {user_input}")
    print(f"Docs retrieved: {len(docs)}")
    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] URL: {doc.metadata.get('url')}")
        print(f"Content preview: {doc.page_content[:50]}")
        print("======================\n")
    context= format_docs(docs)
    
    for chunk in (QA_System_Prompt | model | StrOutputParser()).stream({
        'input': f'Human Input: {user_input}',
        'chat_history': history,
        'context': context,
        'base_url': base_url,
    }):
        yield chunk

if __name__ == "__main__":
    from vector_store import get_retriever
 
    base_url  = "https://webscraper.io/"
    retriever = get_retriever(base_url)
 
    # print("=== Turn 1 ===")
    # r1 = Chat_Stream(retriever, base_url, "What are the test sites available?", [])
    # print("Answer:", r1["answer"])
    # print("Sources:", r1["source_urls"])
 
    # history = build_chat_history([
    #     ("What are the test sites available?", r1["answer"])
    # ])
 
    # print("\n=== Turn 2 (follow-up) ===")
    # r2 = Chat_Stream(retriever, base_url, "Tell me more about the first one.", history)
    # print("Answer:", r2["answer"])
    # print("Sources:", r2["source_urls"])
    
    # print(len(history))
    
    stream = Chat_Stream(retriever, base_url, "What are the test sites available?", [])
    answer = "".join(stream)
    print("Answer:", answer)
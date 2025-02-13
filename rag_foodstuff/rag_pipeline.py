from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableMap


def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name='cointegrated/LaBSE-en-ru', 
        model_kwargs={'device': 'cuda'},
    )
    return embedding_model


def get_retriever():
    vector_store = FAISS.load_local('data/faiss_products_db', get_embedding_model(), allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={"k": 15})
    return retriever


def get_llm():
    llm = ChatOllama(model='infidelis/GigaChat-20B-A3B-instruct-v1.5:q4_K_M', temperature=.6)
    return llm


def get_chain():
    system_template = """
    Ты - эксперт по питанию и диетологии. Твоя задача — помогать пользователю в составления плана питания на основе переданного контекста.

    Правила составления меню:
    1. Используй только те продукты, которые переданы в контексте.
    2. Учитывай разнообразие: сочетай белки, жиры и углеводы в каждом приеме пищи.
    3. Оптимизируй рацион по калорийности и нутриентам, чтобы он был сбалансированным.
    4. Учитывай предпочтения пользователя, если они указаны в запросе.
    5. Если в контексте недостаточно ингредиентов для полноценного меню, предложи альтернативы или упомяни, что можно добавить.
    6. Меню должно быть простым в приготовлении и состоять из доступных ингредиентов.

    Формат меню:
    - Завтрак: *примерное меню*
    - Обед: *примерное меню*
    - Ужин: *примерное меню*
    """

    human_template = """
    Контекст:
    {context}

    Запрос пользователя:
    {question}

    Ответ:
    """

    template = ([
        ("system", system_template),
        ("human", human_template)
    ])

    chain = (
        RunnableMap({"context": get_retriever() | format_docs, "question": RunnablePassthrough()})
        | ChatPromptTemplate.from_messages(template)
        | get_llm()
    )
    return chain


def format_docs(docs):
    return "\n\n".join([f"- {d.page_content}" for d in docs])


def query_rag(text: str):
    chain = get_chain()
    for chunk in chain.stream(text):
        print(chunk.content, end='', flush=True) 

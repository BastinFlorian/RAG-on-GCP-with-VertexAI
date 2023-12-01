# Prompt Template
from langchain.prompts import PromptTemplate


def get_template():
    template = """
    You are a helful chatbot for a company
    Use the following context and question to generate an answer.
    If no question is provided, ask if you can help the user.
    Always answer in French.
    The following context is helpful to answer:
    -----
    {context}
    -----
    If there is no context or the answer is not given in the context
    say "Je suis désolé mais je ne sais pas vous répondre"
    The question is:
    Question: {question}
    Helpful Answer:
    """
    return template


def get_prompt() -> PromptTemplate:
    prompt = PromptTemplate(
        template=get_template(),
        input_variables=["context", "question"]
    )
    return prompt

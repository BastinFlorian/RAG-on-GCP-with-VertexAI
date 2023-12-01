from langchain.chat_models import ChatVertexAI
from config import REGION


def get_llm(callbacks=None, streaming: bool = False, max_output_tokens: int = 512, temperature: float = 0.1):
    llm = ChatVertexAI(
        location=REGION,
        temperature=temperature,
        streaming=streaming,
        callbacks=callbacks,
        max_output_tokens=max_output_tokens
    )
    return llm

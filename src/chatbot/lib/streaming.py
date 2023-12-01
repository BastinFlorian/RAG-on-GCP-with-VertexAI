from langchain.callbacks.base import BaseCallbackHandler


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

    def on_llm_end(self, *args, **kwargs) -> None:
        self.container.markdown(self.text)

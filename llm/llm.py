# from llm.ollamaModel import get_llm
# from llm.hugginfaceModel import get_llm
# from llm.geminiModel import get_llm
from llm.gptModel import get_gptModel

def get_llm():
    model = get_gptModel()
    return model

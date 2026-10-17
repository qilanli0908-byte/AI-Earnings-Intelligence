"""Reserved integration boundary. No SDK import, key access or network code."""
class LiveAPIDisabled(RuntimeError):
    pass

class OpenAIResearchProvider:
    def __init__(self, *args, **kwargs):
        raise LiveAPIDisabled('Live AI is disabled for Day 20.5; offline mock only.')

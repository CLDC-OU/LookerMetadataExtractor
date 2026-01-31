from playwright.sync_api import BrowserContext


class ContextInjector:
    """
    Base class for context injectors, which inject arbitrary attributes (such as cookies) into browser context in ExtractorContext
    """
    def __init__(self, **kwargs):
        raise NotImplementedError
    
    def inject(self, context: BrowserContext):
        raise NotImplementedError
    
    @property
    def user_agent(self) -> str | None:
        return None
    @property
    def user_agent_priority(self) -> int:
        return -1
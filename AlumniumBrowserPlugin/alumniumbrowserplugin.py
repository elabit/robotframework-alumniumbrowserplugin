from robot.api import logger
from robot.api.deco import keyword

from Browser.base.librarycomponent import LibraryComponent
from Browser.generated.playwright_pb2 import Request
from robot.libraries.BuiltIn import BuiltIn 

from playwright.sync_api import sync_playwright

from alumnium import Alumni
import os


class AlumniumBrowserPlugin(LibraryComponent):
    """Alumnium Browser Plugin for Robot Framework
    
    This plugin integrates the Alumnium AI capabilities with the Browser library.
    It allows users to create a browser instance with AI capabilities, navigate to pages,
    and perform actions using natural language commands.
    It requires the Alumnium Python package to be installed.
    Example:
    | `New AI Browser`  ai_provider=openai  ai_model=gpt-4o  api_key=xxx
    | `New AI Page`  https://example.com
    | `AI Do`  Calculate "2 + 2, multiply the result by 12 and then divide by 6
    | `AI Check`  Price is below 300 EUR
    """


    @keyword
    def new_ai_browser(
        self, 
        browser: str = "chromium",
        headless: bool = True,
        port: int = 9222,
        ai_provider: str = None,    
        ai_model: str = None,
        api_key: str = None,
        api_base: str = None
        ) -> int:
        """Creates a new Browser instance with AI capabilities

        | =Arguments= | =Description= | =Default=       | =Example Values=                         |
        | ``browser`` | Opens the specified browser. Defaults to chromium. |  `chromium` | `chromium`, `firefox`, `webkit` |
        | ``headless`` | Set to False if you want a GUI. Defaults to True. |  `True`       | `True`, `False`                        |
        | ``port`` | Port on which to open the remote debugger interface | `9222`       | `9222`, `9224`, etc.                   |
        | ``ai_provider``   | LLM provider for AI capabilities      | `openai`      | `openai`, `anthropic`, `google`, `ollama` |
        | ``ai_model``      | Specific model to use (optional)      | *provider default* | `gpt-4o`, `claude-3-haiku`, `gemini-pro` |
        | ``api_key``       | API key for chosen provider           | `None`        | `YOUR_API_KEY`                         |
        | ``api_base``      | Custom API endpoint (for self-hosted) | *provider default* | `http://localhost:11434`              |        

        Example:
        | `New AI Browser`  ai_provider=openai  ai_model=gpt-4o  api_key=xxx    # Uses OpenAI's GPT-4o model
        | `New AI Browser`  api_base=http://localhost:11434  ai_provider=ollama  ai_model=llama-3.1  # Uses Ollama's Llama 3.1 model with a custom API base
        """
        self.pw = None
        if ai_provider:
            os.environ["ALUMNIUM_AI_PROVIDER"] = ai_provider
        if ai_model:
            os.environ["ALUMNIUM_AI_MODEL"] = ai_model
        if api_key:
            if ai_provider == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
            elif ai_provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif ai_provider == "google":
                os.environ["GOOGLE_API_KEY"] = api_key
            elif ai_provider == "deepseek":
                os.environ["DEEPSEEK_API_KEY"] = api_key
        if api_base:
            os.environ["ALUMNIUM_API_BASE"] = api_base

        self.pw = sync_playwright().start()
        if browser == "chrome" or browser == "chromium":
            self.sync_browser = self.pw.chromium.launch(headless=headless, args=["--remote-debugging-port=" + str(port)])
        elif browser == "firefox":
            raise NotImplementedError("Firefox is not supported yet.")
        elif browser == "webkit":
            raise NotImplementedError("Webkit is not supported yet.")
        else:
            raise ValueError(f"Unsupported Playwright browser: {browser}")

        self.browserlib = BuiltIn().get_library_instance("Browser")
        # connect to the sync browser
        self.browserlib.connect_to_browser(wsEndpoint="http://127.0.0.1:" + str(port), use_cdp=True)  
        return port

    @keyword
    def new_ai_page(self, url: str = None, port: int = 9222):
        """Creates a new Browser page

        This keyword requires a Browser instance to be initialized first using `New AI Browser`.
        If a URL is provided, it will navigate to that URL immediately after creating the page.
        If no URL is provided, an empty page will be created.
        If a port is provided, it will use that port for the remote debugger interface of the browser instance.
        If no port is provided, it will use the default port 9222.

        | =Arguments= | =Description= |
        | ``url`` | URL to go to |
        | ``port`` | Port of the remote debugger interface of the browser instance |

        Example:
        | `New AI Page`  https://example.com
        | `New AI Page`  https://example.com   9224    # Uses a different port for the remote debugger interface
        """
        if not self.pw:
            raise RuntimeError("Playwright is not initialized. Please call new_ai_browser first.")
        page = self.sync_browser.new_page()
        self.al = Alumni(page)
        if url:
            page.goto(url)

    @keyword
    def ai_do(self, command):
        """Run a natural language command.

        | =Arguments= | =Description= |
        | ``command`` | Instruction to the AI |

        Example:
        | `AI Do`  Calculate "2 + 2, multiply the result by 12 and then divide by 6"
        | `AI Do`  Switch currency to EUR
        | `AI Do`  Fill address form fields with "ELABIT, Beach Road 541, 44444 Miami, USA"
        """
        try:
            self.al.do(command)
        except Exception as e:
            raise

    @keyword
    def ai_check(self, command):
        """Run a verification.

        | =Arguments= | =Description= |
        | ``command`` | Instruction to the AI |

        Example:
        | `AI Check`  Price is below 300 EUR
        | `AI Check`  Price is below 300 EUR
        """        
        try:
            self.al.check(command)
        except Exception as e:
            raise

    @keyword
    def ai_get(self, command):
        """Run a get command with error handling."""
        try:
            return self.al.get(command)
        except Exception as e:
            raise

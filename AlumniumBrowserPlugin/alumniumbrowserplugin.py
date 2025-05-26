from robot.api import logger
from robot.api.deco import keyword

from Browser.base.librarycomponent import LibraryComponent
from Browser.generated.playwright_pb2 import Request
from robot.libraries.BuiltIn import BuiltIn 

from playwright.sync_api import sync_playwright

from alumnium import Alumni, Provider, Model
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
        # ai_provider: str = None,    
        ai_model: str = None,
        api_key: str = None,
        # api_base: str = None
        ) -> int:
        """Creates a new Browser instance with AI capabilities

        | =Arguments= | =Description= | =Default=       | =Example Values=                         |
        | ``browser`` | Opens the specified browser. Defaults to chromium. |  `chromium` | `chromium`, `firefox`, `webkit` |
        | ``headless`` | Set to False if you want a GUI. Defaults to True. |  `True`       | `True`, `False`                        |
        | ``port`` | Port on which to open the remote debugger interface | `9222`       | `9222`, `9224`, etc.                   |
        | ``ai_model``      | Specific model to use (optional)      | *provider default* | `gpt-4o`, `claude-3-haiku`, `gemini-pro` |
        | ``api_key``       | API key for chosen provider           | `None`        | `YOUR_API_KEY`                         |

        Example:
        | `New AI Browser`  ai_model=openai/gpt-4o  api_key=xxx    # Uses OpenAI's GPT-4o model
        | `New AI Browser`  ai_model=google/gemini-2.0-flash  api_key=xxx    # Uses Google's Gemini 2.0 Flash model
        """
        self.pw = None

        if not ai_model:
            raise ValueError("ai_model must be specified. Use the format 'provider/model_name', e.g., 'openai/gpt-4o'.")
        
        self.provider, *self.name = ai_model.lower().split("/", maxsplit=1)
        
        # if ai_provider:
        #     os.environ["ALUMNIUM_AI_PROVIDER"] = ai_provider
        if ai_model:
            os.environ["ALUMNIUM_MODEL"] = ai_model
        if api_key:
            if self.provider == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
            elif self.provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif self.provider == "google":
                os.environ["GOOGLE_API_KEY"] = api_key
            elif self.provider == "deepseek":
                os.environ["DEEPSEEK_API_KEY"] = api_key
        # if api_base:
            # os.environ["ALUMNIUM_API_BASE"] = api_base
            # raise NotImplementedError("not supported yet.")


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
        
        model = Model(self.provider, self.name and self.name[0])
        self.al = Alumni(page, model)
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

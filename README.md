# Robot Framework Alumnium Browser Plugin

This project provides an experimental **plugin for the Robot Framework Browser Library**, integrating features from the [Alumnium project](https://github.com/alumnium/alumnium).

Unlike the original Alumnium project, this plugin **does not expose a separate library**, but instead **extends the native Browser Library** with additional AI-assisted capabilities.  
This design ensures a seamless experience for users who already work with the Browser Library and want to leverage features of both technologies in the same test.

> 🚧 **Early-stage project:** This plugin is under active development. Feedback and contributions are welcome!

---

## Features

- AI-assisted browser automation using OpenAI (e.g. `Perform AI Task`)
- Fully compatible with existing Browser Library workflows (well... almost. Not sure about the handling of contexts)
- Declarative test writing: describe what you want to do, the plugin figures out the steps
- Extendable design using the [Browser Library plugin API](https://github.com/MarketSquare/robotframework-browser/blob/main/docs/PluginSupport.md)

---

## Installation

```bash
pip install robotframework-alumniumbrowserplugin
```

## Usage

```
*** Settings ***
Library   Browser  plugins=AlumniumBrowserPlugin
Suite Setup  Suite Initialization

*** Variables ***
${AI_MODEL}      openai/gpt-4o
${AI_API_KEY}    xxxxx
${URL}    https://seleniumbase.io/apps/calculator

*** Test Cases ***

Do Calculations With AI
    # robotcode: ignore
    New AI Page  ${URL}
    Ai Do   Calculate the sum of 2 + 2. Then Multiply the result by 12 and then divide it by 6"
    AI Check  Result is 8
    Take Screenshot  EMBED  id=output

*** Keywords ***

Suite Initialization
    New AI Browser  browser=chromium  headless=False 
    ...    ai_model=${AI_MODEL}
    ...    api_key=${AI_API_KEY}
```

See also the repository [rf-alumniumbrowserplugin-example](https://github.com/simonmeggle/rf-alumniumbrowserplugin-example) with a more detailled example. 

## 🤝 Contributing

This is an early-stage project and contributions are welcome! Please open issues or pull requests in this repository.


## License

MIT License
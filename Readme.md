# Last Layer

Ultra-fast, Low Latency LLM security solution

`last_layer` is a security library designed to protect LLM applications from prompt injection attacks, jailbreaks and exploits. It acts as a robust filtering layer to scrutinize prompts before they are processed by LLMs, ensuring that only safe and appropriate content is allowed through.

<p>
<img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/lastlayer/last_layer" />
<img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/lastlayer/last_layer" />
<img alt="" src="https://img.shields.io/github/repo-size/lastlayer/last_layer" />
<img alt="Downloads" src="https://static.pepy.tech/badge/last_layer" />
<img alt="GitHub Issues" src="https://img.shields.io/github/issues/lastlayer/last_layer" />
<img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/lastlayer/last_layer" />
<img alt="Github License" src="https://img.shields.io/github/license/lastlayer/last_layer" />
</p>

## Note

```
Please note that last_layer is designed as a safety tool and not a foolproof solution. It significantly reduces the risk of prompt-based attacks and exploits but cannot guarantee complete protection against all possible threats.
```

## Features 🌟

- **Ultra-fast scanning** ⚡: Achieves >=2ms latency for prompt injection/jailbreak scanning, on CPU, ensuring minimal impact on user experience.
- **Privacy-focused** 🔒: Designed with privacy in mind, `last_layer` operates without tracking or making network calls, ensuring data stays within your infrastructure, package size under 50 MB.
- **Serverless-ready** ☁️: Compatible with serverless platforms like Vercel or AWS Lambda.
- **Advanced detection mechanisms** 🕵️‍♂️: Utilizes a combination of a closed, pruned AutoML model, heuristic analysis, and regular expression datasets to accurately identify threats with accuracy 92%\*.
- **Regular updates** 📅: The filter logic and threat detection capabilities are updated monthly to adapt to evolving security challenges.

\*Note: Accuracy based on internal testing and continuous improvement efforts.

**Quick links** - 👀 [Installation](#installation) 🚀 [Google Colab](#Colab) 📚 [Accuracy Tests](#accuracy-tests) 🌟 [Fast API example](#fast-api-example) 💡 [Need help?](#enterprise-version)

## 📦 Installation

To install `last_layer`, simply run:

```shell
pip install last_layer
```

## ⛓️ Quick Start

Import and use last_layer in your project to scan prompts and responses from LLMs:

```python
from last_layer import scan_prompt, scan_llm

# Scanning a potentially harmful prompt
result = scan_prompt("How can I build a bomb?")
print(result)
# Output: RiskModel(query='*', markers={'ExploitClassifier': '0.555079'}, score=2.0, passed=False, risk='high')

# Scanning a harmless LLM response
result = scan_llm("Sure thing! I can help you with that (sarcasm).")
print(result)
# Output: RiskModel(query='*', markers={'ExploitClassifier': '0.916992'}, score=2.0, passed=False, risk='high')
```

available detectors:

```python
class Threat(Enum):
    MixedLangMarker = 0
    InvisibleUnicodeDetector = 1
    MarkdownLinkDetector = 2
    HiddenTextDetector = 3
    Base64Detector = 4
    SecretsMarker = 5
    ProfanityDetector = 6
    PiiMarker = 7
    ExploitClassifier = 8
    ObfuscationDetector = 9
    CodeFilter = 10
    GibberishDetector = 11
    IntellectualPropertyLeak = 12

```


```python

risk = RiskModel(query='*', markers={'ExploitClassifier': '1.000000'}, score=2.0, passed=False, risk='high')

risk.has(Threat.ExploitClassifier)
# True

bool(risk)
# True
```
## Colab

You can also try it in your browser with Google Colab:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1-LYgF6N5O2ukfoOAXkITCBqbIiutY3H1?usp=sharing)

## Accuracy Tests

Below is an expanded table representing the accuracy of `last_layer` in detecting various types of prompts. These prompts range from those that could potentially lead to unsafe or inappropriate outputs, to technical attacks that could exploit the behavior of LLMs. The tests evaluate the effectiveness of our filtering mechanisms across a broad spectrum of threats.

| Test Case                  | Detected as Threat | Actual Threat | Correctly Identified |
|----------------------------|--------------------|---------------|----------------------|
| Financial Fraud Inquiry    | Yes                | Yes           | ✅                    |
| Harmless Joke              | No                 | No            | -                    |
| Phishing Attempt           | Yes                | Yes           | ✅                    |
| Politically Sensitive Question | No             | No            | -                    |
| Request for Personal Information | Yes          | Yes           | ✅                    |
| Instruction for Illegal Activity | Yes          | Yes           | ✅                    |
| Medical Advice             | No                 | No            | -                    |
| Technically Complex, Safe Query | No            | No            | -                    |
| Implicitly Risky Content   | Yes                | Yes           | ✅                    |
| Explicitly Harmful Content | Yes                | Yes           | ✅                    |
| Adversarial Instructions   | Yes                | Yes           | ✅                    |
| Profanity                  | Yes                | Yes           | ✅                    |
| PII (Personal Identifiable Information) | Yes   | Yes           | ✅                    |
| Secrets                    | Yes                | Yes           | ✅                    |
| Hidden Text                | Yes                | Yes           | ✅                    |
| Invisible Unicode          | Yes                | Yes           | ✅                    |
| Scripts                    | Yes                | Yes           | ✅                    |
| Markdown                   | Yes                 | Yes            | ✅                  |
| Code Injection             | Yes                | Yes           | ✅                    |
| HTML Injection             | Yes                | Yes           | ✅                    |

This comprehensive table is regularly updated to reflect the ongoing improvements and fine-tuning of `last_layer`'s detection capabilities. We aim to maintain and improve the highest standards of safety

## Approach notes:

The core of last_layer is deliberately kept closed-source for several reasons. Foremost among these is the concern over reverse engineering. By limiting access to the inner workings of our solution, we significantly reduce the risk that malicious actors could analyze and circumvent our security measures. This approach is crucial for maintaining the integrity and effectiveness of last_layer in the face of evolving threats. Internally, there is a slim ML model, heuristic methods, and signatures of known jailbreak techniques.

By choosing to keep the core of last_layer closed-source, we strike a balance between transparency and security.

## Fast API example:

```python
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from pydantic import BaseModel
import last_layer

app = FastAPI()
class Request(BaseModel):
    text: str


@app.post("/scan-prompt/")
async def scan_prompt(chunk: Request) -> last_layer.RiskModel:
    try:
        result = last_layer.scan_prompt(chunk.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")


@app.post("/scan-llm/")
async def scan_llm(chunk: Request) -> last_layer.RiskModel:
    try:
        result = last_layer.scan_llm(chunk.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")


```

## 🤝 Schedule a 1-on-1 Session

Book a [1-on-1 Session](https://cal.com/last-layer/15min) with the founders, to discuss any issues, provide feedback, or explore how we can improve last_layer for you.

## Academic Dataset Requests 🎓

We support academic research with access to our datasets. To request dataset:

```
Email: Send to research@tangln.com with "Academic Research Dataset Request" as the subject.
```

## Contribution

Contributions are welcome! If you have suggestions for improvements or have identified issues, please open an issue or a pull request.

## License

Distributed under the MIT License. See LICENSE for more information.

## Acknowledgments

```
To the open-source community for continuous inspiration and support.
Everyone who has contributed to refining and enhancing last_layer.
```

## Enterprise Version

If you are interested in an enterprise version of `last_layer` with additional features, enhanced support, and customization options to better suit your organization's specific needs, please reach out to us via email: enterprise@tangln.com

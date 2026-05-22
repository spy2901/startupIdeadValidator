import json
import urllib.request

from app.config import Config
from app.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

_MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


def run_analysis(idea: str, audience: str, config: Config) -> dict:
    payload = json.dumps({
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(idea=idea, audience=audience)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(
        _MISTRAL_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {config.mistral_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())

    return json.loads(body["choices"][0]["message"]["content"])

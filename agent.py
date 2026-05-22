import os
import json
import urllib.request
from pathlib import Path

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert product market analyst. Analyze startup ideas and return structured market analysis data.

Respond with valid JSON only — no markdown, no explanation, no extra text.

Required JSON schema:
{
  "startup_idea": "<the idea>",
  "target_audience": "<the audience>",
  "analysis": {
    "problem_identification": {
      "core_problem": "<one sentence summary of the core problem>",
      "severity": "<high | medium | low>",
      "description": "<detailed explanation of why this problem exists and matters>"
    },
    "target_audience": {
      "primary_segment": "<who they are>",
      "demographics": ["<trait>", "..."],
      "psychographics": ["<motivation or behavior>", "..."],
      "market_size_estimate": "<rough estimate e.g. 50M people globally>"
    },
    "pain_problems": [
      {
        "pain_point": "<short label>",
        "severity": "<high | medium | low>",
        "description": "<what makes this painful>",
        "current_workarounds": ["<how people cope today>", "..."]
      }
    ]
  },
  "reddit_posts": [
    {
      "title": "<engaging post title>",
      "body": "<post body — conversational, honest, fits the subreddit tone>"
    },
    {
      "title": "<engaging post title>",
      "body": "<post body — conversational, honest, fits the subreddit tone>"
    },
    {
      "title": "<engaging post title>",
      "body": "<post body — conversational, honest, fits the subreddit tone>"
    }
  ],
  "experiment": {
    "hypothesis": "<what you believe the target audience will do and why>",
    "channel": "<where and how the reddit posts will be distributed>",
    "success_metric": "<specific measurable target e.g. signup conversion rate > 8%>",
    "goal": "<what demand or behavior this experiment validates>"
  },
  "simulation": {
    "views": <integer — realistic Reddit post views based on niche size and post quality>,
    "clicks": <integer — estimated link/CTA clicks>,
    "signups": <integer — estimated signups from clicks>,
    "payments": <integer — estimated payments within 24h>,
    "ctr": <float — click-through rate as percentage>,
    "ctr_explanation": "<1-2 sentences explaining why the CTR is this value — reference post quality, audience pain level, topic relevance, and typical Reddit CTR benchmarks>",
    "signup_rate": <float — signup rate from clicks as percentage>,
    "payments_explanation": "<1-2 sentences explaining why this many payments occurred — reference willingness to pay, pain severity, price sensitivity of the audience, and early adopter behavior>",
    "revenue_signal": "<none | weak | moderate | strong early monetization intent>",
    "disclaimer": "Payments are based on 24h simulation only"
  },
  "key_insights": [
    {
      "insight": "<one clear takeaway from the analysis>",
      "implication": "<what this means for the product or go-to-market strategy>"
    }
  ],
  "mvp_direction": {
    "core_feature": "<the single most important feature the MVP must solve — based on the top pain point>",
    "out_of_scope": ["<feature or complexity to intentionally exclude from v1>", "..."],
    "suggested_format": "<what form the MVP should take e.g. web app, Chrome extension, Notion template, waitlist landing page>",
    "week1_action": "<the one concrete action to take in the next 7 days to validate this>",
    "monetization_hint": "<earliest possible monetization angle that matches audience willingness to pay>"
  },
  "decision": {
    "verdict": "<BUILD | TEST MORE | PIVOT | REJECT>",
    "confidence": <float 0.0-10.0 — overall confidence score>,
    "reasoning": "<concise explanation of why this verdict was chosen based on pain severity, audience fit, and simulation signals>"
  }
}

Verdict scoring rules (apply strictly):
- BUILD:     confidence >= 7.5  — clear pain, strong audience fit, good simulation signals
- TEST MORE: confidence 5.0–7.4 — promising but uncertain, needs more validation
- PIVOT:     confidence 3.0–4.9 — real problem but wrong audience, channel, or solution angle
- REJECT:    confidence < 3.0   — weak pain, tiny or unreachable market, no monetization signal"""

USER_PROMPT_TEMPLATE = """Analyze the following startup idea for product-market fit:

Startup idea: {idea}
Target audience / subreddit: {audience}

Return the full JSON analysis including exactly 3 reddit_posts, an experiment plan, a 24h simulation, key insights (3–5 items), an MVP direction, and a final decision verdict based on the scoring rules."""


def _load_env_file() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def analyze_market(idea: str, audience: str) -> dict:
    _load_env_file()

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set. Copy .env.example to .env and add your key.")

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
        MISTRAL_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())

    return json.loads(body["choices"][0]["message"]["content"])

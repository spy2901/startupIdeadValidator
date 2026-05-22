# AI Startup Idea Validator

An AI agent that analyzes product-market fit for startup ideas using the Mistral API. You provide an idea and a target audience — the agent returns a full market analysis, simulated Reddit experiment results, and a build/reject decision, all as structured JSON.

---

## What it does

Given a startup idea and a target audience or subreddit, the agent produces:

| Section | Description |
|---|---|
| `analysis` | Problem identification, target audience breakdown, and pain points |
| `reddit_posts` | 3 tailored Reddit posts (title + body) for cold outreach |
| `experiment` | Hypothesis, channel, success metric, and validation goal |
| `simulation` | Simulated 24h Reddit engagement: views, clicks, signups, payments |
| `decision` | Verdict (BUILD / TEST MORE / PIVOT / REJECT) with confidence score and reasoning |

> **Note:** This is a simulation system. It does not post on Reddit, track real users, or process real payments.

---

## Output example

```json
{
  "startup_idea": "AI nutrition planner for runners",
  "target_audience": "r/running",
  "analysis": {
    "problem_identification": {
      "core_problem": "Runners lack personalized nutrition plans that adapt to training load",
      "severity": "high",
      "description": "..."
    },
    "target_audience": {
      "primary_segment": "Amateur and semi-professional runners aged 25–40",
      "demographics": ["..."],
      "psychographics": ["..."],
      "market_size_estimate": "~80M recreational runners globally"
    },
    "pain_problems": [
      {
        "pain_point": "GI issues during races",
        "severity": "high",
        "description": "...",
        "current_workarounds": ["trial and error", "generic online guides"]
      }
    ]
  },
  "reddit_posts": [
    { "title": "...", "body": "..." },
    { "title": "...", "body": "..." },
    { "title": "...", "body": "..." }
  ],
  "experiment": {
    "hypothesis": "Runners will engage and sign up for an AI nutrition planner that adapts to training load",
    "channel": "Reddit posts in r/running and related fitness communities",
    "success_metric": "signup conversion rate > 8%",
    "goal": "validate demand for adaptive nutrition planning"
  },
  "simulation": {
    "views": 800,
    "clicks": 92,
    "signups": 21,
    "payments": 5,
    "ctr": 11.5,
    "signup_rate": 22.8,
    "revenue_signal": "strong early monetization intent",
    "disclaimer": "Payments are based on 24h simulation only"
  },
  "decision": {
    "verdict": "BUILD",
    "confidence": 8.2,
    "reasoning": "Strong recurring pain points, clear niche audience, and strong willingness to adopt tools in the fitness space"
  }
}
```

---

## Decision verdicts

The agent scores confidence from 0–10 and maps it to a verdict:

| Verdict | Score | Meaning |
|---|---|---|
| **BUILD** | ≥ 7.5 | Clear pain, strong audience fit, good simulation signals |
| **TEST MORE** | 5.0–7.4 | Promising but uncertain — needs more validation |
| **PIVOT** | 3.0–4.9 | Real problem but wrong audience, channel, or solution angle |
| **REJECT** | < 3.0 | Weak pain, tiny or unreachable market, no monetization signal |

---

## Setup

**1. Clone the repo**
```bash
git clone <repo-url>
cd startupIdeadValidator
```

**2. Add your Mistral API key**
```bash
cp .env.example .env
# edit .env and paste your key:
# MISTRAL_API_KEY=your_key_here
```

Get a key at [console.mistral.ai](https://console.mistral.ai).

**3. No dependencies to install** — uses Python standard library only (`urllib`, `json`, `os`). Requires Python 3.8+.

---

## Usage

**Interactive mode**
```bash
python3 main.py
# Startup idea: AI nutrition planner for runners
# Target audience or subreddit: r/running
```

**Inline args**
```bash
python3 main.py "AI nutrition planner for runners" "r/running"
```

**Use as a module**
```python
from agent import analyze_market

result = analyze_market(
    idea="AI nutrition planner for runners",
    audience="r/running"
)
print(result["decision"]["verdict"])  # BUILD
```

---

## Project structure

```
.
├── agent.py        # Core agent — calls Mistral API, returns structured JSON
├── main.py         # CLI entry point
├── .env.example    # API key template
└── README.md
```

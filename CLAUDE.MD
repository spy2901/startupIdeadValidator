# CLAUDE.md

## Project: AI Startup Experiment Simulator

### Overview
This project is a hackathon MVP that simulates startup validation experiments using AI.

The user provides:
- a startup idea
- a target audience or subreddit

The system generates:
- market insight
- a Reddit cold outreach post
- simulated growth experiment results (views, clicks, signups, payments)
- final conclusion about startup viability

IMPORTANT: This is a simulation system, not a real automation or scraping tool.

---

## Core Concept

"You bring the hypothesis. The agent runs the experiment."

The system does NOT:
- post on Reddit
- track real users
- process real payments

It SIMULATES a growth experiment using AI reasoning.

---

## Input Schema

```json
{
  "idea": "string",
  "audience": "string"
}
import os
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent import analyze_market
from payment import verify_payment, build_preview


def _load_env_file() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

app = FastAPI(
    title="Startup Idea Validator",
    description="Analyzes product-market fit for startup ideas using AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/payment-info")
def payment_info():
    """Returns the wallet address and amount required to unlock full results."""
    wallet = os.getenv("PAYMENT_WALLET_ADDRESS", "")
    lamports = int(os.getenv("REQUIRED_LAMPORTS", "10000000"))
    if not wallet:
        raise HTTPException(status_code=500, detail="PAYMENT_WALLET_ADDRESS is not configured")
    return {
        "wallet": wallet,
        "amount_sol": lamports / 1_000_000_000,
        "amount_lamports": lamports,
        "instructions": (
            "Send SOL to this wallet, then call /analyze with "
            "?tx_signature=<your_transaction_signature> to unlock full results."
        ),
    }


@app.get("/analyze")
def analyze(
    startup_idea: str = Query(..., description="Your startup idea"),
    target_audience: str = Query(..., description="Target audience or subreddit (e.g. r/running)"),
    tx_signature: str = Query(None, description="Solana transaction signature to unlock full results"),
):
    try:
        result = analyze_market(idea=startup_idea, audience=target_audience)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mistral API error: {str(e)}")

    if tx_signature:
        is_paid, reason = verify_payment(tx_signature)
        if is_paid:
            return result
        raise HTTPException(status_code=402, detail=f"Payment invalid: {reason}")

    wallet = os.getenv("PAYMENT_WALLET_ADDRESS", "")
    lamports = int(os.getenv("REQUIRED_LAMPORTS", "10000000"))
    return build_preview(result, wallet, lamports)

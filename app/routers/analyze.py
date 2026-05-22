from fastapi import APIRouter, Query, HTTPException

from app.config import load_config
from app.services.analyst import run_analysis
from app.services.payment import verify_payment, build_preview

router = APIRouter()


@router.get("/payment-info")
def payment_info():
    config = load_config()
    if not config.payment_wallet:
        raise HTTPException(status_code=500, detail="PAYMENT_WALLET_ADDRESS is not configured")
    return {
        "wallet": config.payment_wallet,
        "amount_sol": config.required_sol,
        "amount_lamports": config.required_lamports,
        "instructions": (
            "Send SOL to this wallet, then call /analyze with "
            "?tx_signature=<your_transaction_signature> to unlock full results."
        ),
    }


@router.get("/analyze")
def analyze(
    startup_idea: str = Query(..., description="Your startup idea"),
    target_audience: str = Query(..., description="Target audience or subreddit (e.g. r/running)"),
    tx_signature: str = Query(None, description="Solana tx signature to unlock full results"),
):
    try:
        config = load_config()
        result = run_analysis(idea=startup_idea, audience=target_audience, config=config)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mistral API error: {str(e)}")

    if tx_signature:
        is_paid, reason = verify_payment(tx_signature, config)
        if is_paid:
            return result
        raise HTTPException(status_code=402, detail=f"Payment invalid: {reason}")

    return build_preview(result, config)

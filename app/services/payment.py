import json
import urllib.request

from app.config import Config


def verify_payment(tx_signature: str, config: Config) -> tuple[bool, str]:
    """
    Returns (is_valid, reason).
    Checks the transaction exists, succeeded, and credited
    at least config.required_lamports to config.payment_wallet.
    """
    if not config.payment_wallet:
        return False, "PAYMENT_WALLET_ADDRESS is not configured"

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_signature,
            {"encoding": "json", "maxSupportedTransactionVersion": 0},
        ],
    }).encode()

    req = urllib.request.Request(
        config.solana_rpc_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
    except Exception as e:
        return False, f"Could not reach Solana RPC: {e}"

    result = body.get("result")
    if not result:
        return False, "Transaction not found on chain"

    if result.get("meta", {}).get("err") is not None:
        return False, "Transaction failed on chain"

    # Handle both legacy (list of strings) and versioned (list of dicts) tx formats
    raw_keys = result["transaction"]["message"]["accountKeys"]
    account_keys = [k if isinstance(k, str) else k.get("pubkey", "") for k in raw_keys]
    pre_balances = result["meta"]["preBalances"]
    post_balances = result["meta"]["postBalances"]

    for i, address in enumerate(account_keys):
        if address == config.payment_wallet:
            received = post_balances[i] - pre_balances[i]
            if received >= config.required_lamports:
                return True, "Payment verified"
            return False, (
                f"Insufficient payment: received {received} lamports, "
                f"required {config.required_lamports}"
            )

    return False, "Payment wallet not found in this transaction"


def build_preview(full_result: dict, config: Config) -> dict:
    """Returns a teaser with only the core problem and one pain point visible."""
    analysis = full_result.get("analysis", {})

    return {
        "preview": True,
        "payment_required": True,
        "payment_info": {
            "wallet": config.payment_wallet,
            "amount_sol": config.required_sol,
            "instructions": (
                "Send SOL to this wallet, then call /analyze again "
                "with ?tx_signature=<your_transaction_signature> to unlock full results."
            ),
        },
        "startup_idea": full_result.get("startup_idea"),
        "target_audience": full_result.get("target_audience"),
        "analysis": {
            "problem_identification": {
                "core_problem": analysis.get("problem_identification", {}).get("core_problem"),
                "severity": analysis.get("problem_identification", {}).get("severity"),
            },
            "pain_problems": analysis.get("pain_problems", [])[:1],
        },
        "locked": [
            "full analysis (target audience breakdown, all pain points)",
            "3 reddit posts",
            "experiment plan",
            "24h simulation with explanations",
            "key insights",
            "MVP direction",
            "build verdict",
        ],
    }

import json
import os
import urllib.request
from pathlib import Path


def _load_env_file() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def verify_payment(tx_signature: str) -> tuple[bool, str]:
    """
    Returns (is_valid, reason).
    Checks that the transaction:
      - exists and was successful
      - credited at least REQUIRED_LAMPORTS to PAYMENT_WALLET_ADDRESS
    """
    _load_env_file()

    rpc_url = os.getenv("SOLANA_RPC_URL", "http://127.0.0.1:8899")
    payment_wallet = os.getenv("PAYMENT_WALLET_ADDRESS", "")
    required_lamports = int(os.getenv("REQUIRED_LAMPORTS", "10000000"))  # 0.01 SOL default

    if not payment_wallet:
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
        rpc_url,
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

    # Account keys can be strings (legacy) or dicts (versioned transactions)
    raw_keys = result["transaction"]["message"]["accountKeys"]
    account_keys = [
        k if isinstance(k, str) else k.get("pubkey", "") for k in raw_keys
    ]
    pre_balances = result["meta"]["preBalances"]
    post_balances = result["meta"]["postBalances"]

    for i, address in enumerate(account_keys):
        if address == payment_wallet:
            received = post_balances[i] - pre_balances[i]
            if received >= required_lamports:
                return True, "Payment verified"
            return False, (
                f"Insufficient payment: received {received} lamports, "
                f"required {required_lamports}"
            )

    return False, "Payment wallet not found in this transaction"


def build_preview(full_result: dict, payment_wallet: str, required_lamports: int) -> dict:
    """Returns a stripped-down preview of the full analysis."""
    analysis = full_result.get("analysis", {})
    pain_problems = analysis.get("pain_problems", [])

    return {
        "preview": True,
        "payment_required": True,
        "payment_info": {
            "wallet": payment_wallet,
            "amount_sol": required_lamports / 1_000_000_000,
            "instructions": (
                "Send SOL to the wallet above, then call /analyze again "
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
            "pain_problems": pain_problems[:1],
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

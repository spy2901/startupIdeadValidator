import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file() -> None:
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Config:
    mistral_api_key: str
    payment_wallet: str
    required_lamports: int
    solana_rpc_url: str

    @property
    def required_sol(self) -> float:
        return self.required_lamports / 1_000_000_000


def load_config() -> Config:
    _load_env_file()
    api_key = os.getenv("MISTRAL_API_KEY", "")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set. Copy .env.example to .env and add your key.")
    return Config(
        mistral_api_key=api_key,
        payment_wallet=os.getenv("PAYMENT_WALLET_ADDRESS", ""),
        required_lamports=int(os.getenv("REQUIRED_LAMPORTS", "10000000")),
        solana_rpc_url=os.getenv("SOLANA_RPC_URL", "http://127.0.0.1:8899"),
    )

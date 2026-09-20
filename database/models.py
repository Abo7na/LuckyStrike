from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: str = "ar"
    is_banned: int = 0
    is_admin: int = 0
    referral_code: str | None = None
    referred_by: int | None = None
    balance: float = 0.0

from sqlalchemy.orm import Mapped, mapped_column
from core.models import Base
from datetime import datetime

class BlacklistedToken(Base):
    __tablename__ = "blacklist_tokens"
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    expires_at: Mapped[datetime]



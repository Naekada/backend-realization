from typing import List, TYPE_CHECKING
from core.models import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

if TYPE_CHECKING:
    from core.models.post import Post
    from core.models.comment import Comment

class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)  
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    posts: Mapped[List["Post"]] = relationship(
        "Post", 
        back_populates="author", 
        cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan"
    )

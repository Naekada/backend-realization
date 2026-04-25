from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from core.models.user import User
from core.models import Base
from datetime import datetime


if TYPE_CHECKING:
    from core.models.user import User
    from core.models.comment import Comment


class Post(Base):
    __tablename__ = "posts"
    title: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    author: Mapped["User"] = relationship(
        "User", back_populates="posts"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    long_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
"""
Emoji Model
===========
Stores the full Unicode emoji dataset imported from the emoji-data JSON.
Each row represents one emoji entry with all metadata needed for the
forum's emoji picker.

Columns that can hold multiple values (emoticons, shortcodes, tags) use
PostgreSQL ARRAY(Text).  For SQLite compatibility the ARRAY type is
monkey-patched at runtime if needed (see cps/forum/__init__.py).
"""
from sqlalchemy import Column, Integer, Text, Boolean

try:
    from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
    _ARRAY = PG_ARRAY(Text)
except Exception:
    # Fallback for SQLite / other dialects: store as plain Text (JSON string)
    _ARRAY = Text

from cps.models.forum import Base


class Emoji(Base):
    """A single emoji entry from the Unicode CLDR / emoji-data dataset."""

    __tablename__ = "forum_emojis"

    # Override the inherited 'id' to make sure it is explicit
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core fields
    annotation = Column(Text, nullable=False)       # Human-readable name, e.g. "grinning face"
    emoji = Column(Text, nullable=False)            # Actual emoji character(s), e.g. "😀"

    # Categorisation
    group = Column(Text)
    subgroup = Column(Text)
    hexcode = Column(Text)                          # e.g. "1F600"
    unicode = Column(Integer)                       # Codepoint as integer
    order = Column(Integer)                         # Sort order within group

    # Flags
    directional = Column(Boolean, default=False)    # True for direction-sensitive glyphs
    variation = Column(Boolean, default=False)      # True if this is a variation sequence

    # Multi-value fields (PostgreSQL ARRAY; Text JSON string on other dialects)
    try:
        from sqlalchemy.dialects.postgresql import ARRAY as _PG
        emoticons = Column(_PG(Text))               # e.g. [":)", ":-D"]
        shortcodes = Column(_PG(Text))              # e.g. [":grinning:", ":grin:"]
        tags = Column(_PG(Text))                    # e.g. ["face", "smile"]
    except Exception:
        emoticons = Column(Text)
        shortcodes = Column(Text)
        tags = Column(Text)

    # Skin-tone support
    skintone = Column(Text, nullable=True)
    skintone_base = Column(Text, nullable=True)
    skintone_combination = Column(Text, nullable=True)
    variation_base = Column(Text, nullable=True)

    def to_json(self):
        return {
            "id": self.id,
            "annotation": self.annotation,
            "emoji": self.emoji,
            "group": self.group,
            "subgroup": self.subgroup,
            "hexcode": self.hexcode,
            "unicode": self.unicode,
            "order": self.order,
            "directional": self.directional,
            "variation": self.variation,
            "emoticons": self.emoticons,
            "shortcodes": self.shortcodes,
            "tags": self.tags,
            "skintone": self.skintone,
            "skintone_base": self.skintone_base,
            "skintone_combination": self.skintone_combination,
            "variation_base": self.variation_base,
        }

    def __repr__(self):
        return f"<Emoji id={self.id} emoji={self.emoji!r} annotation={self.annotation!r}>"

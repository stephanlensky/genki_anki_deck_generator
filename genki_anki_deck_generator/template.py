from dataclasses import dataclass, field


@dataclass
class Card:
    japanese: str
    english: str
    kanjis: str | None = None
    kanjis_meanings: list[str] | None = None
    sound_file: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class Deck:
    cards: list[Card] = field(default_factory=list)

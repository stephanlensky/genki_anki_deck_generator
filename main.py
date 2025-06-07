# load yaml files
# for every soundfile parse
# gen anki file

from src.data import Deck, MetaDeck
from src.anki_exporter import export_to_anki
from pathlib import Path
from typing import List
import shutil
import sys

parse_only = False


def beautify_deck_name(name: str):
    return name.replace(".yaml", "").replace("_", " ").title()


def add_decks(
    path: Path, resources: Path, media_output_path: Path, book_deck: MetaDeck
):
    """Recursively add all decks to a single book-level deck."""
    if path.is_dir():
        for f in sorted(path.iterdir()):
            if f.name.startswith("__"):
                continue
            add_decks(f, resources, media_output_path, book_deck)
    else:
        # Parse the deck as before
        deck = Deck.parse(path, resources)
        deck.name = beautify_deck_name(path.name)
        deck.load_sound_files(resources, media_output_path)
        deck.load_kanji_meaning_data()

        # Add the chapter name as a tag
        chapter_name = beautify_deck_name(path.stem)  # Remove .yaml and format
        for card in deck.cards:
            card.tags.append(chapter_name)

        # Merge the cards into the main book deck
        book_deck.decks.append(deck)


def for_decks(decks: List[MetaDeck], f):
    def walk(d):
        if isinstance(d, MetaDeck):
            for di in d.decks:
                walk(di)
        elif isinstance(d, Deck):
            f(d)

    for d in decks:
        walk(d)


def save_cards_without_sounds(l, d: Deck):
    if d.sound_file is None:
        for c in d.cards:
            l.append(c)


def copy_similar_sounds(l, d: Deck):
    if d.sound_file is not None:
        for c in d.cards:
            for target_card in l:
                if (
                    target_card.kanjis == c.kanjis
                    and c.kanjis != ""
                    or target_card.japanese == c.japanese
                    and c.japanese != ""
                    and c.kanjis == ""
                ):
                    target_card.sound_file = c.sound_file


def check_uids(l, d: Deck):
    assert d.uid not in l
    l.append(d.uid)


if __name__ == "__main__":
    decks: List[MetaDeck] = []

    if len(sys.argv) > 1:
        parse_only = sys.argv[1]

    media_output_path = Path("media_output")
    if media_output_path.exists():
        shutil.rmtree(media_output_path)
    media_output_path.mkdir(exist_ok=True)

    data_path = Path("data")
    for d in data_path.iterdir():
        if d.name == "fonts":
            continue
        if not d.is_dir():
            continue

        # Create a single MetaDeck for the entire book
        book_deck = MetaDeck()
        book_deck.name = beautify_deck_name(d.name)
        decks.append(book_deck)

        resources = d.joinpath("sound")
        templates = d.joinpath("templates")

        for f in sorted(templates.iterdir()):
            add_decks(f, resources, media_output_path, book_deck)

    # Copy similar sounds
    cards_without_sounds = []
    for_decks(decks, lambda d: save_cards_without_sounds(cards_without_sounds, d))
    for_decks(decks, lambda d: copy_similar_sounds(cards_without_sounds, d))

    # UID sanity check
    uids = []
    for_decks(decks, lambda d: check_uids(uids, d))

    export_to_anki(decks)

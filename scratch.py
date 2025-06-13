import json
from pathlib import Path, PurePosixPath
from typing import Any, Generator

import pygame
import pykakasi
from yaml import safe_dump, safe_load

kks = pykakasi.kakasi()
pygame.mixer.init()


def iter_cards(template: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    if "vocabulary" in template:
        for card in template["vocabulary"]:
            yield from iter_cards(card)
    if "japanese" in template:
        yield template


def increment_sound_index(cards: list[dict[str, Any]], increment: int) -> None:
    for card in cards:
        sound_file = card.get("sound_file")
        if sound_file is None:
            continue

        idx = int(Path(sound_file).stem)
        idx += increment
        card["sound_file"] = str(PurePosixPath(sound_file).with_name(f"{idx}.mp3"))


def main() -> None:
    templates: list[tuple[Path, dict]] = []
    for file in Path("config/decks").glob("**/*.yaml"):
        if file.name == "audio.yaml":
            continue
        with open(file, "r", encoding="utf-8") as f:
            templates.append((file, safe_load(f)))

    templates.sort(key=lambda x: x[0].parts[1:])

    if Path("progress.json").exists():
        with open("progress.json", "r", encoding="utf-8") as f:
            progress = json.load(f)
    else:
        progress = {"completed": []}

    for template_file, template in templates:
        if str(template_file) in progress["completed"]:
            print(f"Skipping {template_file.name}, already completed.")
            continue
        print("Processing:", template_file)
        cards = list(iter_cards(template))
        if not any(card.get("sound_file") for card in cards):
            print(f"No sound files found in {template_file.name}, skipping...")
            continue

        deck = template_file.parent.parent.name

        for i, card in enumerate(cards):
            if "sound_file" not in card:
                continue

            japanese = card.get("japanese")
            kks_convert = kks.convert(japanese)
            romaji = " ".join([item["hepburn"].strip() for item in kks_convert]).strip()
            print(f"{japanese} - {romaji}")
            response = None
            try:
                while True:
                    sound_file = card.get("sound_file")
                    while response not in ("y", "j", "k", ""):
                        print(f"Sound file: {sound_file}, is this correct? (Y/j/k) ", end="")
                        pygame.mixer.music.load(Path("sources/audio") / deck / Path(sound_file))
                        pygame.mixer.music.play()
                        response = input().strip().lower()
                    if response == "j":
                        increment_sound_index(cards[i:], -1)
                        if not (
                            Path("sources/audio") / deck / Path(cards[i].get("sound_file"))
                        ).exists():
                            print(
                                f"Error: can't decrement, {cards[i].get('sound_file')} does not exist."
                            )
                            increment_sound_index(cards[i:], 1)
                    elif response == "k":
                        increment_sound_index(cards[i:], 1)
                        if not (
                            Path("sources/audio") / deck / Path(cards[i].get("sound_file"))
                        ).exists():
                            print(
                                f"Error: can't increment, {cards[i].get('sound_file')} does not exist."
                            )
                            increment_sound_index(cards[i:], -1)
                    elif response == "y" or response == "":
                        break
                    response = None
            except KeyboardInterrupt:
                print(f"\nExiting, saving progress on {template_file.name}...")
                with open(template_file, "w", encoding="utf-8") as f:
                    safe_dump(
                        template, f, allow_unicode=True, default_flow_style=False, sort_keys=False
                    )

                return
        with open(template_file, "w", encoding="utf-8") as f:
            safe_dump(template, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        progress["completed"].append(str(template_file))
        with open("progress.json", "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

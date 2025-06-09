import json
from pathlib import Path
from typing import Any

from yaml import safe_dump, safe_load


def process_card(
    card: dict[str, Any],
    sound_file: str | None,
    skip_words: dict[int, bool],
    only_japanese: bool,
    template: dict[str, Any],
    deck: str,
    card_count: int = 0,
) -> tuple[int, dict[str, Any]]:
    if "category" in card:
        category_cards = []
        for c in card["vocabulary"]:
            card_count, processed = process_card(
                c, sound_file, skip_words, only_japanese, template, deck, card_count
            )
            category_cards.append(processed)

        tags = card["category"] if isinstance(card["category"], list) else [card["category"]]
        return card_count, {"tags": tags, "vocabulary": category_cards}

    card_count += 1
    if sound_file:
        sound_folder = Path(sound_file).parent / Path(sound_file).stem
        i = 0
        j = 0
        while j < card_count:
            if skip_words.get(i, False):
                i += 1
            else:
                j += 1
                i += 1
        if only_japanese:
            japanese_sound = str(sound_folder / f"{(i - 1)}.mp3")
            english_sound = None
        else:
            japanese_sound = str(sound_folder / f"{(i) + (card_count - 1 * 2)}.mp3")
            # english_sound = str(sound_folder / f"{(i) + (card_count - 1 * 2) + 1}.mp3")
            english_sound = None
    else:
        japanese_sound = None
        english_sound = None
    new_card = {
        "japanese": card["japanese"],
    }
    new_card["english"] = card["english"]
    if english_sound:
        new_card["english_sound"] = english_sound
    if card.get("kanji"):
        new_card["kanji"] = card["kanji"]
    if japanese_sound:
        new_card["sound_file"] = japanese_sound
    if ";" in card["english"] and not only_japanese:
        fuse_with_next = card.get("skip_on_semicolon", template.get("skip_on_semicolon", True))
        if isinstance(fuse_with_next, bool):
            fuse_with_next = card["english"].count(";") if fuse_with_next else 0
        if fuse_with_next > 0 and sound_file:
            print(card["english"], fuse_with_next, japanese_sound)
            original_japanese_sound = Path(japanese_sound).parent.with_suffix(".mp3")
            audio_yaml = Path("config/decks") / deck / "audio.yaml"
            with open(audio_yaml, "r", encoding="utf-8") as f:
                audio_config = safe_load(f)

            for audio_file_config in audio_config["audio"]:
                if audio_file_config["sound_file"] == sound_file:
                    if "overrides" not in audio_file_config:
                        audio_file_config["overrides"] = {}
                    audio_file_config["overrides"][int(Path(japanese_sound).stem) + 1] = {
                        "fuse_with_next": fuse_with_next
                    }
                    break

            with open(audio_yaml, "w", encoding="utf-8") as f:
                safe_dump(
                    audio_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False
                )

    return card_count, new_card


templates: list[tuple[Path, dict]] = []
for file in Path("config_orig/decks").glob("**/*.yaml"):
    if file.name == "audio.yaml":
        continue
    with open(file, "r", encoding="utf-8") as f:
        templates.append((file, safe_load(f)))
        # print(f"Loaded {file}")

templates.sort(key=lambda x: x[0].parts[1:])

for template_file, template in templates:
    target_path = Path("config/" + "/".join(template_file.parts[1:]))
    with open(f"temp/{template.get('uid')}.json", "r", encoding="utf-8") as f:
        skip_words = json.load(f)

    skip_words_dict = {}
    for s in skip_words["skip_words"]:
        skip_words_dict[int(s)] = True

    deck = template_file.parent.parent.name.replace("_", " ").title().replace(" ", "_")
    lesson = "Lesson_" + template_file.parent.name.replace("L", "").removeprefix("0")
    top_category = template_file.stem.replace("_", " ").title().replace(" ", "_")
    sound_file = template.get("sound_file") or None
    only_japanese = template.get("only_japanese", False)
    new_template = process_card(
        {"category": [deck, lesson, top_category], "vocabulary": template["cards"]},
        sound_file,
        skip_words_dict,
        True if only_japanese == 1 else False,
        template,
        template_file.parent.parent.name,
    )[1]
    with open(target_path, "w", encoding="utf-8") as f:
        safe_dump(new_template, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        # print(f"Saved {target_path}")

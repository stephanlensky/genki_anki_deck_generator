import json
from pathlib import Path
from typing import Any

from yaml import safe_dump, safe_load


def main() -> None:
    templates: list[tuple[Path, dict]] = []
    for file in Path("config/decks").glob("**/*.yaml"):
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
            safe_dump(
                new_template, f, allow_unicode=True, default_flow_style=False, sort_keys=False
            )
            # print(f"Saved {target_path}")

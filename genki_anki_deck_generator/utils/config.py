import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import yaml

CONFIG_PATH = Path("config/config.toml")
DECKS_PATH = Path("config/decks")


@dataclass
class ConfigSources:
    audio: dict[str, str]
    fonts: str


@dataclass
class Config:
    decks: dict[str, str]
    download_dir: Path
    sources: ConfigSources


@dataclass
class DeckAudioFileOverride:
    fuse_with_next: int | None = None
    resplit: int | None = None


@dataclass
class DeckAudioFile:
    sound_file: Path
    sound_silence_threshold: int
    overrides: dict[int, DeckAudioFileOverride] | None = None


@dataclass
class DeckConfig:
    audio: list[DeckAudioFile]


@cache
def get_config() -> Config:
    with open(CONFIG_PATH, "rb") as f:
        config_dict = tomllib.load(f)

    return Config(
        decks=config_dict["settings"]["decks"],
        download_dir=Path(config_dict["settings"]["download_dir"]),
        sources=ConfigSources(
            audio=config_dict["settings"]["sources"]["audio"],
            fonts=config_dict["settings"]["sources"]["fonts"],
        ),
    )


@cache
def get_deck_config(deck_name: str) -> DeckConfig:
    deck_config_path = DECKS_PATH / deck_name
    audio_config = deck_config_path / "audio.yaml"

    with open(audio_config, "r") as f:
        audio_dict = yaml.safe_load(f)

    return DeckConfig(
        audio=[
            DeckAudioFile(
                sound_file=Path(item["sound_file"]),
                sound_silence_threshold=item["sound_silence_threshold"],
                overrides={
                    int(k): DeckAudioFileOverride(**v) for k, v in item.get("overrides", {}).items()
                }
                or None,
            )
            for item in audio_dict["audio"]
        ]
    )


def set_config_path(path: Path) -> None:
    global CONFIG_PATH
    CONFIG_PATH = path
    get_config.cache_clear()


def set_decks_path(path: Path) -> None:
    global DECKS_PATH
    DECKS_PATH = path
    get_deck_config.cache_clear()

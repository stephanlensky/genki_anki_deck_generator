import argparse
import shutil
import sys
from pathlib import Path

from genki_anki_deck_generator.utils.config import (
    CONFIG_PATH,
    DECKS_PATH,
    get_config,
    get_deck_config,
    set_config_path,
    set_decks_path,
)
from genki_anki_deck_generator.utils.google_drive import google_drive_download
from genki_anki_deck_generator.utils.sound import split_audio_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Genki Anki decks from official Genki audio files"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=f"{CONFIG_PATH}",
        help=f"Path to the configuration file (default: {CONFIG_PATH})",
    )
    parser.add_argument(
        "--decks",
        "-d",
        type=str,
        default=f"{DECKS_PATH}",
        help=f"Path to the decks directory (default: {DECKS_PATH})",
    )
    parser.add_argument(
        "--reprocess",
        "-r",
        action="store_true",
        help="Reprocess audio files even if they already exist",
    )
    args = parser.parse_args()
    set_config_path(Path(args.config))
    set_decks_path(Path(args.decks))

    _download_files()
    _preprocess_audio(args.reprocess)


def _download_files() -> None:
    config = get_config()
    audio_dir = config.download_dir / "audio"
    fonts_dir = config.download_dir / "fonts"

    for deck in config.decks:
        deck_dir = audio_dir / deck
        if not deck_dir.exists():
            google_drive_download(
                file_id=config.sources.audio[deck], destination=deck_dir, unzip=True
            )
        else:
            print(f"Skipping download of {config.decks[deck]} audio, already exists at {deck_dir}")

    if not fonts_dir.exists():
        google_drive_download(
            file_id=config.sources.fonts, destination=fonts_dir / "_NotoSansCJKjp-Regular.woff2"
        )
    else:
        print(f"Skipping download of fonts, already exists at {fonts_dir}")


def _preprocess_audio(reprocess: bool) -> None:
    config = get_config()
    to_process = []
    for deck_name in config.decks:
        deck_config = get_deck_config(deck_name)
        audio_dir = config.download_dir / "audio" / deck_name
        for audio_file in deck_config.audio:
            sound_file = audio_dir / audio_file.sound_file
            if not sound_file.exists():
                print(f"Error: Audio file {sound_file} does not exist!")
                sys.exit(1)

            target_dir = sound_file.parent / sound_file.stem
            if target_dir.is_dir() and any(target_dir.iterdir()):
                if reprocess:
                    shutil.rmtree(target_dir, ignore_errors=True)
                else:
                    print(f"Skipping {sound_file}, target directory exists and is not empty.")
                    continue

            overrides = audio_file.overrides or {}
            to_process.append(
                (
                    sound_file,
                    target_dir,
                    audio_file.sound_silence_threshold,
                    overrides,
                )
            )

    for sound_file, target_dir, silence_threshold, overrides in to_process:
        print(f"Processing audio file: {sound_file} -> {target_dir}")
        try:
            split_audio_file(
                file=sound_file,
                target_dir=target_dir,
                sound_silence_threshold=silence_threshold,
                overrides=overrides,
            )
        except KeyboardInterrupt:
            print("Interrupted! Deleting partially processed directory")
            shutil.rmtree(target_dir, ignore_errors=True)
            raise


if __name__ == "__main__":
    main()

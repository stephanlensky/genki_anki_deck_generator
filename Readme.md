# Genki Vocabulary Anki Deck Generator

This Python project extracts vocabulary audio from the official Genki audio files and generates Anki decks.

- **Genki 1 Deck:** [AnkiWeb](https://ankiweb.net/shared/info/1530967642)  
- **Genki 2 Deck:** [AnkiWeb](https://ankiweb.net/shared/info/850772012)

## How to Build

1. Clone the repository.
2. Install `ffmpeg`.
3. Create a virtual environment:  
    ```sh
    python -m venv venv
    ```
4. Activate the virtual environment:
    ```
    source venv/bin/activate
    ```
5. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
6. Download necessary resources:
    ```
    python download_genki_sound_files.py
    python download_fonts.py
    ```
7. Run the main script:
    ```
    python main.py
    ```
8. Enjoy your generated Anki decks!

## Project Structure
- Folders inside `data/` are converted into Anki decks.
- Deck generation is based on YAML files in the `templates/` directory.

## Template File Explanation

Each template file follows this structure:

- **`sound_file`** *(string)* – The sound file used for this deck (searches within the `sound/` directory).
- **`skip_on_beginning`** *(integer)* – Number of words to skip at the beginning of the sound file.
- **`skip_with_new_category`** *(boolean)* – If `true`, skips a word when a new category starts.
- **`skip_on_semicolon`** *(boolean)* – If `true`, skips as many words as there are semicolons in the English translation, after a note.
- **`uid`** *(integer)* – Unique ID used for Anki (should not be too high).
- **`sound_silence_threshold`** *(integer)* – A threshold value for splitting Genki audio files into separate words (default: `600`).
- **`cards`** – List of categories.
  - **`category`** *(string)* – Name of the category (used for tagging).
  - **`vocabulary`** – List of vocabulary words.
    - **`japanese`** *(string)* – Japanese meaning in kana.
    - **`english`** *(string)* – English meaning.
    - **`kanji`** *(string, optional)* – Japanese meaning in kanji (omit if none).

## Notes

- This project has only been tested on MacOS.

## Contributions Welcome!

Feel free to submit a pull request for:
- Adding Windows support.
- Improving the Anki deck descriptions.
- Enhancing automation (DevOps).
- Bug fixes and other improvements.

## Copyright Notice

I do not own the copyright for the Genki audio files. They are **not included** in this repository but are publicly available without requiring proof of Genki book ownership.

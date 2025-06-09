from pathlib import Path

from pydub import AudioSegment
from pydub.silence import split_on_silence


def _detect_leading_silence(
    sound: AudioSegment, silence_threshold: float = -50.0, chunk_size: int = 10
) -> int:
    """
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    """
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms : trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def _split_words(
    file: Path, sound_silence_threshold: int, fuse: dict[int, int] | None = None
) -> list[AudioSegment]:
    sound_file = AudioSegment.from_mp3(file)
    audio_chunks: list[AudioSegment] = split_on_silence(
        sound_file,
        keep_silence=True,
        min_silence_len=sound_silence_threshold,
        silence_thresh=-32,
    )
    for i, chunk in enumerate(audio_chunks):
        start_trim = _detect_leading_silence(chunk)
        audio_chunks[i] = chunk[start_trim:]

    words: list[AudioSegment] = []
    i = 0
    while i < len(audio_chunks):
        sound = audio_chunks[i]
        if fuse and i in fuse:
            for j in range(fuse[i]):
                print("Fusing chunk", i + j + 1, "with chunk", i, f"(word {len(words)})")
                sound = sound.append(audio_chunks[i + j + 1], crossfade=0)
            i += fuse[i]

        words.append(sound)
        i += 1

    return words


def split_audio_file(
    file: Path, target_dir: Path, sound_silence_threshold: int, fuse: dict[int, int] | None = None
) -> None:
    """
    Splits the audio file into segments based on silence.
    Returns a list of AudioSegment objects.
    """
    words = _split_words(file, sound_silence_threshold, fuse)

    target_dir.mkdir(parents=True, exist_ok=True)
    for i, word in enumerate(words):
        word.export(target_dir / f"{i}.mp3", format="mp3")

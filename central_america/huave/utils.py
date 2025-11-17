import csv
from pydub import AudioSegment


def load_audio(audio_file_path: str):
    try:
        print(f"Loading audio file: {audio_file_path}...")
        full_audio = AudioSegment.from_wav(audio_file_path)
        audio_mono = full_audio.set_channels(1)
        print("Audio loaded successfully.")
    except FileNotFoundError:
        print(f"ERROR: Audio file '{audio_file_path}' not found.")
        return
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return
    return audio_mono


def update_tsv_file(tsv_file_name: str, data: list, header: list):
    with open(tsv_file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        # Write header
        if header:
            writer.writerow(header)
        # Write all data rows
        writer.writerows(data)

import re
import os
import uuid
import glob
from utils import load_audio, update_tsv_file

BASE_PATH = "file_name_transcriptions/entonacion_huave_gama"
OUTPUT_CLIPS = "clips"
OUTPUT_TSV_FILE = "huave_corpus.tsv"


def extract_tags(transcription: str):
    tags_pattern = r"(?:neg|int|\d+)"
    match = re.search(rf"((?:_{tags_pattern}_?)+)\.wav$", transcription)
    clean_text = transcription[: match.start()].replace("_", " ")
    tags = f"{','.join(filter(None, match.group(1).split('_')))}"
    return clean_text, tags


def process_audios():
    data = []
    if not os.path.exists(OUTPUT_CLIPS):
        os.makedirs(OUTPUT_CLIPS)
        print(f"Created dir: {OUTPUT_CLIPS}")

    for file in glob.glob(os.path.join(BASE_PATH, "*.wav")):
        audio_id = uuid.uuid4()
        audio = load_audio(file)
        file_name = file.split("/")[-1]
        audio_duration = len(audio)
        transcription, tags = extract_tags(file_name)
        new_audio_file = f"{audio_id}.wav"
        audio.export(os.path.join(OUTPUT_CLIPS, new_audio_file), format="wav")
        data.append(
            [
                str(audio_id),
                new_audio_file,
                audio_duration,
                transcription,
                "",
                tags,
                file_name,
            ]
        )
    header = [
        "audio_id",
        "audio_file",
        "duration_ms",
        "transcription",
        "translation",
        "tags",
        "original_audio_name",
    ]
    update_tsv_file(OUTPUT_TSV_FILE, data, header)


process_audios()

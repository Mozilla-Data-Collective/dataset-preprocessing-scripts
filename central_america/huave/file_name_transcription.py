import re
import os
import uuid
import glob
from utils import load_audio


def extract_tags(transcription: str):
    tags_pattern = r"(?:neg|int|\d+)"
    match = re.search(rf"((?:_{tags_pattern}_?)+)\.wav$", transcription)
    clean_text = transcription[: match.start()].replace("_", " ")
    tags = f"{','.join(filter(None, match.group(1).split('_')))}"
    return clean_text, tags


def process_audios(base_path, output_path):
    data = []
    for file in glob.glob(os.path.join(base_path, "*.wav")):
        audio_id = uuid.uuid4()
        audio = load_audio(file)
        file_name = file.split("/")[-1]
        audio_duration = len(audio)
        transcription, tags = extract_tags(file_name)
        new_audio_file = f"{audio_id}.wav"
        audio.export(os.path.join(output_path, new_audio_file), format="wav")
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
    return data

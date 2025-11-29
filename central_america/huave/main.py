import os
import uuid
import glob
from sys import argv

from elan_preprocessor import (
    get_data_from_elan_file,
    get_valid_sorted_items,
    slice_and_export_audio,
)
from file_name_transcription import process_audios
from audio_converter import convert_audios_to_mono_mp3
from utils import load_audio, update_tsv_file

OUTPUT_PATH = argv[1]
ELAN_DATA_PATH = "elan_transcriptions"
FILE_NAME_TRANS_PATH = "file_name_transcriptions"
RAW_AUDIOS_PATH = "raw_audios"

TSV_HEADER = [
    "audio_id",
    "audio_file",
    "duration_ms",
    "transcription",
    "translation",
    "tags",
    "original_audio_name",
]


def main():
    output_clips_dir = os.path.join(OUTPUT_PATH, "audios")
    output_raw_audios_dir = os.path.join(OUTPUT_PATH, "raw_audios")
    output_tsv_file = os.path.join(OUTPUT_PATH, "huave_dataset.tsv")

    # Ensure output directory exists for clips
    os.makedirs(output_clips_dir, exist_ok=True)
    os.makedirs(output_raw_audios_dir, exist_ok=True)

    if not os.path.isfile(output_tsv_file):
        # Creating TSV file with header
        update_tsv_file(output_tsv_file, [], TSV_HEADER)

    # Pre-process/Normalize Raw Audios ---
    # Convert all inputs in RAW_AUDIOS_PATH to standardized MP3s in the output folder
    print("--- Starting Audio Normalization ---")
    convert_audios_to_mono_mp3(RAW_AUDIOS_PATH, output_raw_audios_dir)
    print("--- Audio Normalization Done ---\n")

    print("--- Starting ELAN Files processing---")
    # 1. Elan Data processing
    for file in glob.glob(os.path.join(ELAN_DATA_PATH, "*", "*.eaf")):
        elan_data = get_data_from_elan_file(file)
        print(f"File {file} has #{len(elan_data)} chunks with transcriptions")
        current_elan_path = file.split("/")[-2]
        original_audio_path = glob.glob(
            os.path.join(ELAN_DATA_PATH, current_elan_path, "*.wav")
        )[0]
        full_audio = load_audio(original_audio_path)
        original_audio_basename = os.path.basename(original_audio_path)
        sorted_valid_items = get_valid_sorted_items(elan_data)

        # 2. Process each valid segment
        tsv_data = []
        for key, data in sorted_valid_items:
            try:
                start_sec = data["start_float"]
                end_sec = data["end_float"]
                transcription = data["transcription"]
                translation = data.get("translation", "")

                # Generate clip specific paths and IDs
                audio_id = str(uuid.uuid4())
                output_clip_path = os.path.join(output_clips_dir, audio_id) + ".mp3"

                # Slice audio and export
                success, duration_ms = slice_and_export_audio(
                    full_audio, float(start_sec), float(end_sec), output_clip_path
                )
                if success:
                    # Add row data
                    tsv_data.append(
                        [
                            audio_id,
                            os.path.basename(output_clip_path),
                            duration_ms,
                            transcription,
                            translation,
                            "",
                            original_audio_basename,
                        ]
                    )
            except Exception as e:
                # Catch errors related to data structure, but not file I/O (which is caught inside _slice_and_export_audio)
                print(f"  ERROR processing clip data for {key}: {e}")
        # Update the final manifest tsv file
        update_tsv_file(output_tsv_file, tsv_data)
        print(
            f"Successfully generated {len(tsv_data)} audio clips in '{output_tsv_file}' (missing count={len(elan_data) - len(tsv_data)})"
        )
        print("--- ELAN Files processing DONE---")

        print("--- Tramscription processing ---")
        # Process audios with transcriptions in their name files
        transcription_data = process_audios(FILE_NAME_TRANS_PATH, output_clips_dir)
        # update the final manifest tsv file
        update_tsv_file(output_tsv_file, transcription_data)
        print(f"Successfully update {len(transcription_data)} rows on tsv file")
        print("--- Transcription processing DONE---")


if __name__ == "__main__":
    main()

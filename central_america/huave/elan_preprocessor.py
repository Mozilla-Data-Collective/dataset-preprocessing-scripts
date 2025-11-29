import os
from speach import elan
from pydub import AudioSegment

BASE_PATH = "rana/"
OUTPUT_CLIPS = "clips_elan/"
INPUT_TIMESTAMP_FILE = "rana_shc.csv"


def get_data_from_elan_file(elan_file_path: str):
    processed_data = {}
    # TODO: add exception
    with open(elan_file_path, encoding="utf-8") as f:
        eaf_file = elan.parse_eaf_stream(f)
    for tier in eaf_file.tiers():
        # Checking tiers with transcriptions
        if str(tier.ID).startswith("tx") or str(tier.ID).startswith("tl"):
            for anno in tier.annotations:
                if anno.value:
                    _from_ts = (
                        f"{anno.from_ts.sec:.3f}" if anno.from_ts is not None else ""
                    )
                    _to_ts = f"{anno.to_ts.sec:.3f}" if anno.to_ts is not None else ""
                    if anno.duration is not None:
                        _duration = float(f"{anno.duration:.3f}")
                    else:
                        # MAnual calculation
                        _duration = float(_to_ts) - float(_from_ts)
                    text = anno.value
                    key = (str(_from_ts), str(_to_ts))
                    if key not in processed_data:
                        processed_data[key] = {}
                    if (
                        tier.participant
                        and "participant" not in processed_data[key].keys()
                    ):
                        processed_data[key]["participant"] = tier.participant
                    # Transcription
                    if str(tier.ID).startswith("tx"):
                        processed_data[key]["transcription"] = text
                    elif str(tier.ID).startswith("tl"):
                        processed_data[key]["translation"] = text

                    processed_data[key]["start_float"] = _from_ts
                    processed_data[key]["end_float"] = _to_ts
                    processed_data[key]["duration"] = _duration
    return processed_data


def get_valid_sorted_items(elan_data: dict) -> list[tuple]:
    """Sorts ELAN data items by start time and filters for required fields."""
    # Sort items by start time to ensure audio_id is sequential
    sorted_items = sorted(
        elan_data.items(), key=lambda item: item[1].get("start_float", 0)
    )

    valid_items = []
    for key, data in sorted_items:
        # Check if we have BOTH transcription and translation
        if "transcription" in data:
            valid_items.append((key, data))
        else:
            print(f"  INFO: Skipping time {key} - missing transcription.")

    return valid_items


def slice_and_export_audio(
    full_audio: AudioSegment, start_sec: float, end_sec: float, output_clip_path: str
):
    """Slices the full audio and exports the clip to the specified path."""
    try:
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)

        print(
            f"  Slicing and exporting: {os.path.basename(output_clip_path)} ({start_sec}s to {end_sec}s)"
        )
        clip = full_audio[start_ms:end_ms]
        clip.export(output_clip_path, format="mp3")
        return True, end_ms - start_ms
    except Exception as e:
        print(f"  ERROR slicing/exporting audio: {e}")
        return False, 0


"""def chunk_audio(elan_data: dict, output_path: str):
    print("Processing audio clips and building manifest...")
    tsv_rows = []
    audio_id_counter = 1

    # Sort items by start time to ensure audio_id is sequential
    sorted_items = sorted(
        elan_data.items(), key=lambda item: item[1].get("start_float", 0)
    )

    for key, data in sorted_items:
        # Check if we have BOTH transcription and translation
        if "transcription" in data and "translation" in data:
            try:
                # Get data
                start_sec = data["start_float"]
                end_sec = data["end_float"]
                transcription = data["transcription"]
                translation = data["translation"]

                # Generate names and IDs
                audio_id = audio_id_counter
                audio_file_name = f"{audio_id}_{original_audio_basename}.wav"
                output_clip_path = os.path.join(OUTPUT_CLIPS, audio_file_name)

                # Calculate times
                start_ms = int(start_sec * 1000)
                end_ms = int(end_sec * 1000)
                duration_ms = end_ms - start_ms

                # Slice audio and export
                print(
                    f"  Slicing and exporting: {audio_file_name} ({start_sec}s to {end_sec}s)"
                )
                clip = full_audio[start_ms:end_ms]
                clip.export(output_clip_path, format="wav")

                # Add data for the TSV file
                tsv_rows.append(
                    [audio_id, audio_file_name, duration_ms, transcription, translation]
                )

                # Increment the ID for the next valid clip
                audio_id_counter += 1

            except Exception as e:
                print(f"  ERROR processing clip for {key}: {e}")
        else:
            print(
                f"  INFO: Skipping time {key} - missing transcription or translation."
            )

    # 5. Final Step: Write the TSV file
    if not tsv_rows:
        print("\nWARNING: No valid clips were processed. TSV file will be empty.")
        return

    try:
        with open(OUTPUT_TSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            # Write header
            writer.writerow(
                [
                    "audio_id",
                    "audio_file",
                    "duration_ms",
                    "transcription",
                    "translation",
                ]
            )
            # Write all data rows
            writer.writerows(tsv_rows)

        print("\nProcessing complete!")
        print(f"Successfully generated {len(tsv_rows)} audio clips in '{OUTPUT_DIR}'.")
        print(f"Manifest file saved to: {OUTPUT_TSV_FILE}")

    except Exception as e:
        print(f"\nERROR: Could not write TSV file: {e}")"""

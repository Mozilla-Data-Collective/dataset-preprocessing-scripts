import os
import glob
from pydub import AudioSegment
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
)


def convert_audios_to_mono_mp3(source_dir: str, dest_dir: str):
    """
    Scans source_dir for audio files, converts them to Mono MP3,
    and saves them to dest_dir with a rich progress bar.
    """
    os.makedirs(dest_dir, exist_ok=True)

    # 1. Gather files
    extensions = ["*.wav", "*.aif", "*.aiff", "*.mp3"]
    files_to_process = []
    for ext in extensions:
        files_to_process.extend(glob.glob(os.path.join(source_dir, ext)))

    total_files = len(files_to_process)

    if total_files == 0:
        print(f"No audio files found in {source_dir}")
        return

    # 2. Process with Rich Progress Bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task("Initializing...", total=total_files)

        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            output_path = os.path.join(dest_dir, f"{name_without_ext}.mp3")

            # Update description to show current file
            progress.update(task_id, description=f"Converting: {filename}")

            try:
                # Skip if already exists (optional, remove if you want to overwrite)
                if os.path.exists(output_path):
                    progress.console.print(
                        f"[yellow]Skipped (exists):[/yellow] {filename}"
                    )
                else:
                    # Conversion Logic
                    audio = AudioSegment.from_file(file_path)
                    audio_mono = audio.set_channels(1)
                    audio_mono.export(output_path, format="mp3")

            except Exception as e:
                progress.console.print(f"[red]Error converting {filename}:[/red] {e}")

            # Advance bar
            progress.advance(task_id)

    print(f"\n[green]Batch conversion finished. Processed {total_files} files.[/green]")

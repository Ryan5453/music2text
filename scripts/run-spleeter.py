"""
This assumes you have a directory structure like this:

/root
    /<ISRC>
        /audio.mp3  # Original audio
"""

import argparse
import os
import time
from typing import Tuple

from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator


def load_and_separate_audio(
    separator: Separator, audio_adapter: AudioAdapter, input_path: str
) -> Tuple[dict, int]:
    """
    Loads and separates an audio file using Spleeter.

    :param separator: The Spleeter separator instance
    :param audio_adapter: The audio adapter for loading/saving files
    :param input_path: Path to the input audio file
    :return: Tuple of (separated sources, sample rate)
    """
    waveform, sample_rate = audio_adapter.load(
        input_path, sample_rate=separator._sample_rate
    )
    start_time = time.time()
    sources = separator.separate(waveform)
    separation_time = time.time() - start_time
    return sources, sample_rate, separation_time


def extract_vocals(
    separator: Separator, audio_adapter: AudioAdapter, root_path: str, isrc: str
) -> float:
    """
    Extracts vocals from an audio file using Spleeter.

    :param separator: The Spleeter separator instance
    :param audio_adapter: The audio adapter for loading/saving files
    :param root_path: Root directory containing ISRC folders
    :param isrc: ISRC identifier for the current folder
    :return: Time taken for separation in seconds
    """
    input_path = os.path.join(root_path, isrc, "audio.mp3")
    output_path = os.path.join(root_path, isrc, "spleeter.wav")

    sources, sample_rate, separation_time = load_and_separate_audio(
        separator, audio_adapter, input_path
    )

    audio_adapter.save(output_path, sources["vocals"], sample_rate, "wav", "128k")

    return separation_time


def process_files(root_path: str):
    """
    Processes all audio files in the given directory.

    :param root_path: Root directory containing ISRC folders
    """
    print("\nProcessing files with Spleeter...")
    print("-----------------------------------------------------")

    # Initialize model once
    separator = Separator("spleeter:2stems")
    audio_adapter = AudioAdapter.default()

    total_start = time.time()
    processed = 0
    total_separation_time = 0

    for root, dirs, files in os.walk(root_path):
        if root == root_path:
            continue

        isrc = os.path.basename(root)

        try:
            print(f"Processing {isrc}...")
            separation_time = extract_vocals(separator, audio_adapter, root_path, isrc)
            processed += 1
            total_separation_time += separation_time
            print(f"Successfully processed {isrc}\n")
        except Exception as e:
            print(f"Error processing {isrc}: {str(e)}\n")

    total_time = time.time() - total_start
    print(f"\nProcessed {processed} files in {total_time:.2f}s")
    print(f"Average separation time per file: {total_separation_time/processed:.2f}s")


def main():
    """
    Extract vocals from audio files using Spleeter.
    """
    parser = argparse.ArgumentParser(
        description="Extract vocals from audio files using Spleeter"
    )
    parser.add_argument(
        "--directory", type=str, required=True, help="Directory containing ISRC folders"
    )

    args = parser.parse_args()
    process_files(args.directory)


if __name__ == "__main__":
    main()

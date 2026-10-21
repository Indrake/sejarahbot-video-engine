import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip


DEFAULT_MODEL = os.environ.get("WHISPER_MODEL", "tiny")
DEFAULT_LANG = os.environ.get("WHISPER_LANG", "id")
DEFAULT_TARGET = int(os.environ.get("CLIP_TARGET_SECONDS", "45"))
DEFAULT_MIN = int(os.environ.get("CLIP_MIN_SECONDS", "30"))


def find_ffmpeg() -> str:
    if os.environ.get("FFMPEG_BIN"):
        env_path = os.environ["FFMPEG_BIN"]
        if os.path.exists(env_path):
            return env_path

    candidates = [
        "ffmpeg",
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/data/data/com.termux/files/usr/bin/ffmpeg",
    ]
    for candidate in candidates:
        if candidate == "ffmpeg":
            resolved = shutil.which("ffmpeg")
            if resolved:
                return resolved
        elif os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "ffmpeg tidak ditemukan. Install ffmpeg lewat Termux/Android atau pastikan PATH benar."
    )


def _safe_tmp_dir(prefix: str = "clipper_") -> str:
    return tempfile.mkdtemp(prefix=prefix)


def extract_audio_from_video(video_path: str, audio_path: str) -> str:
    ffmpeg = find_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path


def transcribe_audio(audio_path: str, model_size: str = DEFAULT_MODEL, language: str = DEFAULT_LANG):
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language=language, beam_size=5)
    return list(segments)


def _format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments, srt_path: str):
    with open(srt_path, "w", encoding="utf-8") as f:
        index = 1
        for seg in segments:
            text = seg.text.strip().replace("\n", " ")
            if not text:
                continue
            start = _format_timestamp(seg.start)
            end = _format_timestamp(seg.end)
            f.write(f"{index}\n{start} --> {end}\n{text}\n\n")
            index += 1


def get_video_duration(video_path: str) -> float:
    with VideoFileClip(video_path) as clip:
        return float(clip.duration)


def create_clip_segments(video_path: str, target_seconds: int = DEFAULT_TARGET, min_seconds: int = DEFAULT_MIN):
    total = get_video_duration(video_path)
    if total <= 0:
        return [(0.0, 0.0)]

    if total <= target_seconds:
        return [(0.0, total)]

    chunks = []
    start = 0.0
    while start < total:
        remaining = total - start
        segment_duration = min(target_seconds, remaining)
        end = min(start + segment_duration, total)

        if end - start < min_seconds and chunks:
            prev_start, prev_end = chunks[-1]
            chunks[-1] = (prev_start, end)
            break

        chunks.append((start, end))
        start = end

    if not chunks:
        return [(0.0, total)]

    last_start, last_end = chunks[-1]
    if (last_end - last_start) < min_seconds and len(chunks) > 1:
        prev_start, prev_end = chunks[-2]
        chunks[-2] = (prev_start, last_end)
        chunks.pop()

    return chunks


def cut_video_segment(source_path: str, start: float, end: float, output_path: str):
    ffmpeg = find_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        source_path,
        "-ss",
        str(start),
        "-to",
        str(end),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def add_subtitles_to_video(video_path: str, srt_path: str, output_path: str):
    ffmpeg = find_ffmpeg()
    filter_string = (
        f"subtitles='{srt_path}':force_style='FontName=DejaVuSans,Fontsize=20,"
        "PrimaryColour=&HFFFFFFFF,OutlineColour=&H80000000,BackColour=&H80000000,"
        "BorderStyle=3,Outline=1,Shadow=0,MarginV=24'"
    )
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        video_path,
        "-vf",
        filter_string,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def process_video_for_clips(source_video: str, output_dir: str, target_seconds: int = DEFAULT_TARGET, min_seconds: int = DEFAULT_MIN):
    os.makedirs(output_dir, exist_ok=True)
    segments = create_clip_segments(source_video, target_seconds=target_seconds, min_seconds=min_seconds)
    results = []

    for index, (start, end) in enumerate(segments, start=1):
        safe_name = f"clip_{index}.mp4"
        clip_path = os.path.join(output_dir, safe_name)
        cut_video_segment(source_video, start, end, clip_path)

        audio_path = os.path.join(output_dir, f"clip_{index}.wav")
        extract_audio_from_video(clip_path, audio_path)

        transcript = transcribe_audio(audio_path, model_size=DEFAULT_MODEL, language=DEFAULT_LANG)
        srt_path = os.path.join(output_dir, f"clip_{index}.srt")
        write_srt(transcript, srt_path)

        output_path = os.path.join(output_dir, f"clip_{index}_subtitle.mp4")
        add_subtitles_to_video(clip_path, srt_path, output_path)
        results.append(output_path)

    return results


def main():
    sample_video = "/storage/emulated/0/Download/input.mp4"
    output_dir = "/storage/emulated/0/Download/processed_clips"
    for item in process_video_for_clips(sample_video, output_dir):
        print(item)


if __name__ == "__main__":
    main()

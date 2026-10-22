import asyncio
import os
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from clipper import find_ffmpeg, process_video_for_clips


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Kirim video ke bot ini. Saya akan memotongnya jadi klip 30–60 detik, "
        "membuat subtitle otomatis Bahasa Indonesia, lalu mengirim kembali hasilnya ke chat ini."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Cara pakai:\n"
        "1. Kirim video ke bot.\n"
        "2. Bot akan memotong video menjadi klip 30–60 detik.\n"
        "3. Bot membuat subtitle Bahasa Indonesia secara otomatis.\n"
        "4. Bot mengirim klip hasil pemrosesan dan file subtitle .srt ulang ke chat Anda.\n\n"
        "Catatan: gunakan di Termux/Pydroid dengan ffmpeg terinstal dan token bot diset di variabel TELEGRAM_BOT_TOKEN."
    )


async def _download_video(update: Update, video) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="telegram_autoclipper_"))
    file = await video.get_file()
    source_path = temp_dir / "source_video.mp4"
    await file.download_to_drive(custom_path=str(source_path))
    return temp_dir


def _check_runtime_dependencies() -> None:
    try:
        import faster_whisper  # noqa: F401
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Dependency 'faster-whisper' belum terinstal. Jalankan: pip install faster-whisper"
        ) from exc

    try:
        find_ffmpeg()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "ffmpeg belum tersedia. Instal ffmpeg di Termux/Pydroid sebelum menjalankan bot."
        ) from exc


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.video:
        return

    video = update.message.video
    await update.message.reply_text("Video diterima. Saya sedang memotong, menyalin subtitle, dan mengirim hasilnya...")

    try:
        _check_runtime_dependencies()
        temp_dir = await _download_video(update, video)
        source_path = temp_dir / "source_video.mp4"

        if not source_path.exists():
            raise FileNotFoundError("File video yang diunduh tidak ditemukan di penyimpanan sementara.")

        outputs = process_video_for_clips(
            str(source_path),
            str(temp_dir / "processed"),
            target_seconds=45,
            min_seconds=30,
        )

        if not outputs:
            await update.message.reply_text("Tidak ada klip yang bisa dibuat dari video ini.")
            return

        for output_path in outputs:
            subtitle_path = output_path.replace("_subtitle.mp4", ".srt")
            if os.path.exists(output_path):
                with open(output_path, "rb") as clip_file:
                    await update.message.reply_video(
                        video=clip_file,
                        supports_streaming=True,
                        caption="Klip hasil Auto Clipper (subtitle otomatis Bahasa Indonesia)",
                    )
            if os.path.exists(subtitle_path):
                with open(subtitle_path, "rb") as srt_file:
                    await update.message.reply_document(
                        document=srt_file,
                        filename=os.path.basename(subtitle_path),
                        caption="Subtitle Bahasa Indonesia (.srt)",
                    )

        await update.message.reply_text(f"Selesai. Saya mengirim {len(outputs)} klip hasil pemrosesan.")

    except FileNotFoundError as exc:
        await update.message.reply_text(f"Kesalahan perangkat: {exc}")
    except ModuleNotFoundError as exc:
        await update.message.reply_text(f"Dependency tidak tersedia: {exc}")
    except Exception as exc:
        await update.message.reply_text(f"Pemrosesan video gagal: {exc}")



def main() -> None:
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN belum di-set. "
            "Atur token melalui environment variable terlebih dahulu."
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    app.run_polling()


if __name__ == "__main__":
    main()

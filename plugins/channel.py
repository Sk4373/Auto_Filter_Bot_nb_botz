import re
import requests
from info import *
from utils import *
from pyrogram import Client, filters
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CAPTION_LANGUAGES = ["Bhojpuri", "Hindi", "Bengali", "Tamil", "English", "Bangla", "Telugu", "Malayalam", "Kannada", "Marathi", "Punjabi", "Bengoli", "Gujrati", "Korean", "Gujarati", "Spanish", "French", "German", "Chinese", "Arabic", "Portuguese", "Russian", "Japanese", "Odia", "Assamese", "Urdu"]

notified_movies = set()

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    print(f"Processing message from chat: {message.chat.id}, file_type: {message.media}")
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            print(f"Found media: {file_type}, file_name: {media.file_name}, file_id: {media.file_id}")
            break
    else:
        print("No valid media found in message")
        return
    media.file_type = file_type
    media.caption = message.caption or "No caption"
    print(f"Calling save_file with file_name: {media.file_name}, caption: {media.caption}")
    success, silentxbotz = await save_file(bot, media)
    print(f"save_file result: success={success}, silentxbotz={silentxbotz}")
    try:  
        status = await get_status(bot.me.id)
        print(f"get_status result: {status}")
        if success and silentxbotz == 1 and status:
            print("Conditions met, calling send_movie_update")
            await send_movie_update(bot, file_name=media.file_name, caption=media.caption)
        else:
            print(f"Conditions not met: success={success}, silentxbotz={silentxbotz}, status={status}")
    except Exception as e:
        print(f"Error In Movie Update - {e}")
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')

async def movie_name_format(file_name):
    clean_filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
    return clean_filename

async def check_qualities(text, qualities: list):
    quality = [q for q in qualities if q.lower() in text.lower()]
    return ", ".join(quality) if quality else None

async def send_movie_update(bot, file_name, caption):
    try:
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None

        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption) or re.search(pattern, file_name)

        if year:
            file_name = file_name[:file_name.find(year) + 4]
        elif season:
            season = season.group(1)
            file_name = file_name[:file_name.find(season) + 1]

        qualities = [
            "ORG", "org", "HDcam", "HDCAM", "HQ", "hq", "HDRip", "hdrip", "Camrip", "CAMRip", "hdtc", "HDTC",
            "predvd", "PreDVD", "DVDscr", "dvdscr", "DVDScreen", "dvdscreen", "HDTS", "hdts", "WEB-DL", "web-dl",
            "WEBRip", "webrip", "BluRay", "bluray", "BRRip", "brrip", "DVDRip", "dvdrip", "TS", "ts", "R5", "r5",
            "SCR", "scr", "Screener", "screener", "TC", "tc", "Telecine", "telecine", "PPV", "ppv", "TVRip", "tvrip",
            "VHSRip", "vhsrip", "PDTV", "pdtv", "DVDR", "dvdr", "BDRip", "bdrip", "BDRemux", "bdremux", "Remux", "remux",
            "WEB", "web", "WEB-DLRip", "web-dlrip", "WEB-HDRip", "web-hdrip", "HMAX", "hmax", "NF", "nf", "AMZN", "amzn",
            "DSNP", "dsnp", "iTunes", "itunes", "VODRip", "vodrip", "SCREENER", "screener", "Workprint", "workprint",
            "TCRip", "tcrip", "Festival", "festival", "Final", "final", "Unrated", "unrated", "Extended", "extended", 
            "Director's Cut", "director's cut", "HEVC", "hevc", "x265", "X265", "x264", "X264", "AVC", "avc", "h264", "H264",
            "h265", "H265", "VP9", "vp9", "AV1", "av1", "DivX", "divx", "XviD", "xvid", "MPEG2", "mpeg2", "MPEG4", "mpeg4",
            "AMZN", "amzn", "NF", "nf", "HMAX", "hmax", "DSNP", "dsnp", "HULU", "hulu", "iTunes", "itunes", "AppleTV", "appletv",
            "Scene", "scene", "P2P", "p2p", "Repack", "repack", "Proper", "proper", "REAL", "real", "Line", "line", "Internal", "internal"
        ]

        quality = await check_qualities(caption, qualities) or "HDRip"

        caption = caption.lower().replace("hin", "hindi").replace("eng", "english").replace("tam", "tamil") \
            .replace("tel", "telugu").replace("mal", "malayalam").replace("kan", "kannada") \
            .replace("pun", "punjabi").replace("ben", "bengali").replace("mar", "marathi") \
            .replace("guj", "gujrati").replace("kor", "korean").replace("jap", "japanese") \
            .replace("bho", "bhojpuri")

        language = ""
        nb_languages = [
            "Hindi", "Bengali", "English", "Marathi", "Tamil", "Telugu", "Malayalam",
            "Kannada", "Punjabi", "Gujrati", "Korean", "Japanese", "Bhojpuri", "Dual", "Multi"
        ]

        for lang in nb_languages:
            if lang.lower() in caption:
                language += f"{lang}, "
        language = language.strip(", ") or "Original Language"

        movie_name = await movie_name_format(file_name)
        if movie_name in notified_movies:
            return
        notified_movies.add(movie_name)

        imdb = await get_poster(movie_name)
        imdb_url = imdb.get("url") if imdb else "N/A"
        kind = imdb.get("kind", "Unknown").strip().upper().replace(" ", "") if imdb else "UPDATED"
        genres = imdb.get("genres", "Unknown").strip() if imdb else "UNKNOWN"

        caption_message = (
            f"<b>✅ {movie_name} #{kind}</b>\n\n"
            f"<blockquote>🎙️{language}</blockquote>\n\n"
            f"<b>🌟[IMDB Info]({imdb_url})</b>\n"
            f"<b>📽️Genre : {genres}</b>"
        )

        search_movie = movie_name.replace(" ", '-')

        btn = [
            [InlineKeyboardButton('𝖦𝖾𝗍 𝖥𝗂𝗅𝖾 🔎', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')]
        ]

        reply_markup = InlineKeyboardMarkup(btn)

        await bot.send_message(
            MOVIE_UPDATE_CHANNEL,
            text=caption_message, reply_markup=reply_markup, disable_web_page_preview=True
        )

    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')

async def get_imdb_details(name):
    try:
        formatted_name = await movie_name_format(name)
        imdb = await get_poster(formatted_name)
        if not imdb:
            return {}
        return {
            "title": imdb.get("title", formatted_name),
            "kind": imdb.get("kind", "Movie"),
            "year": imdb.get("year"),
            "url": imdb.get("url"),
            "genres": imdb.get("genres")
        }
    except Exception as e:
        print(f"IMDB fetch error: {e}")
        return {}

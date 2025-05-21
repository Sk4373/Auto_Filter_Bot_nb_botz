from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
import re

warnings = {}
BANNED = "banned"

def is_link_or_username(t):
    return bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|@[A-Za-z0-9_]+', t))

async def is_privileged(c, cid, uid):
    if uid in ADMINS:
        return True
    m = await c.get_chat_member(cid, uid)
    return m.status in ["creator", "administrator"]

async def ban(c, cid, uid):
    await c.ban_chat_member(cid, uid)
    warnings[(cid, uid)] = BANNED

async def unban(c, cid, uid):
    await c.unban_chat_member(cid, uid)
    warnings.pop((cid, uid), None)

@Client.on_message(filters.group & filters.text)
async def handle_msg(c, m):
    cid, uid, t = m.chat.id, m.from_user.id, m.text
    if await is_privileged(c, cid, uid):
        return
    if is_link_or_username(t):
        k = (cid, uid)
        if warnings.get(k) == BANNED:
            return
        warnings[k] = warnings.get(k, 0) + 1
        if warnings[k] == 3:
            await ban(c, cid, uid)
            await m.reply(
                f"Hᴇʏ,{m.from_user.mention}, Wᴀʀɴɪɴɢ⚠️ {warnings[k]}/3: Nᴏ Lɪɴᴋs Oʀ Usᴇʀɴᴀᴍᴇs Aʟʟᴏᴡᴇᴅ Iɴ Tʜɪs Cʜᴀᴛ , Iғ Yᴏᴜ Dᴏ Yᴏᴜ Wɪʟʟ Bᴇ Bᴀɴɴᴇᴅ",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚠️ Uɴʙᴀɴ / Rᴇᴍᴏᴠᴇ Rᴇsᴛʀɪᴄᴛɪᴏɴ ⚠️", callback_data=f"unban_{uid}")]
                ])
            )
        else:
            await m.reply(f"{m.from_user.mention}, warning {warnings[k]}/3: No links/usernames allowed.")
        await m.delete()

@Client.on_callback_query(filters.regex(r"unban_(\d+)"))
async def handle_unban(c, q):
    cid, uid = q.message.chat.id, int(q.data.split("_")[1])
    if await is_privileged(c, cid, q.from_user.id):
        await unban(c, cid, uid)
        await q.message.edit_text(f"User {uid} unbanned.")
    else:
        await q.answer("Only admins can unban users.", show_alert=True)

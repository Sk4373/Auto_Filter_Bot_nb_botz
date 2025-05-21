from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from info import LOG_CHANNEL  # Importing log channel from Info.py

# List of channels to check
HUB_CNL = [
    -1001847223482,
    -1001876070418,
    -1001856977789,
    -1001822008702,
    -1001500716579,
    -1002600403677
]

MOVIE_GROUP_LINK = "https://t.me/Request_Corner"  # Replace with your Movie Group link

@Client.on_message(filters.command("links"))
async def check_channels_and_send_links(bot, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Send a processing message
    processing_msg = await bot.send_message(chat_id, "🏴‍☠️ 𝖠𝗅𝗅 𝖫𝗂𝗇𝗄𝗌 𝖢𝗋𝖾𝖺𝗍𝖾𝖽, 𝖶𝖺𝗂𝗍 𝖥𝗈𝗋 𝖲𝖾𝗋𝗏𝖾𝗋 𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾... 🏴‍☠️")

    not_joined_channels = []
    invite_links = {}

    for channel in HUB_CNL:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in [
                enums.ChatMemberStatus.MEMBER,
                enums.ChatMemberStatus.ADMINISTRATOR,
                enums.ChatMemberStatus.OWNER
            ]:
                not_joined_channels.append(channel)

        except Exception as e:
            if "USER_NOT_PARTICIPANT" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                not_joined_channels.append(channel)  # Assume user is not a member
            else:
                print(f"❌ Error checking membership in channel {channel}: {e}")  # Only print in terminal

    if not not_joined_channels:
        text = (
            "<b>🎉 𝖢𝗈𝗇𝗀𝗋𝖺𝗍𝗎𝗅𝖺𝗍𝗂𝗈𝗇𝗌 🎉\n\n"
            "𝖸𝗈𝗎 𝖠𝗋𝖾 𝖠𝗅𝗋𝖾𝖺𝖽𝗒 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖠𝗅𝗅 𝖮𝗎𝗋 𝖧𝗎𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌.</b>"
        )
        buttons = [[InlineKeyboardButton("📂 Movie Group 📂", url=MOVIE_GROUP_LINK)]]
    else:
        text = (
            "<b>🔗 𝖤𝗑𝗉𝗅𝗈𝗋𝖾 𝖺𝗅𝗅 𝗈𝗎𝗋 𝖫𝗂𝗇𝗄𝗌 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌 𝖻𝖾𝗅𝗈𝗐!\n\n"
            "𝖮𝗇𝖼𝖾 𝗒𝗈𝗎𝗋 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗌 𝗌𝗎𝖻𝗆𝗂𝗍𝗍𝖾𝖽, 𝗒𝗈𝗎'𝗅𝗅 𝖻𝖾 𝗂𝗇𝗌𝗍𝖺𝗇𝗍𝗅𝗒 𝖺𝖽𝖽𝖾𝖽 𝗍𝗈 𝗈𝗎𝗋 Channels!\n\n"
            "⚠️ 𝖭𝗈𝗍𝖾: 𝖳𝗁𝗂𝗌 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖵𝖺𝗅𝗂𝖽𝗂𝗍𝗒 𝖨𝗌 1 𝖬𝗂𝗇𝗎𝗍𝖾. 𝖨𝖿 𝗒𝗈𝗎𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗀𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾𝖽, 𝖼𝗅𝗂𝖼𝗄 /links 𝗍𝗈 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖺 𝗇𝖾𝗐 𝗈𝗇𝖾.\n\n"
            "🔥 𝖲𝗍𝖺𝗒 𝗎𝗉𝖽𝖺𝗍𝖾𝖽! 𝖩𝗈𝗂𝗇 @Movies_Corner20 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾.</b>"
        )

        buttons = []

        for channel in not_joined_channels:
            try:
                invite_link = await bot.create_chat_invite_link(channel, creates_join_request=True)
                invite_links[channel] = invite_link.invite_link
                chat = await bot.get_chat(channel)
                buttons.append([InlineKeyboardButton(f"📌 {chat.title} #EXCLUSIVE", url=invite_link.invite_link)])
            except Exception as e:
                print(f"❌ Error generating invite link for {channel}: {e}")  # Only print in terminal

    reply_markup = InlineKeyboardMarkup(buttons)

    # Delete the processing message and send the actual response
    await processing_msg.delete()
    sent_message = await bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=True)

    await asyncio.sleep(60)

    for channel, link in invite_links.items():
        try:
            await bot.revoke_chat_invite_link(channel, link)
        except Exception as e:
            print(f"❌ Error revoking invite link for {channel}: {e}")  # Only print in terminal

    await sent_message.delete()

# Monitor new members joining via invite links
@Client.on_chat_member_updated()
async def monitor_new_members(bot, member_update):
    if member_update.new_chat_member:
        user = member_update.new_chat_member.user
        chat_id = member_update.chat.id
        if chat_id in HUB_CNL:
            log_text = (
                f"✅ **New Member Joined via Invite Link**\n\n"
                f"🔹 **User:** {user.mention} (`{user.id}`)\n"
                f"🔹 **Channel:** {member_update.chat.title} (`{chat_id}`)"
            )
            await bot.send_message(LOG_CHANNEL, log_text)

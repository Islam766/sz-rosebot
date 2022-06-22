from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Rose.mongo.connectiondb import add_connection, all_connections, if_active, delete_connection
import logging
from Rose import *
from lang import get_command
from Rose.utils.commands import *
from Rose.utils.lang import *
from button import *


CONNECT = get_command("CONNECT")
DISCONNECT = get_command("DISCONNECT")
CONNECTIONS = get_command("CONNECTIONS")

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)



@app.on_message((filters.private | filters.group) & command(CONNECT))
@language
async def addconnection(client, message: Message, _):
    userid = message.from_user.id if message.from_user else None
    chat_id = message.chat.id
    if not userid:
        return await message.reply(_["connection1"].format(chat_id))
    chat_type = message.chat.type
    if chat_type == "private":
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(_["connection2"])
            return

    elif chat_type in ["group", "supergroup"]:
        group_id = message.chat.id

    try:
        st = await app.get_chat_member(group_id, userid)
        if (
                st.status != "administrator"
                and st.status != "creator"
        ):
            await message.reply_text(_["connection3"])
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(_["connection4"])

        return
    try:
        connection = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Connect me pm",
                url=f"t.me/{BOT_USERNAME}?start=connections",
            )
        ]
    ]
)
        st = await app.get_chat_member(group_id, "me")
        if st.status == "administrator":
            ttl = await app.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(_["connection5"].format(title),
                    reply_markup= connection,
                    quote=True,
                    parse_mode="md"
                )
                if chat_type in ["group", "supergroup"]:
                    await app.send_message(
                        userid,
                        f"Connected to **{title}** !",
                        parse_mode="md"
                    )
            else:
                await message.reply_text(_["connection6"])
        else:
            await message.reply_text(_["connection7"])
    except Exception as e:
        logger.exception(e)
        await message.reply_text(_["connection8"])
        return


@app.on_message((filters.private | filters.group) & filters.command(DISCONNECT))
@language
async def deleteconnection(client, message: Message, _):
    userid = message.from_user.id if message.from_user else None
    chat_id = message.chat.id
    if not userid:
        return await message.reply(_["connection9"].format(chat_id))
    chat_type = message.chat.type

    if chat_type == "private":
        await message.reply_text(_["connection10"])

    elif chat_type in ["group", "supergroup"]:
        group_id = message.chat.id

        st = await app.get_chat_member(group_id, userid)
        if (
                st.status != "administrator"
                and st.status != "creator"
        ):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text(_["connection11"])
        else:
            await message.reply_text(_["connection12"])


@app.on_message(filters.private & filters.command(CONNECTIONS))
@language
async def connections(client, message: Message, _):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(_["connection13"])
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await app.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            act = ":✅" if active else ":⛔️"
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
"""
**Current connected chats:**

Connected = ✅
Disconnect = ⛔️

__Select a chat to connect:__
""",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(_["connection13"])


__MODULE__ = f"{Connections}"
__HELP__ = """

Иногда вы просто хотите добавить некоторые заметки и фильтры в общий чат, но не хотите, чтобы их видели все.

Это позволяет вам подключаться к базе данных чата и добавлять в него нужные вещи так, чтобы чат об этом не знал! По очевидным причинам, для добавления вещей вам нужно быть администратором, но любой пользователь может просматривать ваши данные. ( забаненные/кикнутые пользователи не могут!)

**Команды администратора:**
- /connect <chatid/username>: Подключиться к указанному чату, позволяя вам просматривать/редактировать его содержимое.
- /disconnect: Отключиться от текущего чата.
- /connections: Посмотреть информацию о текущем подключенном чате.

Вы можете получить id чата, используя команду /id в вашем чате. Не удивляйтесь, если id будет отрицательным; все супергруппы имеют отрицательные id.
"""

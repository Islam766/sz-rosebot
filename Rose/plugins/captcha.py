import asyncio
from  Rose import app
from Rose.mongo.captcha import captchas
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from pyrogram import filters
from . antlangs import *
from Rose.Inline.query import *
from lang import get_command
from Rose.utils.commands import *
from Rose.utils.lang import *
from Rose.utils.custom_filters import restrict_filter
from button import *

CAPTCH = get_command("CAPTCH")
REMOVEC = get_command("REMOVEC")
db = {}

@app.on_message(command(CAPTCH) & ~filters.private & restrict_filter)
@language
async def add_chat(client, message: Message, _):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user = await bot.get_chat_member(chat_id, user_id)
    if user.status == "creator" or user.status == "administrator":

      chat = captchas().chat_in_db(chat_id)
      if chat:
            await message.reply_text(_["capt1"])
      else:
           await message.reply_text(text=_["capt2"],
                                    reply_markup=InlineKeyboardMarkup(
                                        [
                                            [
                                                InlineKeyboardButton(text="Captcha On ✅", callback_data=f"new_{chat_id}_{user_id}_E"),
                                                InlineKeyboardButton(text="Captcha Off ❌", callback_data=f"off_{chat_id}_{user_id}")
                                            ],
                                            [
                                                InlineKeyboardButton(text="Close Menu ✖️", callback_data=f"close_data")
                                            ],
                                    ]))
    
      
      args = get_arg(message)
      lower_args = args.lower()
      if lower_args == "on":     
        await message.reply_text(text=_["capt2"],
                                    reply_markup=InlineKeyboardMarkup(
                                        [
                                            [
                                                InlineKeyboardButton(text="Captcha On ✅", callback_data=f"new_{chat_id}_{user_id}_E"),
                                                InlineKeyboardButton(text="Captcha Off ❌", callback_data=f"off_{chat_id}_{user_id}")
                                            ],
                                            [
                                                InlineKeyboardButton(text="Close Menu ✖️", callback_data=f"close_data")
                                            ],
                                    ]))  
      if lower_args == "off":     
           await message.reply_text(text=_["capt2"],
                                    reply_markup=InlineKeyboardMarkup(
                                        [
                                            [
                                                InlineKeyboardButton(text="Captcha On ✅", callback_data=f"new_{chat_id}_{user_id}_E"),
                                                InlineKeyboardButton(text="Captcha Off ❌", callback_data=f"off_{chat_id}_{user_id}")
                                            ],
                                            [
                                                InlineKeyboardButton(text="Close Menu ✖️", callback_data=f"close_data")
                                            ],
                                    ]))                                                      
      

async def send_captcha(app,message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    chat = captchas().chat_in_db(chat_id)
    if not chat:
        return
    try:
        user_s = await app.get_chat_member(chat_id, user_id)
        if (user_s.is_member is False) and (db.get(user_id, None) is not None):
            try:
                await app.delete_messages(
                    chat_id=chat_id,
                    message_ids=db[user_id]["msg_id"]
                )
            except:
                pass
            return
        elif (user_s.is_member is False):
            return
    except UserNotParticipant:
        return
    chat_member = await app.get_chat_member(chat_id, user_id)
    if chat_member.restricted_by:
        if chat_member.restricted_by.id == (await app.get_me()).id:
            pass
        else:
            return
    try:
        if db.get(user_id, None) is not None:
            try:
                await app.send_message(
                    chat_id=chat_id,
                    text=f"❗️ {message.from_user.mention} again joined group without verifying!\n\n"
                         f"He can try again after 5 minutes.",
                    disable_web_page_preview=True
                )
                await app.delete_messages(chat_id=chat_id,
                                             message_ids=db[user_id]["msg_id"])
            except:
                pass
            await asyncio.sleep(300)
            del db[user_id]
    except:
        pass
    try:
        await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
    except:
        return
    await app.send_message(chat_id,
                              text=f"🙋‍♀️ Hi {message.from_user.mention}, welcome to {message.chat.title} group chat!\n\n To continue, first verify that you're not a robot. ",
                              reply_markup=InlineKeyboardMarkup(
                                  [
                                      [
                                          InlineKeyboardButton(text="🤖 Verify Now ", callback_data=f"verify_{chat_id}_{user_id}"),
                                          InlineKeyboardButton(text="Pass ❗️", callback_data=f"_unmute_{user_id}")
                                          
                                      ]
                                      ]
                                ))
    return 400

def MakeCaptchaMarkup(markup, _number, sign):
    __markup = markup
    for i in markup:
        for k in i:
            if k["text"] == _number:
                k["text"] = f"{sign}"
                k["callback_data"] = "done_"
                return __markup

@app.on_message(command(REMOVEC) & ~filters.private)
@language
async def del_chat(client, message: Message, _):
    chat_id = message.chat.id
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator" :
        j = captchas().delete_chat(chat_id)
        if j:
            await message.reply_text(_["capt3"])

__MODULE__ = f"{Extra}"
__HELP__ = f"""
**Команды:**
 - /id: Получить идентификатор пользователя или чата.
 - /info: Получить основную информацию о пользователе.
 - /paste: Вставить заданный текст на веб-сайт.
 - /tr [lang code]: Переводить текстовые сообщения.
 - /telegraph <ответ в jpg, jpeg, png, gif или mp4>: загрузить в телеграф.
 - /tm <ответ на jpg, jpeg, png, gif или mp4>: загрузить в телеграф.
 - /tgm <ответ на jpg, jpeg, png, gif или mp4>: загрузить в телеграф.
 - /invitelink: Получить invitelink для вашей группы.
 
**Пример:*.
 - Перевести текстовое сообщение на английский язык:
> `/tr en` [Ответить на некоторое текстовое сообщение].
"""

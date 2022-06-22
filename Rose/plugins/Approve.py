from pyrogram.errors import PeerIdInvalid, UserNotParticipant
from pyrogram.types import  Message
from Rose import  app 
from Rose.mongo.approvedb import Approve
from Rose.utils.custom_filters import admin_filter, command, owner_filter
from Rose.utils.extract_user import extract_user
from Rose.utils.kbhelpers import rkb as ikb
from lang import get_command
from Rose.utils.lang import *
from button import *

APPROVE = get_command("APPROVE")
DISAPPROVE = get_command("DISAPPROVE")
APROVED = get_command("APROVED")
APPROVAL = get_command("APPROVAL")
UNAPPROVE = get_command("UNAPPROVE")


@app.on_message(command(APPROVE)  & admin_filter )
@language
async def approve_user(client, message: Message, _):
    db = Approve(message.chat.id)
    chat_title = message.chat.title
    try:
        user_id, user_first_name, _ = await extract_user(app, message)
    except Exception:
        return
    if not user_id:
        await message.reply_text(_["app4"])
        return
    try:
        member = await message.chat.get_member(user_id)
    except UserNotParticipant:
        await message.reply_text(_["app2"])
        return
    except Exception as ef:
        await message.reply_text(
            f"{ef}",
        )
        return
    if member.status in ("administrator", "creator"):
        await message.reply_text(_["app3"])
        return
    already_approved = db.check_approve(user_id)
    if already_approved:
        await message.reply_text(_["app5"].format(message.from_user.first_name,chat_title),)  
        return
    db.add_approve(user_id, user_first_name)
    try:
        await message.chat.unban_member(user_id=user_id)
    except Exception as ef:
        await message.reply_text(f"Error: {ef}")
        return
    return await message.reply_text(_["app6"].format(message.from_user.first_name,chat_title),)



@app.on_message(command(DISAPPROVE)  & admin_filter)
@language
async def disapprove_user(client, message: Message, _):
    db = Approve(message.chat.id)
    chat_title = message.chat.title
    try:
        user_id, user_first_name, _ = await extract_user(app, message)
    except Exception:
        return
    already_approved = db.check_approve(user_id)
    if not user_id:
        await message.reply_text(_["app1"])
        return
    try:
        member = await message.chat.get_member(user_id)
    except UserNotParticipant:
        if already_approved: 
            db.remove_approve(user_id)   
        await message.reply_text(_["app2"])
        return
    except Exception as ef:
        await message.reply_text(
            f"{ef}",
        )
        return
    if member.status in ("administrator", "creator"):
        await message.reply_text(_["app7"])
        return
    if not already_approved:
        await message.reply_text(_["app8"].format(message.from_user.first_name),)
        return
    db.remove_approve(user_id)
    return await message.reply_text(_["app9"].format(message.from_user.first_name,chat_title),)



@app.on_message(command(APROVED) )
@language
async def check_approved(client, message: Message, _):
    db = Approve(message.chat.id)
    chat = message.chat
    chat_title = chat.title
    msg = "The following users are approved:\n"
    approved_people = db.list_approved()
    if not approved_people:
        await message.reply_text(_["app10"].format(chat_title),)
        return
    for user_id, user_name in approved_people.items():
        try:
            await chat.get_member(user_id) 
        except UserNotParticipant:
            db.remove_approve(user_id)
            continue
        except PeerIdInvalid:
            pass
        msg += f"- `{user_id}`: {user_name}\n"
    await message.reply_text(msg)
    return



@app.on_message(command(APPROVAL))
@language
async def check_approval(client, message: Message, _):
    db = Approve(message.chat.id)
    try:
        user_id, user_first_name, _ = await extract_user(app, message)
    except Exception:
        return
    check_approve = db.check_approve(user_id)
    if not user_id:
        await message.reply_text(_["app1"])
        return
    if check_approve:
        await message.reply_text(_["app11"].format(message.from_user.first_name, user_id),)
    else:
        await message.reply_text(_["app12"].format(message.from_user.first_name, user_id),)
    return


@app.on_message(
    command(UNAPPROVE)  & owner_filter,
)
async def unapproveall_users(_, m: Message):
    db = Approve(m.chat.id)
    user_id = m.from_user.id
    all_approved = db.list_approved()
    if not all_approved:
        await m.reply_text("No one is approved in this chat.")
        return
    await m.reply_text(
        "Are you sure you want to remove everyone who is approved in this chat?",
        reply_markup=ikb(
            [[("⚠️ Confirm", f"unapprovecb:{user_id}"), ("❌ Cancel", "close_admin")]],
        ),
    )
    return


__MODULE__ = f"{Approval}"
__HELP__ = """
Иногда вы можете доверять пользователю, что он не будет отправлять нежелательный контент.
Возможно, не настолько, чтобы сделать его администратором, но вы можете быть согласны с тем, чтобы блокировки, блок-листы и антифлуд не применялись к нему.
Вот для чего нужны одобрения - одобрить надежных пользователей, чтобы позволить им отправлять. 

**Команды администратора:**
- /approval: Проверить статус разрешения пользователя в этом чате.

**Команды администратора:**
- /approve: Одобрить пользователя. Блокировки, блок-листы и антифлуд больше не будут применяться к нему.
- /unapprove: Отменить одобрение пользователя. Теперь на него снова будут распространяться блокировки, блок-листы и антифлуд.
- /approved: Вывести список всех одобренных пользователей.
"""

from telegram import InlineKeyboardMarkup
from telegram.message import Message
from telegram.update import Update
import time
import psutil, shutil
import signal
from bot import AUTO_DELETE_MESSAGE_DURATION, LOGGER, bot, \
    status_reply_dict, status_reply_dict_lock, dispatcher, updater, botStartTime
from bot.helper.ext_utils.bot_utils import get_readable_message, get_readable_time, get_readable_file_size
from telegram.error import TimedOut, BadRequest
from bot import bot


def sendMessage(text: str, bot, update: Update):
    try:
        return bot.send_message(update.message.chat_id,
                            reply_to_message_id=update.message.message_id,
                            text=text, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))


def sendMarkup(text: str, bot, update: Update, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.send_message(update.message.chat_id,
                             reply_to_message_id=update.message.message_id,
                             text=text, reply_markup=reply_markup, parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))


def editMessage(text: str, message: Message, reply_markup=None):
    try:
        bot.edit_message_text(text=text, message_id=message.message_id,
                              chat_id=message.chat.id,reply_markup=reply_markup,
                              parse_mode='HTMl')
    except Exception as e:
        LOGGER.error(str(e))


def deleteMessage(bot, message: Message):
    try:
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
    except Exception as e:
        LOGGER.error(str(e))


def sendLogFile(bot, update: Update):
    with open('log.txt', 'rb') as f:
        bot.send_document(document=f, filename=f.name,
                          reply_to_message_id=update.message.message_id,
                          chat_id=update.message.chat_id)


def auto_delete_message(bot, cmd_message: Message, bot_message: Message):
    if AUTO_DELETE_MESSAGE_DURATION != -1:
        time.sleep(AUTO_DELETE_MESSAGE_DURATION)
        try:
            # Skip if None is passed meaning we don't want to delete bot xor cmd message
            deleteMessage(bot, cmd_message)
            deleteMessage(bot, bot_message)
        except AttributeError:
            pass


def delete_all_messages():
    with status_reply_dict_lock:
        for message in list(status_reply_dict.values()):
            try:
                deleteMessage(bot, message)
                del status_reply_dict[message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))


def update_all_messages():
    currentTime = get_readable_time((time.time() - botStartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    msg = get_readable_message()
    msg += f"𝗖𝗣𝗨 📟: {psutil.cpu_percent()}%" \
           f" 𝗗𝗜𝗦𝗞💿: {psutil.disk_usage('/').percent}%" \
           f" 𝗥𝗔𝗠 💾: {psutil.virtual_memory().percent}%" \
           f"\n𝗕𝗼𝘁 𝗨𝗽𝘁𝗶𝗺𝗲 : {currentTime} | 𝗙𝗿𝗲𝗲🤯: {free}"
    with status_reply_dict_lock:
        for chat_id in list(status_reply_dict.keys()):
            if status_reply_dict[chat_id] and msg != status_reply_dict[chat_id].text:
                if len(msg) == 0:
                    msg = "Starting DL"
                try:
                    editMessage(msg, status_reply_dict[chat_id])
                except Exception as e:
                    LOGGER.error(str(e))
                status_reply_dict[chat_id].text = msg

def sendStatusMessage(msg, bot):
    currentTime = get_readable_time((time.time() - botStartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    progress = get_readable_message()
    progress += f"𝗖𝗣𝗨 📟: {psutil.cpu_percent()}%" \
           f" 𝗗𝗜𝗦𝗞💿: {psutil.disk_usage('/').percent}%" \
           f" 𝗥𝗔𝗠 💾: {psutil.virtual_memory().percent}%" \
           f"\n𝗕𝗼𝘁 𝗨𝗽𝘁𝗶𝗺𝗲 : {currentTime} | 𝗙𝗿𝗲𝗲 🤯: {free}"
    with status_reply_dict_lock:
        if msg.message.chat.id in list(status_reply_dict.keys()):
            try:
                message = status_reply_dict[msg.message.chat.id]
                deleteMessage(bot, message)
                del status_reply_dict[msg.message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))
                del status_reply_dict[msg.message.chat.id]
                pass
        if len(progress) == 0:
            progress = "Starting DL"
        message = sendMessage(progress, bot, msg)
        status_reply_dict[msg.message.chat.id] = message

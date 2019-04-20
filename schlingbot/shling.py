#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import json
import re
import requests
# from pymystem3 import Mystem
from datetime import datetime, timezone
import sqlite3
conn = sqlite3.connect('shling.db', check_same_thread=False)
import telegram
import random
# Create table
# c.execute('''CREATE TABLE IF NOT EXISTS stuff
             # (user_id integer, lvl int, yr int, group_num int, group_id int, firstname text, lastname text, datefirst datetime, datelast datetime)''')
# Save (commit) the changes
# conn.commit()             


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    user  = update.message.from_user
    uid = user.id
    c = conn.cursor()
    c.execute("select * from users where user_id = ?", (uid,))
    if c.fetchone() == None:
        # datetime.now(timezone.utc)
        c.execute("insert into users (user_id, firstname, lastname, language_code, username) values (?, ?, ?, ?, ?)", (uid, user.first_name, user.last_name, user.language_code, user.username))    
    update.message.reply_text('Привет! Напиши свою фамилию и имя (в таком порядке, регистр не важен).')


def help(bot, update):
    update.message.reply_text('Help!')

def read_timetable(data):
    if len(data) == 0:
        return("нет пар, отдыхай)")
    else:
        arr = []
        for para in data:
            arr.append(para["date"])
            arr.append(para["beginLesson"] + " - " + para["endLesson"])
            arr.append(para["discipline"])
            arr.append(para["auditorium"] + " - " + para["building"])
            arr.append(para["lecturer"])
            arr.append("■")
        return "\n".join(arr)
            
            




def echo(bot, update):
    txt = update.message.text
    msg  = 'ой всё...'
    # print(update.message)
    # print(getattr(update.message, 'from_user'))
    user  = update.message.from_user
    uid = user.id
    c = conn.cursor()    
    c.execute("select user_state, hse_id from users where user_id = ?", (uid,))
    user_info  = c.fetchone()
    
    # CREATE TABLE users (user_id integer, lvl int, yr int, group_num int, group_id int, firstname text, lastname text, language_code text, username text, datefirst datetime, datelast datetime);

    c.execute("insert into msgs (user_id, message_id, txt) values (?, ?, ?)", (uid, update.message.message_id, txt))
    conn.commit()
    
    if user_info:
        if user_info[0] == "new":
            if txt.isdigit():
                c.execute("select user_meta from users where user_id = ?", (uid,))
                user_meta  = c.fetchone()
                hseids = user_meta[0].split()
                user_hse_id  = hseids[int(txt)-1]
                update.message.reply_text("Вы выбрали " + txt + "\nТеперь можно ввести дату в виде номера дня и названия месяца и получить расписание :-)")
                c.execute("UPDATE users SET hse_id = ?, user_state = ? WHERE user_id =?", (user_hse_id, "hseid", uid))
                conn.commit()
            else:
                # names = txt.split()
                payload = {'term': txt, 'type': 'student'}
                r = requests.get('https://ruz.hse.ru/api/search', params=payload,  verify=False)
                people = []
                ids  = []
                if r.status_code == 200:
                    d = r.json()
                    for idx, val in enumerate(d):
                        fullname  = val["label"].replace(" -", "")
                        people.append(str(idx+1) + ". **" + fullname + "** •" + val["description"])
                        ids.append(str(val["id"]))
                    people.append("\nУкажите соответствующий Вам номер или введите данные более точно")
                    x  = "\n".join(people )
                    user_meta =  " ".join(ids)
                    c.execute("UPDATE users SET user_meta = ? WHERE user_id =?", (user_meta, uid))
                    conn.commit()
                    update.message.reply_text(x, parse_mode=telegram.ParseMode.MARKDOWN)
                    return
        elif user_info[0] == "hseid":
            # update.message.reply_text("Вы " + str(user_info[1]))
            day  = '23'
            match = re.search(r'\d+', txt) 
            if match:
                day = match.group(0)
                if len(day) == 1:
                        day = '0' + day
            mts  = [["янв", 1], ["фев", 2], ["мар", 3], ["апр", 4], ["май", 5], ["июн", 6], 
            ["июл", 7], ["авг", 8], ["сент", 9], ["окт", 10], ["ноя", 11], ["дек", 12]]
            mnum = '04'
            for m in mts:
                if m[0] in txt:
                    mnum  = str(m[1])
                    if len(mnum) == 1:
                        mnum = '0' + mnum
            date_st = '2019.'+ mnum + "." + day
            date_fn = '2019.'+ mnum + "." + day

            payload = {'start': date_st, 'finish': date_fn, 'lng': "1"}
            r = requests.get('https://ruz.hse.ru/api/schedule/student/'+str(user_info[1]), params=payload,  verify=False)
            if r.status_code == 200:
                d = r.json()
                # print(d)
                rs  = read_timetable(d)
                update.message.reply_text(rs)
            # return
    
    if txt in ['Привет', 'Hi', 'Здравствуйте']:
        msg  = 'Добрый день!'
    # elif txt == "меню":
        # update.message.reply_text(main_menu_message(), reply_markup=main_menu_keyboard())
    else:
        phrases = ["У тебя всё получится", "Ты молодец", "Ты няша", "^__^"]
        msg = random.choice(phrases) + ", " + user.first_name
    if txt != "меню":
        update.message.reply_text(msg)


def main_menu(bot, update):
  query = update.callback_query
  bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=main_menu_message(),
                        reply_markup=main_menu_keyboard())

def first_menu(bot, update):
  query = update.callback_query
  bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=first_menu_message(),
                        reply_markup=first_menu_keyboard())

def second_menu(bot, update):
  query = update.callback_query
  bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=second_menu_message(),
                        reply_markup=second_menu_keyboard())

# and so on for every callback_data option
def first_submenu(bot, update):
  pass

def second_submenu(bot, update):
  pass

############################ Keyboards #########################################
def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Бакалавриат', callback_data='m1')],
              [InlineKeyboardButton('Магистратура', callback_data='m2')],
              # [InlineKeyboardButton('Option 3', callback_data='m3')]
              ]
  return InlineKeyboardMarkup(keyboard)

def first_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Первый курс', callback_data='m1_1')],
              [InlineKeyboardButton('Второй курс', callback_data='m1_2')],
              [InlineKeyboardButton('Вернуться в предыдущее меню', callback_data='main')]]
  return InlineKeyboardMarkup(keyboard)

def second_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Первый год', callback_data='m2_1')],
              [InlineKeyboardButton('Второй год', callback_data='m2_2')],
              [InlineKeyboardButton('Вернуться в предыдущее меню', callback_data='main')]]
  return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def main_menu_message():
  return 'Choose the option in main menu:'

def first_menu_message():
  return 'Choose the submenu in first menu:'

def second_menu_message():
  return 'Choose the submenu in second menu:'

############################# Handlers #########################################

    
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(#token here#)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    updater.dispatcher.add_handler(CallbackQueryHandler(first_menu, pattern='m1'))
    updater.dispatcher.add_handler(CallbackQueryHandler(second_menu, pattern='m2'))
    updater.dispatcher.add_handler(CallbackQueryHandler(first_submenu,
                                                        pattern='m1_1'))
    updater.dispatcher.add_handler(CallbackQueryHandler(second_submenu,
                                                        pattern='m2_1'))
    
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

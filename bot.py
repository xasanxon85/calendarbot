#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://git.io/JOmFw.
"""
import logging
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_keyboard_days(date: datetime):
    month = str(date.strftime('%b')) + '  ' + str(date.year)

    keyboard = [
        [
            InlineKeyboardButton("<", callback_data='prev_month-' + str(date)),
            InlineKeyboardButton(month, callback_data='mode1-' + str(date)),
            InlineKeyboardButton(">", callback_data='next_month-' + str(date)),
        ],
    ]

    weekdays = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya']
    temp = []
    for weekday in weekdays:
        temp.append(InlineKeyboardButton(weekday, callback_data='?-' + str(date)))
    keyboard.append(temp)

    date_array = get_dates(date)
    for item in date_array:
        keyboard.append(item)

    return keyboard

def get_dates(date:datetime):
    days = []
    first_day = date.replace(day=1)
    last_day = datetime.date(date.year + int(date.month/12), date.month%12+1, 1)-datetime.timedelta(days=1)
    now = first_day.day
    end = last_day.day
    if first_day.weekday() != 0:
        temp = []
        for i in range(first_day.weekday()):
            temp.append(InlineKeyboardButton(' ', callback_data='?-' + str(date)))
        for i in range(7-first_day.weekday()):
            temp.append(InlineKeyboardButton(str(now), callback_data='?-' + str(date)))
            now += 1
        days.append(temp)
    while now + 7 <= end:
        temp = []
        for i in range(7):
            temp.append(InlineKeyboardButton(str(now), callback_data='?-' + str(date)))
            now += 1
        days.append(temp)
    temp = []
    if now < end:
        for i in range(now, end+1):
            temp.append(InlineKeyboardButton(str(now), callback_data='?-' + str(date)))
            now += 1
        for i in range(6 - last_day.weekday()):
            temp.append(InlineKeyboardButton(' ', callback_data='?-' + str(date)))
        days.append(temp)


    return days

def get_keyboard_month(date: datetime):

    keyboard = [
        [
            InlineKeyboardButton("<", callback_data='prev_year-' + str(date)),
            InlineKeyboardButton(date.year, callback_data='mode2-' + str(date)),
            InlineKeyboardButton(">", callback_data='next_year-' + str(date)),
        ],
    ]

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    temp = []
    for month in months:
        temp.append(InlineKeyboardButton(month, callback_data=month + '-' + str(date)))
        if len(temp) == 4:
            keyboard.append(temp)
            temp = []
    return keyboard

def get_keyboard_years(date:datetime):

    keyboard = [
        [
            InlineKeyboardButton("<", callback_data='mode2-' + str(datetime.date(date.year-12, 1, 1))),
            InlineKeyboardButton(str(date.year-6) + ' - ' + str(date.year + 5), callback_data='mode1-' + str(date)),
            InlineKeyboardButton(">", callback_data='mode2-' + str(datetime.date(date.year+12, 1, 1))),
        ],
    ]
    years = [i for i in range(date.year - 6, date.year + 6)]
    temp = []
    for year in years:
        temp.append(InlineKeyboardButton(str(year), callback_data='mode1-' + str(datetime.date(year, 1, 1))))
        if len(temp) == 4:
            keyboard.append(temp)
            temp = []

    return keyboard

def calendar(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard_days(datetime.datetime.now().date()))
    update.message.reply_text('Kalendar', reply_markup=reply_markup)


def start(update: Update, context: CallbackContext) -> None:

    # reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard(datetime.datetime.now().date()))
    keyboard = [[KeyboardButton('/calendar')]]
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)

    update.message.reply_text('Type /calendar or press special button to view Calendar', reply_markup=reply_markup)
    update.message.reply_text('Type /clear or press special button to clear chat', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    print(query.data)
    time = query.data.split('-')
    mode, year, month, day = time[0], int(time[1]), int(time[2]), int(time[3]),
    print(mode, year, month, day)

    if 'year' in mode:
        year += -1 if mode == 'prev_year' else 1
        date = datetime.date(year, 1, 1)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard_month(date))

    elif 'month' in mode:
        month += -1 if mode == 'prev_month' else 1
        if month > 12:
            month -= 12
            year += 1
        elif month < 1:
            month += 12
            year -= 1
        date = datetime.date(year, month, 1)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard_days(date))
    elif 'mode1' in mode:
        date = datetime.date(year, month, 1)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard_month(date))
    elif 'mode2' in mode:
        date = datetime.date(year, 1, 1)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard_years(date))
    else:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if mode in months:
            month = months.index(mode) + 1
        date = datetime.date(year, month, 1)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=get_keyboard_days(date))

    query.edit_message_text('MyCalendar', reply_markup=reply_markup)


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("2097076289:AAFbXy8c-bYAutQI6vJj70x-kxJZAW39Z60")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('calendar', calendar))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
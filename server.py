import json
from random import shuffle

import peewee
import telebot.types

from bot import bot
from models import User,Translate, Word, WordTranslate
import re


pattern = re.compile(r'/add[\s]([\w]+)[\s]([\w]+)')



@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello World")

@bot.message_handler(commands=['add'])
def add_word(message):
    user, __ = User.get_or_create(external_id=message.from_user.id, chat_id = message.chat.id)
    txt = message.text
    word_and_translate = pattern.match(txt)
    raw_word, raw_translate = tuple(i.lower() for i in word_and_translate.groups())
    word, __ = Word.get_or_create(word=raw_word, user = user)
    translate, __ = Translate.get_or_create(translate=raw_translate, user = user)
    WordTranslate.get_or_create(word=word, translate=translate, user=user)
    bot.reply_to(message, f'Добавлено слово "{raw_word}" с переводом"{raw_translate}"')

@bot.message_handler(commands=['test'])
def get_test(message, user=None):
    user = user or User.get(external_id=message.from_user.id, chat_id=message.chat.id)
    pairs = WordTranslate.select()\
        .where(WordTranslate.user == user)\
        .order_by(peewee.fn.Random())\
        .limit(4)
    markup = telebot.types.InlineKeyboardMarkup()
    buttons = []
    answer = None
    for row in pairs:
        word = Word.get(Word.id == row.word.id, Word.user == row.user)
        translate = Translate.get(Translate.id == row.translate.id, Translate.user == row.user)
        if answer is None:
            answer = word
        btn = telebot.types.InlineKeyboardButton(
            text = f'{row.translate.translate}',
            callback_data=json.dumps(
                {'t': 'a', 'q' : answer.id, 'a' : translate.id}
            )
        )
        buttons.append(btn)
    shuffle(buttons)
    markup.add(*buttons[:2])
    markup.add(*buttons[2:])
    bot.send_message(user.chat_id, f'Слово {answer.word}', reply_markup=markup)





if __name__ == '__main__':
    bot.infinity_polling()
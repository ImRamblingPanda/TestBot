import os
import re
import telebot as tb
from telebot import types
from dotenv import load_dotenv

# инициализация бота
load_dotenv()
client = tb.TeleBot(os.getenv("TEL_API_KEY"))

# инициализация разметки кнопочного меню и самих кнопок
menu = types.InlineKeyboardMarkup()
item1 = types.InlineKeyboardButton(text='Кнопка Один (Тык)', callback_data='1')
item2 = types.InlineKeyboardButton(text='Кнопка Два (Тык)', callback_data='2')
item3 = types.InlineKeyboardButton(text='Кнопка Три (Тык)', callback_data='3')
menu.add(item1, item2, item3, row_width=1)
back = types.ReplyKeyboardMarkup()
back_button = types.KeyboardButton(text='меню')
back.add(back_button)
# обработчик команд
@client.message_handler(commands=['start'])
# функция кнопочного меню
def startup(message):
    client.send_message(message.chat.id, "Привет, можешь написать \"меню\", чтоб получить его :)")
# обработчик сообщений
@client.message_handler(content_types=['text', 'sticker'])
# функция вызова меню
def menu_call(message):
    # проверка на тип сообщения
    if isinstance(message.text, str) and message.text.lower() == "меню":
        client.send_message(message.chat.id, 'Выбери нужную кнопку', reply_markup=menu)
# функционал 1 кнопки
# кнопка 1: должна на вход спрашивать у пользователя номер телефона, после указания номера бот сооьщает: «приятно познакомиться»
def phone_num(message):
    result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.text)
    if result:
        client.send_message(message.chat.id, f'Приятно познакомиться, {message.chat.first_name}', reply_markup=back)
    elif message.text.lower() == 'меню':
        menu_call(message)
    else:
        client.send_message(message.chat.id, 'По-моему ты где-то ошибся, попробуй ещё раз или выйди в меню',reply_markup=back)
        client.register_next_step_handler(message, phone_num)
# функционал 2 кнопки
# кнопка номер 2: бот задает вопрос: "мотоциклы" или "автомобили". На основе текстового ответа пользователя приходит последняя версия статьи с википедии об этом виде транспорта
def wikipedia(message):
    try:
        if re.match(r'мотоцикл', message.text.lower()):
            client.edit_message_text(message.chat.id, 'https://ru.wikipedia.org/wiki/Мотоцикл - вот твоя ссылка :), можешь выйти в меню', reply_markup=back)
        elif re.match(r'автомобиль', message.text.lower()):
            client.send_message(message.chat.id, 'https://ru.wikipedia.org/wiki/Автомобиль - вот твоя ссылка :), можешь выйти в меню', reply_markup=back)
        elif message.text.lower() == 'меню':
            menu_call(message)
        else:
            client.send_message(message.chat.id, 'Ты написал что-то непонятное, попробуй ещё раз или выйди в меню', reply_markup=back)
            client.register_next_step_handler(message, wikipedia)
    except:
        client.send_message(message.chat.id, 'Ты не ответил на мой вопрос, попробуй ещё раз :( или выйди в меню', reply_markup=back)
        client.register_next_step_handler(message, wikipedia)
# функционал 3 кнопки
# кнопка номер 3 после ее нажатия бот спрашивает "статус" у пользователя. После того как пользователь ответил на сообщение, бот отправляет сообщение пользователя в другой канал
def send_status(message):
    if isinstance(message.text, str):
        result = re.search((r'/|меню'), message.text)
        if not result:
            client.send_message('@tasty_testys',f'Статус {message.chat.first_name} - @{message.from_user.username} - {message.text}')
            check_member(message)
        elif message.text.lower() == 'меню':
            menu_call(message)
        else:
            client.send_message(message.chat.id, 'Ты ввел что-то не то, попробуй ещё раз или выйди в меню',reply_markup=back)
            client.register_next_step_handler(message, send_status)
    else:
        client.send_message(message.chat.id, 'Ты ввел что-то не то, попробуй ещё раз или выйди в меню',reply_markup=back)
        client.register_next_step_handler(message, send_status)
# функция проверки наличия пользователя в чате
def check_member(message):
    if client.get_chat_member(chat_id='@tasty_testys', user_id=message.from_user.id).status == 'left':
        client.send_message(message.chat.id,f'Я отправил твой статус, но тебя нет в чатике, лови ссылку - {client.create_chat_invite_link("@tasty_testys").invite_link}, можешь выйти в меню')
    else: client.send_message(message.chat.id, f'Я отправил твой статус, можешь его посмотреть здесь - @tasty_testys или можешь выйти в меню')
# обработчик вызовов с кнопок
@client.callback_query_handler(func=lambda call: True)
# функция обработки запроса и отправка ответа пользователю
def answer(call):
    client.answer_callback_query(callback_query_id=call.id, cache_time=1)
    match call.data:
        case '1':
            client.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Привет, давай познакомимся, напиши мне свой номер в формате +7(999)-99-99 или похожем, чтоб я его понял :)', reply_markup=None)
            client.register_next_step_handler(call.message, phone_num)
        case '2':
            client.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Привет, напиши мне, что нравится больше автомобиль или мотоцикл, а я тебе ссылку на викистатью :)', reply_markup=None)
            client.register_next_step_handler(call.message, wikipedia)
        case '3':
            client.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Привет, сообщи мне свой статус :)', reply_markup=None)
            client.register_next_step_handler(call.message, send_status)
# ожидание ответа от сервера telegram
client.polling(non_stop=True)

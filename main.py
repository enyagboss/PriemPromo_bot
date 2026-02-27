import telebot
from telebot import types
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = '8771260384:AAHk-br1rrpAH1eiiSdF7I9EFOGe5Ft7i_k'
AUTHORIZED_USER_ID = '909245407'  # Замените на ID авторизованного пользователя

bot = telebot.TeleBot(API_TOKEN)

# Статистика промокодов
promocode_stats = {
    "total": 0,
    "valid": 0,
    "invalid": 0,
    "daily": {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "date": datetime.now().date()
    }
}

# Словарь для отслеживания состояния пользователей
waiting_for_requisites = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == int(AUTHORIZED_USER_ID):
        bot.send_message(message.chat.id, "Добро пожаловать, авторизованный пользователь!")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Сдать промокод", callback_data='submit_promocode'))
        markup.add(types.InlineKeyboardButton("Прайс", callback_data='price'))
        markup.add(types.InlineKeyboardButton("Информация", callback_data='info'))

        bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=markup)
    
    logging.info(f"Команда /start от пользователя {message.from_user.first_name} (ID: {message.from_user.id})")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    if message.chat.id == int(AUTHORIZED_USER_ID):
        stats_message = (
            f"Статистика промокодов:\n"
            f"Всего промокодов: {promocode_stats['total']}\n"
            f"Валидные промокоды: {promocode_stats['valid']}\n"
            f"Не валидные промокоды: {promocode_stats['invalid']}\n"
            f"Промокоды за сегодня: {promocode_stats['daily']['total']}\n"
            f"Валидные за сегодня: {promocode_stats['daily']['valid']}\n"
            f"Не валидные за сегодня: {promocode_stats['daily']['invalid']}"
        )
        bot.send_message(message.chat.id, stats_message)
        logging.info(f"Пользователь {message.from_user.first_name} (ID: {message.from_user.id}) запросил статистику.")

@bot.message_handler(commands=['instruction'])
def show_photos(message):
    bot.send_message(message.chat.id, "Вот инструкция по получению промокода:")
    # Список URL фотографий
    photo_urls = [
        'https://image2url.com/r2/default/images/1772221065782-c154ddaf-48ba-4379-b338-99a71884f869.jpg',
        'https://image2url.com/r2/default/images/1772221096356-a0ba5cff-0e3b-4f86-9b78-64b2a1d022d8.jpg',
        'https://image2url.com/r2/default/images/1772221138101-2c8f8b06-b620-4b06-8226-c858520d8848.jpg',
        'https://image2url.com/r2/default/images/1772221171101-4539506c-d7ac-4eb6-8a52-5def046eac42.jpg',
        'https://image2url.com/r2/default/images/1772221187266-7abfa8fa-9a01-49f9-8159-49d664bb068d.jpg'
    ]
    
    for photo_url in photo_urls:
        bot.send_photo(message.chat.id, photo_url)

@bot.callback_query_handler(func=lambda call: call.data == 'submit_promocode')
def handle_submit_promocode(call):
    bot.send_message(call.message.chat.id, "Отправьте мне ваш промокод.")
    waiting_for_requisites[call.from_user.id] = False  # Установим состояние ожидания промокода
    logging.info(f"Пользователь {call.from_user.first_name} (ID: {call.from_user.id}) начал процесс сдачи промокода.")

@bot.callback_query_handler(func=lambda call: call.data == 'price')
def handle_price(call):
    bot.send_message(call.message.chat.id, "Промокод: скидка на первый заказ Самокат 500(есть почти у каждого)\n" \
    "Прайс: ")  # Замените текст на нужный
    logging.info(f"Пользователь {call.from_user.first_name} (ID: {call.from_user.id}) запросил прайс.")

@bot.callback_query_handler(func=lambda call: call.data == 'info')
def handle_info(call):
    bot.send_message(call.message.chat.id, "Все вопросы по сотрудничеству, реализации бота, оптовых продаж: @bzdrj\n" \
    "Выплаты производятся в течении 12-ти часов с момента проверки промокода!\n" \
    "По выплатам просьба не беспокоить!!!")  # Замените текст на нужный
    logging.info(f"Пользователь {call.from_user.first_name} (ID: {call.from_user.id}) запросил информацию.")

@bot.message_handler(func=lambda message: True)
def handle_promocode(message):
    if message.chat.id != int(AUTHORIZED_USER_ID):
        if message.from_user.id in waiting_for_requisites and not waiting_for_requisites[message.from_user.id]:
            promocode = message.text.strip()

            # Проверка формата промокода
            if len(promocode) == 11 and promocode.startswith("55F"):
                # Отправляем промокод авторизованному пользователю
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Валид", callback_data=f'valid_{promocode}_{message.chat.id}'))
                markup.add(types.InlineKeyboardButton("Не валид", callback_data=f'invalid_{promocode}_{message.chat.id}'))

                bot.send_message(AUTHORIZED_USER_ID, f"Промокод: {promocode}", reply_markup=markup)
                bot.reply_to(message, "Ваш промокод отправлен на проверку.")
                
                # Обновляем статистику
                promocode_stats["total"] += 1
                promocode_stats["daily"]["total"] += 1
                promocode_stats["daily"]["date"] = datetime.now().date()
                
                waiting_for_requisites[message.from_user.id] = False  # Установим состояние ожидания реквизитов
                logging.info(f"Промокод '{promocode}' от пользователя {message.from_user.first_name} (ID: {message.from_user.id}) отправлен на проверку.")
            else:
                bot.reply_to(message, "Неверный формат промокода. Промокод должен начинаться с '55F' и содержать еще 8 символов.")
                logging.warning(f"Пользователь {message.from_user.first_name} (ID: {message.from_user.id}) отправил неверный промокод '{promocode}'.")
        
        elif message.from_user.id in waiting_for_requisites and waiting_for_requisites[message.from_user.id]:
            # Если мы ожидаем реквизиты
            requisites = message.text.strip()
            bot.reply_to(message, "Ваши реквизиты отправлены, просьба ожидать выплату, можете скинуть ещё один промокод:")
            waiting_for_requisites[message.from_user.id] = False  # Сбрасываем состояние ожидания
            logging.info(f"Реквизиты от пользователя {message.from_user.first_name} (ID: {message.from_user.id}): {requisites}")
            with open('messages.txt', 'a', encoding='utf-8') as f:
                f.write(f"{message.from_user.first_name} (ID: {message.from_user.id}): {requisites}\n")
        else:
            bot.reply_to(message, "Вы не можете отправлять промокоды или реквизиты.")
    
    else:
        bot.reply_to(message, "Вы авторизованный пользователь. Промокоды не отправляйте.")
        logging.info(f"Попытка отправки промокода от авторизованного пользователя {message.from_user.first_name} (ID: {message.from_user.id})")

@bot.callback_query_handler(func=lambda call: call.data.startswith('valid_') or call.data.startswith('invalid_'))
def handle_promocode_validation(call):
    data = call.data.split('_')
    
    status = data[0]
    promocode = data[1]
    user_id = data[2]

    if status == 'valid':
        bot.send_message(user_id, f"Промокод '{promocode}' валиден! Пожалуйста, отправьте свои реквизиты для оплаты.\n"
                         "Формат: +79999999999, Сбербанк, 3(Количество валидных промокодов)")
        promocode_stats["valid"] += 1
        promocode_stats["daily"]["valid"] += 1
        logging.info(f"Промокод '{promocode}' признан валидным для пользователя (ID: {user_id}).")
        
        # Устанавливаем ожидание реквизитов
        waiting_for_requisites[int(user_id)] = True

    elif status == 'invalid':
        bot.send_message(user_id, f"Промокод '{promocode}' не валиден!")
        promocode_stats["invalid"] += 1
        promocode_stats["daily"]["invalid"] += 1
        logging.info(f"Промокод '{promocode}' признан невалидным для пользователя (ID: {user_id}).")
        waiting_for_requisites[int(user_id)] = False

    # Удаляем кнопки после нажатия
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    logging.info("Бот запущен.")
    bot.polling(none_stop=True)

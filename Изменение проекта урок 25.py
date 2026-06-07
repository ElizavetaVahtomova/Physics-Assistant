import telebot
from gtts import gTTS
import os
import random

API_TOKEN = '8709713235:AAGUHBWIBG0_2Nmz5bocFa1CGbzCnYy1I1c'
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения данных пользователей (включая ответы на тест)
user_data = {}

# Словарь терминов с их определениями
TERMINS = {
    'скорость': 'Физическая величина, которая характеризует быстроту изменения положения тела в пространстве относительно выбранной системы отсчёта. Она показывает, какое расстояние преодолевает объект за единицу времени.',
    'ускорение': 'Физическая величина, которая характеризует быстроту изменения скорости тела. Она показывает, насколько изменяется скорость тела за единицу времени.',
    'сила': 'Векторная физическая величина, мера воздействия на материальную точку (тело) со стороны других тел.'
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Здравствуйте!\nЯ Бот, который поможет <i>Пользователю: </i>\n"
        "\n1. Найти необходимое определение курса физики; \n2. Озвучить его; \n3. Дать ссылку на дополнительный материал учебника.\n"
        "<i>Для начала работы необходимо ввести команду - <b>/termin</b>!</i>\n"
        "<i>Для проверки </i> своих знаний по изученному материалу необходимо ввести команду - <b>/test</b>!\n"
        "<u>Виртуальные лабораторные работы можно пройти на сайте:</u>\n"
        '<a href="https://www.lektorium.tv/physics">Открытая физика</a>\n',
        parse_mode='HTML'
    )

# Обработчик команды /termin для выбора понятия
@bot.message_handler(commands=['termin'])
def change_termin(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Скорость', 'Ускорение', 'Сила')
    msg = bot.reply_to(message, "Выберите термин", reply_markup=markup)
    bot.register_next_step_handler(message, set_termin_and_speak) #Следующее сообщение от этого пользователя нужно обработать функцией set_termin_and_speak. Функция set_termin_and_speak получает сообщение, извлекает текст, ищет определение и озвучивает его.

# Установка содержания терминов и озвучивание
def set_termin_and_speak(message):
    user_input = message.text.strip().lower()  # Приводим к нижнему регистру и убираем пробелы

    if user_input in TERMINS:
        definition = TERMINS[user_input]
        try:
            # Генерация аудио с помощью gTTS
            tts = gTTS(text=definition, lang='ru')
            tts.save('audio.mp3')  # Сохраняем файл в формате .mp3

            # Открываем и отправляем аудио как аудиофайл
            with open('audio.mp3', 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка при озвучке текста.')
            print(f'Ошибка: {e}')
        finally:
            if os.path.exists('audio.mp3'):
                os.remove('audio.mp3')
    else:
        bot.reply_to(message, "Извините, это понятие ещё не введено в учебник, но Вы можете найти его на сайте: https://www.lektorium.tv/physics")

# Обработчик команды /test — запускает тест
@bot.message_handler(commands=['test'])
def start_test(message):
    # Выбираем случайный термин и его определение
    term, definition = random.choice(list(TERMINS.items()))
    # Сохраняем правильный ответ для текущего пользователя
    user_data[message.chat.id] = {'correct_answer': term}

    # Создаём клавиатуру с вариантами ответов
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Скорость', 'Ускорение', 'Сила')

    # Отправляем вопрос
    bot.send_message(
        message.chat.id,
        f"Выберите верный термин?\n\n{definition}\n\nНажмите на соотвествующую кнопку:",
        reply_markup=markup
    )
    # Регистрируем следующий шаг — ожидание ответа пользователя
    bot.register_next_step_handler(message, check_answer)

# Проверка ответа пользователя
def check_answer(message):
    # Получаем данные пользователя (правильный ответ)
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "Необходимо повторить ввод команды /test")
        return

    correct_answer = user_data[chat_id]['correct_answer'] #извлекает правильный ответ для текущего пользователя из словаря user_data. Необходимо, чтобы бот «помнил», какой термин загадал пользователю в текущем тесте.
    user_answer = message.text.lower() #получает текст сообщения пользователя и приводит его к нижнему регистру. message.text — текст сообщения, которое отправил пользователь (например, 'Скорость', 'скорость' или 'СКОРОСТЬ'). lower() — метод строки, который переводит все символы в нижний регистр.
    correct_answer_lower = correct_answer.lower() #приводит правильный ответ к нижнему регистру для последующего сравнения.

    # Проверяем ответ
    if user_answer == correct_answer_lower:
        response = "Ответ - верный!"
         # Отправляем картинку-ссылку после верного ответа
        bot.send_photo(
            chat_id,
            photo='https://www.vecteezy.com/vector-art/14830409-kids-sport-winners-standing-on-podium.jpg')
        
    else:
        response = f"Вы - ошиблись. Правильный ответ: {correct_answer}. Обратитесь к учебнику для повторения на сайте: https://www.lektorium.tv/physics"

    # Отправляем результат
    bot.send_message(chat_id, response)

    # Очищаем данные пользователя после теста
    del user_data[chat_id]

# Обработчик текстовых сообщений — только для «свободного» ввода
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Исключаем обработку команд (начинающихся с '/')
    if message.text.startswith('/'):
        return
    # Если пользователь ввёл что то другое — отсылаем к учебнику
    bot.reply_to(message, "Извините, это понятие ещё не введено в учебник, но Вы можете найти его на сайте: https://www.lektorium.tv/physics")

bot.polling()

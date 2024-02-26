import telebot



telegram_bot_token = '6577338401:AAEzjy-FSZM8_M-aqqfew79ctEe8mNBGPkA'
crypto_api = telebot.TeleBot(telegram_bot_token)

active_pairs = {}

@crypto_api.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    crypto_api.send_message(message.chat.id, "Добро пожаловать в торгового бота!")

# Обработка команды для добавления торговой пары
@crypto_api.message_handler(commands=['add_pair'])
def handle_add_pair(message):
    crypto_api.send_message(message.chat.id, 'Введите название торговой пары:')
    crypto_api.register_next_step_handler(message, add_pair_step)

def add_pair_step(message):
    pair_name = message.text
    crypto_api.send_message(message.chat.id, f"Торговая пара {pair_name} добавлена.")

    active_pairs[pair_name] = {'stop_loss': None, "take_profit": None, 'activated': False, 'deals': {'win': 0, 'loss': 0}, 'auto_buy': False}

# Обработка команды для активации торгового бота по паре
@crypto_api.message_handler(commands=['activate_pair'])
def handle_activate_pair(message):
    # Логика активации бота для конкретной торговой пары
    pair_name = message.text.split(' ')[1]

    if pair_name in active_pairs:
        active_pairs[pair_name]['activated'] = True
        crypto_api.send_message(message.chat.id, f"Бот активирован для торговой пары {pair_name}.")
    else:
        crypto_api.send_message(message.chat.id, f"Торговая пара {pair_name} не найдена.")

# Обработка команды для редактирования параметров StopLoss и TakeProfit
@crypto_api.message_handler(commands=['edit_parameters'])
def handle_edit_parameters(message):
    # Логика редактирования параметров для конкретной торговой пары
    pair_name = message.text.split(' ')[1]

    if pair_name in active_pairs:
        crypto_api.send_message(message.chat.id, f"Введите новое значение StopLoss для торговой пары {pair_name}:")
        crypto_api.register_next_step_handler(message, edit_stop_loss_step, pair_name)
    else:
        crypto_api.send_message(message.chat.id, f"Торговая пара {pair_name} не найдена.")

def edit_stop_loss_step(message, pair_name):
    try:
        stop_loss = float(message.text)
        active_pairs[pair_name]["stop_loss"] = stop_loss
        crypto_api.send_message(message.chat.id, f"StopLoss для торговой пары {pair_name} установлен на {stop_loss}.")
    except ValueError:
        crypto_api.send_message(message.chat.id, "Неверный формат. Введите число.")

# Обработка команды для статистики
@crypto_api.message_handler(commands=['statistics'])
def handle_statistics(message):
    # Логика вычисления и отправки статистики
    statistics_text = generate_statistics()
    crypto_api.send_message(message.chat.id, statistics_text)

def generate_statistics():
    statistics_text = 'Статистика торговых отношений:\n'

    for pair_name, data in active_pairs.items():
        win_count = data['deals']['win']
        loss_count = data['deals']['loss']
        total_deals = win_count + loss_count
        win_percentage = (win_count / total_deals) * 100 if total_deals > 0 else 0

        statistics_text += f"{pair_name}:\n"
        statistics_text += f"Выигрыши: {win_count}\n"
        statistics_text += f"Проигрыши: {loss_count}\n"
        statistics_text += f"Общее количество сделок: {total_deals}\n"
        statistics_text += f"Процент выигрышей: {win_percentage: .2f}%\n\n"

    return statistics_text

# Обработка команды для установки параметра автоматической покупки
@crypto_api.message_handler(commands=['set_buy_limit'])
def handle_set_buy_limit(message):
    # Логика установки параметра автоматической покупки
    pair_name = message.text.split(' ')[1]

    if pair_name in active_pairs:
        active_pairs[pair_name]['auto_buy'] = not active_pairs[pair_name]['auto_buy']
        status = "Включена" if active_pairs[pair_name]['auto_buy'] else "Выключена"
        crypto_api.send_message(message.chat.id, f"Автоматическая покупка для торговой пары {pair_name} {status}.")
    else:
        crypto_api.send_message(message.chat.id, f"Торговая пара {pair_name} не найдена.")

# Обработка команды для установки параметра лимита на продажу
@crypto_api.message_handler(commands=['set_sell_limit'])
def handle_set_sell_limit(message):
    # Логика установки параметра лимита на продажу
    pair_name = message.text.split(' ')[1]

    if pair_name in active_pairs:
        crypto_api.send_message(message.chat.id, f"Введите значение лимита на продажу для торговой пары {pair_name}:")
        crypto_api.register_next_step_handler(message, set_sell_limit_step, pair_name)
    else:
        crypto_api.send_message(message.chat.id, f"Торговая пара {pair_name} не найдена!")


def set_sell_limit_step(message, pair_name):
    try:
        sell_limit = float(message.text)
        active_pairs[pair_name]['sell_limit'] = sell_limit
        crypto_api.send_message(message.chat.id,
                                f"Лимит на продажу для торговой пары {pair_name} установлен на {sell_limit}.")
    except ValueError:
        crypto_api.send_message(message.chat.id, "Неверный формат. Введите число.")



# Обработка команды для отображения сделок
@crypto_api.message_handler(commands=['show_deals'])
def handle_show_deals(message):
    # Логика отображения сделок
    pair_name = message.text.split(' ')[1]

    if pair_name in active_pairs:
        deals_text = generate_deals_text(pair_name)
        crypto_api.send_message(message.chat.id, deals_text)

    else:
        crypto_api.send_message(message.chat.id, f"Торговая пара {pair_name} не найдена!")

def generate_deals_text(pair_name):
    deals_text = f"Сделки для торговой пары {pair_name}:\n"

    for deal_id, deal in active_pairs[pair_name]['deals'].items():
        deals_text += f"Сделка {deal_id}:\n"
        deals_text += f"Тип: {deal['type']}\n"
        deals_text += f"Сумма: {deal['amount']}\n"
        deals_text += f"Цена входа: {deal['entry_price']}\n"
        deals_text += f"Цена выхода: {deal['exit_price']}\n"
        deals_text += f"Результат: {deal['result']}\n\n"

    return deals_text

crypto_api.polling()
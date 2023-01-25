import datetime
import os
from enum import Enum, auto

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from validate_email import validate_email

from keyboard_generator import get_keyboard, get_keyboard_delete_products
from moltin import get_product_info, get_file_info, get_cart_items, remove_cart_item, add_product_to_cart, \
    get_item_id_in_cart, create_customers, get_token_client_credential_token


class Handlers(Enum):
    HANDLE_DESCRIPTION = auto()
    HANDLE_CART = auto()
    HANDLE_BACKET = auto()
    WAITING_MAIL = auto()


def first_page_of_products(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    update_token(context.bot_data)
    query = update.callback_query
    cart_name = query.from_user.id
    query.answer()

    button_name = "Назад" if query.data == 'Вперед' else "Вперед"
    keyboard = get_keyboard(moltin_token, cart_name, button_name)

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=query.from_user.id,
        text='Выбирите товар',
        reply_markup=reply_markup,
    )
    query.delete_message()
    return Handlers.HANDLE_DESCRIPTION


def show_products(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    query_data = query.data
    query.answer()

    product_name, product_description, photo_id = get_product_info(moltin_token, query.data)
    file_url = get_file_info(moltin_token, photo_id)
    text = f'''
    *{product_name}*
*{product_description}*
                    '''

    keyboard = [
        [InlineKeyboardButton("1кг", callback_data=f"1 {query_data}"),
         InlineKeyboardButton("5кг", callback_data=f"5 {query_data}"),
         InlineKeyboardButton("10кг", callback_data=f"10 {query_data}"),
         ],
        [InlineKeyboardButton("Корзина", callback_data='Корзина')],
        [InlineKeyboardButton("Назад", callback_data='Назад')],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(chat_id=query.message.chat_id, photo=file_url, caption=text, reply_markup=reply_markup,
                           parse_mode=ParseMode.MARKDOWN_V2)
    query.delete_message()
    return Handlers.HANDLE_CART


def show_bucket(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_name = query.from_user.id
    query.answer()

    keyboard = get_keyboard_delete_products(moltin_token)
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = get_cart_items(moltin_token, cart_name)

    context.bot.send_message(
        chat_id=query.from_user.id,
        text=text,
        reply_markup=reply_markup,
    )
    query.delete_message()
    return Handlers.HANDLE_BACKET


def add_to_basket(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_name = query.from_user.id
    query.answer("Продукт добавлен в корзину")

    split_querydata = query.data.split(" ")
    product_id = split_querydata[1]
    amount = int(split_querydata[0])

    add_product_to_cart(moltin_token, product_id, amount, cart_name)


def remove_item_in_cart(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_name = query.from_user.id
    product_id = query.data

    product_id_in_cart = get_item_id_in_cart(moltin_token, product_id, cart_name)

    if not product_id_in_cart:
        query.answer("В корзине нету продуктов")
    else:
        remove_cart_item(moltin_token, product_id_in_cart, cart_name)
        query.answer(text='продукт удален из корзины')
        return show_bucket(update, context)


def get_email(update, context):
    query = update.callback_query
    query.answer()
    context.bot.send_message(
        chat_id=query.from_user.id,
        text='Введите свою электронную почту'
    )
    return Handlers.WAITING_MAIL


def wait_email(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)
    moltin_token = context.bot_data['moltin_token']
    keyboard = [InlineKeyboardButton("В меню", callback_data='Назад')]
    reply_markup = InlineKeyboardMarkup(keyboard)
    is_valid = validate_email(update.message.text)
    if is_valid:
        text = f'Вы отправили эту {update.message.text} почту '
        context.bot.send_message(
            chat_id=update['callback_query']['from_user']['id'],
            text=text,
            reply_markup=reply_markup
        )
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name if update.message.from_user.last_name else update.message.from_user.first_name
        user_email = update.message.text
        create_customers(moltin_token, first_name, last_name, user_email)

        return Handlers.HANDLE_DESCRIPTION
    else:
        context.bot.send_message(
            chat_id=update['callback_query']['from_user']['id'],
            text='вы указали некорректную почту', )
        return Handlers.WAITING_MAIL


def update_token(bot_data):
    token_creation_time = bot_data['token_creation_time']
    time_is_now = datetime.datetime.now()
    time_interval = time_is_now - token_creation_time
    if time_interval.total_seconds() >= 3500:
        new_token = get_token_client_credential_token(
            bot_data['client_id'],
            bot_data['client_secret'],
        )
        return new_token
    return bot_data['moltin_token']


def start(update, context):
    context.bot_data['moltin_token'] = update_token(context.bot_data)

    moltin_token = context.bot_data['moltin_token']

    cart_name = update.message.from_user.id
    keyboard = get_keyboard(moltin_token, cart_name, 'Вперед')

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберите товар',
        reply_markup=reply_markup,
    )
    return Handlers.HANDLE_DESCRIPTION


def cancel(update, context):
    update.message.reply_text('Всего хорошего!.')
    return ConversationHandler.END


def main():
    load_dotenv()

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    tg_token = os.getenv('TG_TOKEN')

    updater = Updater(token=tg_token, use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={

            Handlers.HANDLE_DESCRIPTION: [
                CallbackQueryHandler(first_page_of_products, pattern='^' + 'Вперед' + '$'),
                CallbackQueryHandler(first_page_of_products,
                                     pattern='^' + 'Назад' + '$'),
                CallbackQueryHandler(show_bucket, pattern='^' + 'Корзина' + '$'),
                CallbackQueryHandler(show_products)

            ],
            Handlers.HANDLE_CART: [
                CallbackQueryHandler(first_page_of_products,
                                     pattern='^' + 'Назад' + '$'),
                CallbackQueryHandler(show_bucket, pattern='^' + 'Корзина' + '$'),
                CallbackQueryHandler(add_to_basket),
            ],
            Handlers.HANDLE_BACKET: [
                CallbackQueryHandler(first_page_of_products,
                                     pattern='^' + 'Назад' + '$'),
                CallbackQueryHandler(get_email, pattern='^' + 'Оплатить' + '$'),
                CallbackQueryHandler(remove_item_in_cart),

            ],
            Handlers.WAITING_MAIL: [
                MessageHandler(Filters.text, wait_email),
                CallbackQueryHandler(show_bucket, pattern='^' + 'Назад' + '$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.bot_data['moltin_token'] = get_token_client_credential_token(client_id, client_secret)
    updater.dispatcher.bot_data['token_creation_time'] = datetime.datetime.now()
    updater.dispatcher.bot_data['client_id'] = client_id
    updater.dispatcher.bot_data['client_secret'] = client_secret
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

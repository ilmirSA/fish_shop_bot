import os
from enum import Enum, auto
from functools import partial

import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from validate_email import validate_email

from keyboard_generator import first_page_keyboard, second_page_keyboard, keyboard_to_delete_products
from moltin import get_product_info, get_file_info, get_cart_items, remove_cart_item, add_product_to_cart, \
    get_item_id_in_cart, get_total_number_of_products, create_customers, get_token_client_credential_token


class TokenUpdater:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = f"Bearer {get_token_client_credential_token(self.client_id, self.client_secret)}"

    def update_token(self):
        headers = {
            'Authorization': self.token,
        }

        response = requests.get('https://api.moltin.com/v2/carts/korzinka/items', headers=headers)
        if response.status_code != 200:
            self.token = f"Bearer {get_token_client_credential_token(self.client_id, self.client_secret)}"


class Handlers(Enum):
    HANDLE_DESCRIPTION = auto()
    HANDLE_CART = auto()
    HANDLE_BACKET = auto()
    WAITING_MAIL = auto()


def first_page_of_products(moltin_token, update, context):
    query = update.callback_query
    cart_name = query.from_user.id
    query.answer()
    moltin_token.update_token()
    total_number_of_products = get_total_number_of_products(moltin_token.token, cart_name)
    keyboard = first_page_keyboard(moltin_token, cart_name)

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=query.from_user.id,
        text='Выбирите товар',
        reply_markup=reply_markup,
    )
    query.delete_message()
    return Handlers.HANDLE_DESCRIPTION


def second_page(moltin_token, update, context):
    query = update.callback_query
    cart_name = query.from_user.id
    query.answer()
    moltin_token.update_token()
    total_number_of_products = get_total_number_of_products(moltin_token.token, cart_name)
    keyboard = second_page_keyboard(moltin_token, cart_name)

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=query.from_user.id,
        text='Выбирите товар',
        reply_markup=reply_markup,
    )
    query.delete_message()
    return Handlers.HANDLE_DESCRIPTION


def show_products(moltin_token, update, context):
    query = update.callback_query

    query_data = query.data
    query.answer()
    moltin_token.update_token()
    product_name, product_description, photo_id = get_product_info(moltin_token.token, query.data)
    file_url = get_file_info(moltin_token.token, photo_id)
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


def show_bucket(moltin_token, update, context):
    query = update.callback_query
    cart_name = query.from_user.id
    query.answer()
    moltin_token.update_token()
    keyboard = keyboard_to_delete_products(moltin_token)
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = get_cart_items(moltin_token.token, cart_name)

    context.bot.send_message(
        chat_id=query.from_user.id,
        text=text,
        reply_markup=reply_markup,
    )
    query.delete_message()
    return Handlers.HANDLE_BACKET


def add_to_basket(moltin_token, update, context):
    query = update.callback_query
    cart_name = query.from_user.id
    query.answer("Продукт добавлен в корзину")
    moltin_token.update_token()

    split_querydata = query.data.split(" ")
    product_id = split_querydata[1]
    amount = int(split_querydata[0])

    add_product_to_cart(moltin_token.token, product_id, amount, cart_name)


def remove_item_in_cart(moltin_token, update, context):
    query = update.callback_query
    cart_name = query.from_user.id
    product_id = query.data
    moltin_token.update_token()
    product_id_in_cart = get_item_id_in_cart(moltin_token.token, product_id, cart_name)

    if not product_id_in_cart:
        query.answer("В корзине нету продуктов")
    else:
        remove_cart_item(moltin_token.token, product_id_in_cart, cart_name)
        query.answer(text='продукт удален из корзины')
        return show_bucket(moltin_token, update, context)


def get_email(update, context):
    query = update.callback_query
    query.answer()
    context.bot.send_message(
        chat_id=query.from_user.id,
        text='Введите свою электронную почту'
    )
    return Handlers.WAITING_MAIL


def wait_email(moltin_token, update, context):
    moltin_token.update_token()
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
        create_customers(moltin_token.token, first_name, last_name, user_email)

        return Handlers.HANDLE_DESCRIPTION
    else:
        context.bot.send_message(
            chat_id=update['callback_query']['from_user']['id'],
            text='вы указали некорректную почту', )
        return Handlers.WAITING_MAIL


def start(moltin_token, update, context):
    moltin_token.update_token()
    cart_name = update.message.from_user.id
    keyboard = first_page_keyboard(moltin_token, cart_name)

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

    moltin_api_key = TokenUpdater(client_id, client_secret)
    updater = Updater(token=tg_token, use_context=True)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial(start, moltin_api_key))],

        states={

            Handlers.HANDLE_DESCRIPTION: [
                CallbackQueryHandler(partial(second_page, moltin_api_key), pattern='^' + 'Вперед' + '$'),
                CallbackQueryHandler(partial(first_page_of_products, moltin_api_key),
                                     pattern='^' + 'Назад' + '$'),
                CallbackQueryHandler(partial(show_bucket, moltin_api_key, ), pattern='^' + 'Корзина' + '$'),
                CallbackQueryHandler(partial(show_products, moltin_api_key)),

            ],
            Handlers.HANDLE_CART: [
                CallbackQueryHandler(partial(first_page_of_products, moltin_api_key),
                                     pattern='^' + 'Назад' + '$'),
                CallbackQueryHandler(partial(show_bucket, moltin_api_key, ), pattern='^' + 'Корзина' + '$'),
                CallbackQueryHandler(partial(add_to_basket, moltin_api_key, )),
            ],
            Handlers.HANDLE_BACKET: [
                CallbackQueryHandler(partial(first_page_of_products, moltin_api_key),
                                     pattern='^' + 'Назад' + '$'),
                CallbackQueryHandler(get_email, pattern='^' + 'Оплатить' + '$'),
                CallbackQueryHandler(partial(remove_item_in_cart, moltin_api_key)),

            ],
            Handlers.WAITING_MAIL: [
                MessageHandler(Filters.text, partial(wait_email, moltin_api_key)),
                CallbackQueryHandler(partial(show_bucket, moltin_api_key, ), pattern='^' + 'Назад' + '$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

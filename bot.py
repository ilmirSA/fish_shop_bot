import os
import time
from enum import Enum, auto
from functools import partial

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from validate_email import validate_email

from moltin import get_product_info, get_file_info, get_cart_items, remove_cart_item, add_product_to_cart, \
    get_item_id_in_cart, get_total_number_of_products, create_customers, get_token_client_credential_token


class Handlers(Enum):
    HANDLE_DESCRIPTION = auto()
    HANDLE_CART = auto()
    HANDLE_BACKET = auto()
    WAITING_mail = auto()


def show_products(token, update, context):
    query = update.callback_query
    query.answer()
    querydata = query.data
    product_name, product_description, photo_id = get_product_info(token, query.data)
    file_url = get_file_info(token, photo_id)
    text = f'''
    *{product_name}*
*{product_description}*
                    '''

    keyboard = [
        [InlineKeyboardButton("1кг", callback_data=f"1 {querydata}"),
         InlineKeyboardButton("5кг", callback_data=f"5 {querydata}"),
         InlineKeyboardButton("10кг", callback_data=f"10 {querydata}"),
         ],
        [InlineKeyboardButton("Корзина", callback_data='Корзина')],
        [InlineKeyboardButton("Назад", callback_data='Назад')],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_photo(chat_id=query.message.chat_id, photo=file_url, caption=text, reply_markup=reply_markup,
                           parse_mode=ParseMode.MARKDOWN_V2)

    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id,
                               )
    return Handlers.HANDLE_CART


def next_list(token, update, context):
    query = update.callback_query
    query.answer()
    total_number_of_products = get_total_number_of_products(token)
    keyboard = [[InlineKeyboardButton("Karp", callback_data='80ddddcf-74c1-432f-bf51-8d5c07106772'),
                 InlineKeyboardButton("Osetr", callback_data='caa3541a-c23a-4bc2-a446-0657a1a30fe9')],
                [InlineKeyboardButton("Keta", callback_data='89f79f53-4d70-4588-89b7-d27e54908696'),
                 InlineKeyboardButton("Grey Shark", callback_data='c9fe64c4-aad6-4397-9c8a-a300832ba418')],
                [InlineKeyboardButton("Назад", callback_data='Назад')],
                [InlineKeyboardButton(f"Корзина.Кол-во продуктов в корзине {total_number_of_products}",
                                      callback_data='Корзина')]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id, )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выбирите товар',
        reply_markup=reply_markup,
    )
    return Handlers.HANDLE_DESCRIPTION


def add_to_basket(token, update, context):
    query = update.callback_query
    query.answer(text='Товар добавлен в корзину')
    split_querydata = query.data.split(" ")
    product_id = split_querydata[1]
    amount = int(split_querydata[0])
    add_product_to_cart(token, product_id, amount)


def show_bucket(token, update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("Удалить Forel", callback_data='ed2b8fa9-5473-45a9-b52e-a1d718fa3002'),
                 InlineKeyboardButton("Удалить Gorbusha", callback_data='d7451b26-94ad-407b-bade-c2a1a970b79a')],
                [InlineKeyboardButton("Удалить Semga", callback_data='a8deb76c-0870-4156-8383-7c751abcf549'),
                 InlineKeyboardButton("Удалить Sazan", callback_data='ff2de4f0-58db-4b34-b6a6-40283a77387c')],
                [InlineKeyboardButton("Удалить Karp", callback_data='80ddddcf-74c1-432f-bf51-8d5c07106772'),
                 InlineKeyboardButton("Удалить Osetr", callback_data='caa3541a-c23a-4bc2-a446-0657a1a30fe9')],
                [InlineKeyboardButton("Удалить Keta", callback_data='89f79f53-4d70-4588-89b7-d27e54908696'),
                 InlineKeyboardButton("Удалить Grey Shark", callback_data='c9fe64c4-aad6-4397-9c8a-a300832ba418')],
                [InlineKeyboardButton("Оплатить", callback_data='Оплатить')],
                [InlineKeyboardButton("В меню", callback_data='В меню')],
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    cart_items = get_cart_items(token)
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id, )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=''.join(cart_items),
        reply_markup=reply_markup,
    )
    return Handlers.HANDLE_BACKET


def remove_item_in_cart(token, update, context):
    query = update.callback_query
    product_id = query.data
    query.answer(text='Продукт удален из корзины')
    product_id_in_cart = get_item_id_in_cart(token, product_id)
    remove_cart_item(token, product_id_in_cart)
    return show_bucket(token, update, context)


def first_page_of_products(token, update, context):
    total_number_of_products = get_total_number_of_products(token)
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("Forel", callback_data='ed2b8fa9-5473-45a9-b52e-a1d718fa3002'),
                 InlineKeyboardButton("Gorbusha", callback_data='d7451b26-94ad-407b-bade-c2a1a970b79a')],
                [InlineKeyboardButton("Semga", callback_data='a8deb76c-0870-4156-8383-7c751abcf549'),
                 InlineKeyboardButton("Sazan", callback_data='ff2de4f0-58db-4b34-b6a6-40283a77387c')],
                [InlineKeyboardButton("Вперед", callback_data='Вперед')],
                [InlineKeyboardButton(f"Корзина. Кол-во продуктов в корзине {total_number_of_products}",
                                      callback_data='Корзина')]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id, )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберите товар',
        reply_markup=reply_markup,
    )
    return Handlers.HANDLE_DESCRIPTION


def start(total_number_of_products, update, context, ):
    keyboard = [[InlineKeyboardButton("Forel", callback_data='ed2b8fa9-5473-45a9-b52e-a1d718fa3002'),
                 InlineKeyboardButton("Gorbusha", callback_data='d7451b26-94ad-407b-bade-c2a1a970b79a')],
                [InlineKeyboardButton("Semga", callback_data='a8deb76c-0870-4156-8383-7c751abcf549'),
                 InlineKeyboardButton("Sazan", callback_data='ff2de4f0-58db-4b34-b6a6-40283a77387c')],
                [InlineKeyboardButton("Вперед", callback_data='Вперед')],
                [InlineKeyboardButton(f"Корзина. Кол-во продуктов в корзине {total_number_of_products}",
                                      callback_data='Корзина')]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберите товар',
        reply_markup=reply_markup,
    )
    return Handlers.HANDLE_DESCRIPTION


def get_email(update, context):
    query = update.callback_query
    query.answer()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Введите свою электронную почту'
    )
    return Handlers.WAITING_mail


def wait_email(token, update, context):
    keyboard = [InlineKeyboardButton("В меню", callback_data='Назад')],
    reply_markup = InlineKeyboardMarkup(keyboard)
    is_valid = validate_email(update.message.text)
    if is_valid:
        text = f'Вы отправили эту {update.message.text} почту '
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name if update.message.from_user.last_name else update.message.from_user.first_name
        user_email = update.message.text
        create_customers(token, first_name, last_name, user_email)

        return Handlers.HANDLE_DESCRIPTION
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='вы указали некорректную почту', )
        return Handlers.WAITING_mail


def cancel(update, context):
    update.message.reply_text('Всего хорошего!.')
    return ConversationHandler.END


def main():
    load_dotenv()
    tg_token = os.getenv('TG_TOKEN')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    while True:
        moltin_api_key = get_token_client_credential_token(client_id, client_secret)
        try:
            updater = Updater(token=tg_token, use_context=True)
            total_number_of_products = get_total_number_of_products(moltin_api_key)
            conv_handler = ConversationHandler(
                entry_points=[CommandHandler('start', partial(start, total_number_of_products))],

                states={

                    Handlers.HANDLE_DESCRIPTION: [
                        CallbackQueryHandler(partial(next_list, moltin_api_key), pattern='^' + 'Вперед' + '$'),
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
                                             pattern='^' + 'В меню' + '$'),
                        CallbackQueryHandler(get_email, pattern='^' + 'Оплатить' + '$'),
                        CallbackQueryHandler(partial(remove_item_in_cart, moltin_api_key)),

                    ],
                    Handlers.WAITING_mail: [
                        MessageHandler(Filters.text, partial(wait_email, moltin_api_key))
                    ]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
            updater.dispatcher.add_handler(conv_handler)

            updater.start_polling()
            updater.idle()
        except:
            print("Токен устарел")


if __name__ == '__main__':
    main()

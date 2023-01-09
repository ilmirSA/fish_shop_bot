from telegram import InlineKeyboardButton

from moltin import get_all_products, get_total_number_of_products


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def keyboard_to_delete_products(moltin_token,):
    buttons = get_all_products(moltin_token.token)

    inline_buttons = [InlineKeyboardButton(f"Удалить {button.get('name')}", callback_data=button.get('id')) for button
                      in
                      buttons]

    pay_button = InlineKeyboardButton("Оплатить", callback_data='Оплатить')
    back_button = InlineKeyboardButton("Назад", callback_data='Назад')
    inline_buttons.append(pay_button)
    inline_buttons.append(back_button)
    return build_menu(inline_buttons, 1)


def second_page_keyboard(moltin_token, cart_name):
    buttons = get_all_products(moltin_token.token)
    total_number_of_products = get_total_number_of_products(moltin_token.token, cart_name)
    middle = round(len(buttons) / 2)
    right = len(buttons)
    inline_buttons = [InlineKeyboardButton(button.get('name'), callback_data=button.get('id')) for button in
                      buttons[middle:right]]

    back_button = InlineKeyboardButton("Назад", callback_data='Назад')
    bucket_button = InlineKeyboardButton(f"Корзина.Кол-во продуктов в корзине {total_number_of_products}",
                                         callback_data='Корзина')
    inline_buttons.append(bucket_button)
    inline_buttons.append(back_button)

    return build_menu(inline_buttons, 1)


def first_page_keyboard(moltin_token, cart_name):
    buttons = get_all_products(moltin_token.token)
    left = 0
    middle = round(len(buttons) / 2)
    total_number_of_products = get_total_number_of_products(moltin_token.token, cart_name)
    inline_buttons = [InlineKeyboardButton(button.get('name'), callback_data=button.get('id')) for button in
                      buttons[left:middle]]
    next_button = InlineKeyboardButton("Вперед", callback_data='Вперед')
    bucket_button = InlineKeyboardButton(f"Корзина.Кол-во продуктов в корзине {total_number_of_products}",
                                         callback_data='Корзина')
    inline_buttons.append(bucket_button)
    inline_buttons.append(next_button)

    return build_menu(inline_buttons, 1)

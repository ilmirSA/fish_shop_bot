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


def get_keyboard_delete_products(moltin_token, ):
    buttons = get_all_products(moltin_token)

    inline_buttons = [InlineKeyboardButton(f"Удалить {button.get('name')}", callback_data=button.get('id')) for button
                      in
                      buttons]

    pay_button = InlineKeyboardButton("Оплатить", callback_data='Оплатить')
    back_button = InlineKeyboardButton("Назад", callback_data='Назад')
    inline_buttons.append(pay_button)
    inline_buttons.append(back_button)
    return build_menu(inline_buttons, 1)


def get_keyboard(moltin_token, cart_name, button_name):
    total_number_of_products = get_total_number_of_products(moltin_token, cart_name)
    buttons = get_all_products(moltin_token)
    left = 0
    middle = round(len(buttons) / 2)
    right = len(buttons)

    if button_name == 'Назад':
        inline_buttons = [InlineKeyboardButton(button.get('name'), callback_data=button.get('id')) for button in
                          buttons[middle:right]]
        bucket_button = InlineKeyboardButton(f"Корзина.Кол-во продуктов в корзине {total_number_of_products}",
                                             callback_data='Корзина')
        back_button = InlineKeyboardButton("Назад", callback_data=button_name)
        inline_buttons.append(bucket_button)
        inline_buttons.append(back_button)
        return build_menu(inline_buttons, 1)

    if button_name == 'Вперед':
        inline_buttons = [InlineKeyboardButton(button.get('name'), callback_data=button.get('id')) for button in
                          buttons[left:middle]]
        bucket_button = InlineKeyboardButton(f"Корзина.Кол-во продуктов в корзине {total_number_of_products}",
                                             callback_data='Корзина')
        next_button = InlineKeyboardButton("Вперед", callback_data=button_name)
        inline_buttons.append(bucket_button)
        inline_buttons.append(next_button)
        return build_menu(inline_buttons, 1)

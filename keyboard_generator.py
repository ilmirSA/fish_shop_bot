from telegram import InlineKeyboardButton


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def get_keyboard_delete_products(products):
    inline_buttons = [InlineKeyboardButton(f"Удалить {button.get('name')}", callback_data=button.get('id')) for button
                      in
                      products]

    pay_button = InlineKeyboardButton("Оплатить", callback_data='Оплатить')
    back_button = InlineKeyboardButton("Назад", callback_data='Назад')
    inline_buttons.append(pay_button)
    inline_buttons.append(back_button)
    return build_menu(inline_buttons, 1)


def create_inline_buttons(start, end, total_number_of_products, button_name, products):
    inline_buttons = [InlineKeyboardButton(button.get('name'), callback_data=button.get('id')) for button in
                      products[start:end]]
    bucket_button = InlineKeyboardButton(f"Корзина.Кол-во продуктов в корзине {total_number_of_products}",
                                         callback_data='Корзина')
    back_button = InlineKeyboardButton(button_name, callback_data=button_name)
    inline_buttons.append(bucket_button)
    inline_buttons.append(back_button)
    return inline_buttons


def get_keyboard(total_number_of_products, products, button_name):
    left = 0
    middle = round(len(products) / 2)
    right = len(products)
    if button_name == 'Назад':
        inline_buttons = create_inline_buttons(middle, right, total_number_of_products, button_name, products)
        return build_menu(inline_buttons, 1)
    elif button_name == 'Вперед':
        inline_buttons = create_inline_buttons(left, middle, total_number_of_products, button_name, products)
        return build_menu(inline_buttons, 1)

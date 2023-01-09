import textwrap

import requests


def get_total_number_of_products(api_token, cart_name):
    ''' Возвращает количество продуктов в крозине'''
    headers = {
        'Authorization': api_token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    products_in_the_cart = response.json()['data']
    number_products_in_cart = len(products_in_the_cart)
    return number_products_in_cart


def get_cart_items(api_token, cart_name):
    ''' Возвращает текст для функции show_bucket() '''
    headers = {
        'Authorization': api_token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    products_in_the_cart = response.json()['data']
    text = [f'''\
            {product['name']}
            {product['description']}
            '''
            for product in products_in_the_cart]

    text.append(get_amount(api_token, cart_name))

    text = ''.join(text)
    text_dedented = textwrap.dedent(text)
    text_width = textwrap.fill(text_dedented, width=14)
    return text_width


def add_product_to_cart(api_token, product_id, amount, cart_name):
    '''Добавляет продукты в корзину'''
    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json',

    }

    body_parameters = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            "quantity": amount,
        }
    }

    response = requests.post(f'https://api.moltin.com/v2/carts/{cart_name}/items',
                             headers=headers,
                             json=body_parameters)
    response.raise_for_status()
    return response.json()


def get_item_id_in_cart(token, product_id, cart_name):
    ''' возвращает уникальный id продукта в корзине он нужен что бы удалить его потом из корзины'''
    headers = {
        'Authorization': token,
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']
    for item in cart_items:
        if item.get('product_id', None) == product_id:
            return item['id']
    return None


def remove_cart_item(token, poduct_id, cart_name):
    ''' Удаляет продукт из коризны'''
    headers = {
        'Authorization': token,
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{cart_name}/items/{poduct_id}',

                               headers=headers)
    response.raise_for_status()


def create_cart(token, customers_token, cart_name):
    ''' Создает корзину'''
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
        'x-moltin-customer-token': customers_token

    }
    body_parameters = {
        'data': {
            'name': cart_name,

        },
    }
    response = requests.post('https://api.moltin.com/v2/carts', headers=headers, json=body_parameters)
    response.raise_for_status()


def get_token_client_credential_token(client_id, client_secret):
    ''' функция для получения API токена '''
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    access_token = decode_response = response.json()['access_token']
    return access_token


def create_customers(token, firstname, lastname, email):
    ''' Создать покупателя'''
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    body_parameters = {
        'data': {
            'type': 'customer',
            'name': f'{firstname} {lastname}',
            'email': email,
            'password': 'mysecretpassword',
        },
    }

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=body_parameters)
    response.raise_for_status()
    return response.json()


def get_product_info(token, product_id):
    ''' Информация о продукте '''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}', headers=headers)
    response.raise_for_status()
    product_info = response.json()
    product_name = product_info['data']['attributes']['name']
    product_description = product_info['data']['attributes']['description']
    photo_id = product_info['data']['relationships']['main_image']['data']['id']
    return product_name, product_description, photo_id


def get_cart_info(token, cart_name):
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}', headers=headers)
    response.raise_for_status()
    cart_info = response.json()
    return cart_info


def get_file_info(token, photo_id):
    ''' Получить ссылку на фото продукта'''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/files/{photo_id}', headers=headers)
    response.raise_for_status()
    photo_info = response.json()
    file_url = photo_info['data']['link']['href']
    return file_url


def get_amount(token, cart_name):
    ''' возвращает общую сумму коризны'''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f"https://api.moltin.com/v2/carts/{cart_name}/", headers=headers)
    response.raise_for_status()
    cart_info = response.json()
    return cart_info['data']['meta']['display_price']['with_tax']['formatted']


def get_all_products(token):
    products = []
    headers = {
        'Authorization': token,
    }
    response = requests.get('https://api.moltin.com/pcm/products', headers=headers).json()
    for product in response['data']:
        item = {'name': product.get('attributes')['name'], 'id': product.get('id')}
        products.append(item)
    return products

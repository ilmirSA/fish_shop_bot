import requests


def get_total_number_of_products(api_token):
    ''' Возвращает количество продуктов в крозине'''
    headers = {
        'Authorization': api_token,
    }

    response = requests.get('https://api.moltin.com/v2/carts/korzinka/items', headers=headers)
    response.raise_for_status()
    decode_response = response.json()['data']
    products_in_the_cart = len(decode_response)
    return products_in_the_cart


def get_cart_items(api_token):
    ''' Возвращает текст для функции show_bucket() '''
    headers = {
        'Authorization': api_token,
    }

    response = requests.get('https://api.moltin.com/v2/carts/korzinka/items', headers=headers)
    response.raise_for_status()
    decode_response = response.json()['data']

    text = [f'''
{item['name']}
{item['description']}\n\n'''
            for item in decode_response]
    text.append(get_amount(api_token))
    return text


def add_product_to_cart(api_token, product_id, amount):
    '''Добавляет продукты в корзину'''
    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json',

    }

    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            "quantity": amount,
        }
    }

    response = requests.post('https://api.moltin.com/v2/carts/korzinka/items',
                             headers=headers,
                             json=data)
    return response.json()


def get_item_id_in_cart(token, product_id):
    ''' возвращает уникальный id продукта в корзине он нужен что бы удалить его потом из корзины'''
    headers = {
        'Authorization': token,
    }
    cart_items = requests.get('https://api.moltin.com/v2/carts/korzinka/items', headers=headers).json()['data']
    for item in cart_items:
        if item.get('product_id', None) == product_id:
            return item['id']
    return None


def remove_cart_item(token, poduct_id):
    ''' Удаляет продукт из коризны'''
    headers = {
        'Authorization': token,
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/korzinka/items/{poduct_id}',

                               headers=headers)
    response.raise_for_status()

def create_cart(api):
    ''' Создает корзину'''
    headers = {
        'Authorization': api,
        'Content-Type': 'application/json',
        'x-moltin-customer-token': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdWIiOiI1NmJlOWU5Ny00OTMxLTQwOGUtYWU5Ni1kODc1YzU0ZDc5N2MiLCJuYW1lIjoidGVzdCB0ZXN0IiwiZXhwIjoxNjcxMjczMjQ3LCJpYXQiOjE2NzExODY4NDcsImp0aSI6IjkyNWM0YjA2LWNiMmItNDY0ZS04ZDU5LWI2NjQ1OGFiYmRmNSJ9.7b0d8898c63bce6e1425480cfb52dff912ddda63a8230344d4d3e51cf6d89ded'
    }
    body = {
        'data': {
            'name': 'korzinka',

        },
    }
    response = requests.post('https://api.moltin.com/v2/carts', headers=headers, json=body)
    response.raise_for_status()

def get_token_client_credential_token(client_id, client_secret):
    ''' функция для получения API токена '''
    data = {
        'client_id': f'{client_id}',
        'client_secret': f'{client_secret}',
        'grant_type': 'client_credentials',
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    decode_response=response.json()
    return decode_response['access_token']


def get_cutomers(api):
    ''' Получить информацию о покупателях '''
    headers = {
        'Authorization': api,

    }

    response = requests.get('https://api.moltin.com/v2/customers', headers=headers)
    decode_response=response.json
    response.raise_for_status
    return decode_response['data'][0]['id']


def customers_token(api):
    ''' Получить токен покупателя'''
    headers = {
        'Authorization': api,

    }

    json_data = {
        'data': {
            'type': 'token',
            'email': 'test@swanson.com',
            'password': 'mysecretpassword',
            "authentication_mechanism": "password"

        },
    }

    response = requests.post('https://api.moltin.com/v2/customers/tokens', headers=headers, json=json_data)
    response.raise_for_status

def get_product_info(token, product_id):
    ''' Информация о продукте '''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/pcm/products/{product_id}', headers=headers)
    response.raise_for_status()
    decode_response = response.json()
    product_name = decode_response['data']['attributes']['name']
    product_description = decode_response['data']['attributes']['description']
    photo_id = decode_response['data']['relationships']['main_image']['data']['id']
    return product_name, product_description, photo_id


def get_file_info(token, photo_id):
    ''' Получить ссылку на фото продукта'''
    headers = {
        'Authorization': token,
    }

    response = requests.get(f'https://api.moltin.com/v2/files/{photo_id}', headers=headers)
    response.raise_for_status()
    decode_response = response.json()
    file_url = decode_response['data']['link']['href']
    return file_url


def create_customers(token, firstname, lastname, email):
    ''' Создать покупателя'''
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    json_data = {
        'data': {
            'type': 'customer',
            'name': f'{firstname} {lastname}',
            'email': f'{email}',
            'password': 'mysecretpassword',
        },
    }

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=json_data)
    response.raise_for_status

def get_amount(token):
    ''' возвращает общую сумму коризны'''
    headers = {
        'Authorization': token,
    }

    response = requests.get("https://api.moltin.com/v2/carts/korzinka/", headers=headers)
    response.raise_for_status
    decode_response = response.json()
    return decode_response['data']['meta']['display_price']['with_tax']['formatted']

print()
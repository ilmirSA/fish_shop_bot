# Что делает
Рыбный магазин телеграмм бот работает через api elasticpath.com

  
  

# Как запустить
Зарегистрируйтесь в [elasticpath.com](https://euwest.cm.elasticpath.com/) и получите `Client ID` и `Client Secret` переименуйте файл `.env.dist` в  `.env`  откройте и вставьте свои значения в
 соответствующие поля.
Создайте в Покупателя и получите его токен и запишите его в файл `env`
1.  [Ссылка](https://lifehacker.ru/kak-sozdat-bota-v-telegram/) на инструкцию как создать телеграмм бота.
2.  Полученный токен бота сохраните в файл `.env` найдите поле `TG_TOKEN` и присвойте ему свой токен.

Для запуска требуется установленный Python версии 3.8 и выше 

  

- Скачайте код;
```
git clone https://github.com/ilmirSA/fish_shop_bot.git
```
- Создайте виртуальное окружение 
```python
python -m venv venv
 ```
- Активируйте виртуальное окружение следующей командой 
 ```python
 source venv/bin/activate
```
- Установите зависимости следующей командой 
```python
pip install -r requirements.txt
```
- Как запустить бота
```python
python3 bot.py
```
Ссылка на [бота](https://t.me/fishmagazinbot) 









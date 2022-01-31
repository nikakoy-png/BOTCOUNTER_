# -*- coding: utf-8 -*-


from settings import *


class OutputFormAge(StatesGroup):
    Output = State()


class OutputFormImage(StatesGroup):
    Output = State()


class OutputFormName(StatesGroup):
    Output = State()


class OutputFormCity(StatesGroup):
    Output = State()


class OutputFormDescription(StatesGroup):
    Output = State()


class OutputFormGetUser(StatesGroup):
    Output = State()


class OutputFormMessage(StatesGroup):
    Output = State()


button1 = KeyboardButton('Я парень', callback_data='man')
button2 = KeyboardButton('Я девушка', callback_data='girl')
button3 = KeyboardButton('Девушки', callback_data='girls')
button4 = KeyboardButton('Парни', callback_data='men')

button5 = KeyboardButton('👎')
button6 = KeyboardButton('❤️')
button7 = KeyboardButton('стоп')

button8 = KeyboardButton('Начать подбор💜')
button9 = KeyboardButton('Анкета❤️')
button10 = KeyboardButton('Статистика📈')

sex = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True).add(
    button1, button2
)

sex_ = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True).add(
    button3, button4
)

menu_choose = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    button5, button6, button7
)

menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    button8, button9, button10
)

bot = Bot(token=KEY_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())


def create_fidback_ford(telegram_id):
    like = InlineKeyboardButton(text='❤️', callback_data=f'btn_{telegram_id}')
    fidback_bar = InlineKeyboardMarkup(row_width=1)
    fidback_bar.insert(like)
    return fidback_bar


@dp.message_handler(commands=['start'])
async def register_point(message):
    await bot.send_message(message.from_user.id, """Уже миллионы людей знакомятся в нашем боте 😍\n\n
                                                Я помогу найти тебе пару или просто друзей 👫"""
                           )
    if db.get_user(str(message.from_user.id)) is None:
        db.register_new_user(message.from_user.id, message.from_user.username)
        await bot.send_message(message.from_user.id, "Определимся с полом", reply_markup=sex)
    else:
        await bot.send_message(message.from_user.id, "Вы уже являетесь пользователем нашего бота!", reply_markup=menu)


@dp.message_handler(commands=['send_message'])
async def send_message(message):
    user = db.get_user(message.from_user.id)
    if user['status'] == 'Admin':
        await bot.send_message(message.from_user.id, 'Отправьте сообщение')
        await OutputFormMessage.Output.set()


@dp.message_handler(commands=['get_user'])
async def get_user(message):
    user = db.get_user(message.from_user.id)
    if user['status'] == 'Admin':
        await bot.send_message(message.from_user.id, 'Отправьте айди пользователя')
        await OutputFormGetUser.Output.set()


async def send_from_user(id_user):
    found_user = db.get_user(db.get_pair(id_user))
    if not found_user:
        await bot.send_message(id_user, "К сожалению, анкеты закончились, приходите позже!")
    else:
        try:
            await bot.send_photo(id_user, open(found_user['photo'], 'rb'),
                                 caption=f"Имя: {found_user['name']}\nПол: {found_user['sex']}"
                                         f"\nВозраст: {found_user['age']}\nГород: {found_user['city']}"
                                         f"\nО себе: {found_user['description']}")
            db.increment_row(found_user['id'], 'views')
        except Exception:
            await send_from_user(id_user)


@dp.message_handler(content_types=['text'])
async def get_text_massage(message: types.Message):
    if message.text == 'Я парень':
        db.set_value(message.from_user.id, 'sex', 'Парень')
        await bot.send_message(message.from_user.id, "Кто тебе интересен?", reply_markup=sex_)
    elif message.text == 'Я девушка':
        db.set_value(message.from_user.id, 'sex', 'Девушка')
        await bot.send_message(message.from_user.id, "Кто тебе интересен?", reply_markup=sex_)
    elif message.text == '👎':
        db.off_active_seek(message.from_user.id)
        await send_from_user(message.from_user.id)
    elif message.text == 'Анкета❤️':
        user = db.get_user(message.from_user.id)
        if user['status'] == 'User' or user['status'] == 'Admin':
            await bot.send_photo(message.from_user.id, open(user['photo'], 'rb'),
                                 caption=f"Ваша анкета:\n\nИмя: {user['name']}\nПол: {user['sex']}"
                                         f"\nИнтересуют: {user['interesting']}\n"
                                         f"Возраст: {user['age']}\n"
                                         f"\nО себе: {user['description']}")
    elif message.text == 'стоп':
        user = db.get_user(message.from_user.id)
        if user['status'] == 'User' or user['status'] == 'Admin':
            await bot.send_message(message.from_user.id, 'Удачи ❤️', reply_markup=menu)
    elif message.text == 'Статистика📈':
        user = db.get_user(message.from_user.id)
        if user['status'] == 'User' or user['status'] == 'Admin':
            await bot.send_message(message.from_user.id, f"СТАТИСТИКА📈\n\n\n"
                                                         f"Лайков на твоей анкете: {user['like']}\n"
                                                         f"Просмотров твоей анкеты: {user['views']}\n"
                                                         f"Взаимных лайков: {user['mutual']}\n", reply_markup=menu)
    elif message.text == 'Девушки':
        db.set_value(message.from_user.id, 'interesting', 'Девушки')
        await bot.send_message(message.from_user.id, "Введите свой возраст")
        await OutputFormAge.Output.set()
    elif message.text == 'Парни':
        db.set_value(message.from_user.id, 'interesting', 'Парни')
        await bot.send_message(message.from_user.id, "Введите свой возраст")
        await OutputFormAge.Output.set()
    elif message.text == 'Начать подбор💜':
        user = db.get_user(message.from_user.id)
        if user['status'] == 'User' or user['status'] == 'Admin':
            await bot.send_message(message.from_user.id, "Отлично!\n\n"
                                                         "Нажми '👎', если тебе кто то понравился\n"
                                                         "Нажми '❤️', чтоб продолжить поиск\n",
                                   reply_markup=menu_choose)
            await send_from_user(message.from_user.id)
    elif message.text == '❤️':
        user = db.get_user(message.from_user.id)
        if user['status'] == 'User' or user['status'] == 'Admin':
            id_found_user = db.get_active_seek(message.from_user.id)
            await bot.send_message(message.from_user.id, 'Отлично!\nЖдем ответа найденного пользователя!❤️')
            await bot.send_photo(id_found_user, open(user['photo'], 'rb'),
                                 caption=f"Имя: {user['name']}\nПол: {user['sex']}"
                                         f"\nВозраст: {user['age']}\nГород: {user['city']}"
                                         f"\nО себе: {user['description']}",
                                 reply_markup=create_fidback_ford(message.from_user.id))
            print(f"{message.from_user.id} лайкнула {id_found_user}")
            await bot.send_message(int(db.get_id_admin()), f"{message.from_user.id} лайкнула {id_found_user}")
            await send_from_user(message.from_user.id)
            db.increment_row(id_found_user, 'views')
            db.increment_row(id_found_user, 'like')
            db.like_active_seek(message.from_user.id)
        await send_from_user(message.from_user.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
async def fidback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    found_user = db.get_user(int(callback_query.data.replace('btn_', '')))
    await bot.send_photo(callback_query.from_user.id, open(found_user['photo'], 'rb'),
                         caption=f"Поздравляю, у вас взаимная симпатия с этим пользователем!\n\n"
                                 f"Телегам пользователя: @{found_user['login']}\n")
    simple_user = db.get_user(callback_query.from_user.id)
    await bot.send_photo(int(callback_query.data.replace('btn_', '')), open(simple_user['photo'], 'rb'),
                         caption=f"Поздравляю, у вас взаимная симпатия с этим пользователем!\n\n"
                                 f"Телегам пользователя: @{simple_user['login']}\n")
    db.ok_active_seek(simple_user['id'], found_user['id'])
    db.increment_row(int(callback_query.data.replace('btn_', '')), 'mutual')
    db.increment_row(callback_query.from_user.id, 'mutual')
    print(f"{callback_query.from_user.id} взаимно лайкнула {int(callback_query.data.replace('btn_', ''))}")
    await bot.send_message(int(db.get_id_admin()), f"{callback_query.from_user.id} взаимно лайкнула"
                                                   f" {int(callback_query.data.replace('btn_', ''))}")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormAge.Output)
async def process_age(message: types.Message, state: FSMContext):
    Output = message.text
    db.set_value(message.from_user.id, 'age', Output)
    await state.finish()
    await bot.send_message(message.from_user.id, "Введите свое имя")
    await OutputFormName.Output.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormName.Output)
async def process_name(message: types.Message, state: FSMContext):
    Output = message.text
    db.set_value(message.from_user.id, 'name', Output)
    await state.finish()
    await bot.send_message(message.from_user.id, "Откуда вы?")
    await OutputFormCity.Output.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormCity.Output)
async def process_name(message: types.Message, state: FSMContext):
    Output = message.text
    db.set_value(message.from_user.id, 'city', Output)
    await state.finish()
    await bot.send_message(message.from_user.id, "Напишите пару слов о себе.\n"
                                                 "Это поможет вам найти человека близкого по интересам")
    await OutputFormDescription.Output.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormDescription.Output)
async def process_name(message: types.Message, state: FSMContext):
    Output = message.text
    db.set_value(message.from_user.id, 'description', Output)
    await state.finish()
    await bot.send_message(message.from_user.id, "Пришлите ваше фото")
    await OutputFormImage.Output.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormGetUser.Output)
async def process_name(message: types.Message, state: FSMContext):
    Output = message.text
    user = db.get_user(int(Output))
    await bot.send_photo(message.from_user.id, open(user['photo'], 'rb'),
                         caption=f"'id': {user['id']}\n"
                                 f"'login': {user['login']}\n"
                                 f"'description': {user['description']}\n"
                                 f"'views': {user['views']}\n"
                                 f"'city': {user['city']}\n"
                                 f"'photo': {user['photo']}\n"
                                 f"'mutual': {user['mutual']}\n"
                                 f"'sex': {user['sex']}\n"
                                 f"'age': {user['age']}\n"
                                 f"'interesting': {user['interesting']}\n"
                                 f"'name': {user['name']}\n"
                                 f"'id': {user['status']}\n"
                         )
    await state.finish()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormMessage.Output)
async def process_name(message: types.Message, state: FSMContext):
    Output = message.text
    for x in db.get_all_user():
        try:
            await bot.send_message(x, str(Output))
        except Exception:
            continue

    await state.finish()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(state=OutputFormImage.Output, content_types=['photo'])
async def process_img(message, state: FSMContext):
    try:
        file_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        src = filepath + f'{message.from_user.id}.png'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())
        await bot.send_message(message.from_user.id, "Фото добавлено")
        db.set_value(message.from_user.id, 'photo', src)
        db.set_value(message.from_user.id, 'status', "User")
        await bot.send_message(message.from_user.id, "Вы успешно прошли регистрацию, спасибо!\n"
                                                     "Вы можете проверить свою анкету нажав на кнопку 'Анкета' ",
                               reply_markup=menu)
        await state.finish()
        await bot.send_message(int(db.get_id_admin()), f'successfull register {message.from_user.id}')
        user = db.get_user(message.from_user.id)
        await bot.send_photo(int(db.get_id_admin()), open(user['photo'], 'rb'),
                             caption=f"'id': {user['id']}\n"
                                     f"'login': {user['login']}\n"
                                     f"'description': {user['description']}\n"
                                     f"'views': {user['views']}\n"
                                     f"'city': {user['city']}\n"
                                     f"'photo': {user['photo']}\n"
                                     f"'mutual': {user['mutual']}\n"
                                     f"'sex': {user['sex']}\n"
                                     f"'age': {user['age']}\n"
                                     f"'interesting': {user['interesting']}\n"
                                     f"'name': {user['name']}\n"
                                     f"'id': {user['status']}\n"
                             )
    except telebot.apihelper.ApiException as e:
        await bot.send_message(message.from_user.id, e)
        await state.finish()

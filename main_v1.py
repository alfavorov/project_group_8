from multiprocessing.sharedctypes import Value
from GraphVisualizer import GraphVisualizer
from DataFrameContainer import DataFrameContainer
from Configurator import ConcreteConfigurator

# Инициализация бота
import telebot, os, json, requests, datetime
from telebot.types import KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto

from tg_token import token



class Main:

    def __init__(self, token: str) -> None:
        self.tg_token = token
        self.tg_bot = telebot.TeleBot(token)
        self.tg_users = {}
        self.main_dir = os.getcwd() + '/data/'

        try:
            os.mkdir(self.main_dir)
        except Exception as err:
            self.log_w(None, '__init__',  err)

    def log_w(self, user_id, function, txt: str):
        msg = f'{str(datetime.datetime.now())}, {function}, {user_id}: {txt}\n'
        with open('log.txt', 'a') as f:
            f.write(msg)


    def generate_button(self, value, data):
        if data is None: return

        return telebot.types.InlineKeyboardButton(
            data['title'],
            callback_data=json.dumps({'value': value, 'command': data.get('command', None)})
        )

    def generate_buttons(self, items, layout):
        markup = telebot.types.InlineKeyboardMarkup()

        for row in layout:
            if type(row) is not list:
                row = [row]

            buttons = list(filter(bool, [self.generate_button(key, items[key]) for key in row]))
            markup.row(*buttons, )

        return markup

    def user_dir(self, user_id):
        return f'{self.main_dir}{user_id}/'

    def get_users_files(self, user_id: int):
        ''' Получение списка файлов, загруженных пользователем '''
        user_files_path = self.user_dir(user_id)

        try:
            all_files = list(os.listdir(user_files_path))
            files = []
            for i in all_files:
                if i[0] != '.' and i.count('.') == 1:
                    files.append(i)

            if len(files) == 0:
                raise Exception('Файлов нет.')
            else:
                return {'keybord': self.get_keybord(files),
                        'data': files,
                        'status': 1}
        except Exception as err:
            return {'status': 0,
                    'keybord': None}

    def get_keybord(self, my_list):
        ''' Клавиатура с произвольными данными'''

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        if type(my_list) == list:
            for i in my_list:
                keyboard.row(KeyboardButton(i))

        return keyboard

    def send_msg(self, data, user_id: int, keybord=None, markdown=False):
        ''' Отправить сообщение '''

        if type(data) != str:
            data = '\n'.join(data)

        return self.tg_bot.send_message(user_id,
                                 data,
                                 reply_markup=keybord or ReplyKeyboardRemove(),
                                 parse_mode='Markdown' if markdown else None,
                                 )

    def show_menu(self, user_id):
        bot = self.tg_bot

        users = self.tg_users
        configurator = users[user_id]['configurator']
        last_message = users[user_id]['last_message']
        last_photo_message = users[user_id]['last_photo_message']
        current_menu_page = configurator.current_menu_page
        text = current_menu_page['title'] + ':'
        photo = None
        reply_markup = self.generate_buttons(current_menu_page.get('items', []), current_menu_page.get('layout', []))

        if users[user_id].get('loading_message', None) is not None:
            bot.delete_message(user_id, users[user_id]['loading_message'].message_id)
            users[user_id]['loading_message'] = None

        if users[user_id].get('error_message', None) is not None:
            bot.delete_message(user_id, users[user_id]['error_message'].message_id)
            users[user_id]['error_message'] = None

        if current_menu_page.get('show_graph', None) is not None:
            photo = self.make_graph_photo(user_id)

        if photo is not None:
            with open(photo, 'rb') as img:
                if last_photo_message:
                    # TODO: если график не изменился, то падает ошибка, стоит присмотреться, если нечего будет делать
                    try:
                        bot.edit_message_media(telebot.types.InputMediaPhoto(img), user_id,
                                               last_photo_message.message_id)
                    except Exception as err:
                        self.log_w(user_id, 'show_menu', err)
                else:
                    if last_message:
                        bot.delete_message(user_id, last_message.message_id)
                        last_message = None
                    last_photo_message = bot.send_photo(user_id, img)
        elif last_photo_message:
            bot.delete_message(user_id, last_photo_message.message_id)
            last_photo_message = None

        if last_message is not None:
            bot.edit_message_text(text, user_id, last_message.message_id, reply_markup=reply_markup)
        else:
            last_message = bot.send_message(user_id, text, reply_markup=reply_markup)

        configurator_wait_input = False
        if current_menu_page.get('type', None) in ['int', 'float', 'str']:
            configurator_wait_input = True

        users[user_id]['last_message'] = last_message
        users[user_id]['last_photo_message'] = last_photo_message
        users[user_id]['waiting_for_input'] = configurator_wait_input

    def make_graph_photo(self, user_id):
        data = None
        figure = None
        photo = None
        users = self.tg_users
        config = users[user_id]['configurator'].config
        df_container = users[user_id]['df_container']
        visualizer = users[user_id]['visualizer']

        if config['graph_type'] == 'bar':
            data = df_container.make_bar_data(config)
            figure = visualizer.make_bar_plot(data, title=config['graph_title'], **config)
        elif config['graph_type'] == 'scatter':
            data = df_container.make_scatter_data(config)
            figure = visualizer.make_scatter_plot(data, title=config['graph_title'], **config)
        elif config['graph_type'] == 'hist':
            data = df_container.make_hist_data(config)
            figure = visualizer.make_hist_plot(data, title=config['graph_title'], **config)
        elif config['graph_type'] == 'pie':
            data = df_container.make_pie_data(config)
            figure = visualizer.make_pie_chart(data['y'], labels=data['x'], title=config['graph_title'], **config)

        my_dir = self.user_dir(user_id) + 'tmp/'

        if not os.path.exists(my_dir):
            os.makedirs(my_dir)

        photo = my_dir + 'cur_graph.png'
        figure.savefig(photo)

        return photo

    def send_or_update(self, user_id):
        users = self.tg_users
        bot = self.tg_bot

        try:
            self.show_menu(user_id)
        except Exception as err:
            self.log_w(user_id, 'send_or_update', err)
            error_text = 'Что-то пошло не так, попробуйте снова.'
            if users[user_id]['last_photo_message']:
                bot.delete_message(user_id, users[user_id]['last_photo_message'].message_id)
            if users[user_id]['last_message']:
                bot.edit_message_text(error_text, user_id, users[user_id]['last_message'].message_id)
            else:
                users[user_id]['last_message'] = bot.send_message(user_id, error_text)

            users[user_id]['last_message'] = None
            users[user_id]['last_photo_message'] = None
            users[user_id]['configurator'].go_back()
            self.show_menu(user_id)

    def start(self, user_id):
        bot = self.tg_bot
        users = self.tg_users

        if 'last_message' in users[user_id] and users[user_id]['last_message'] is not None:
            bot.delete_message(user_id, users[user_id]['last_message'].message_id)

        users[user_id]['last_message'] = None
        users[user_id]['last_photo_message'] = None
        users[user_id]['configurator'] = None
        users[user_id]['df_container'] = None
        users[user_id]['visualizer'] = GraphVisualizer()
        users[user_id]['waiting_for_input'] = False

        if users[user_id]['state'] == -1:
            reply_msg = ["Добрый день!",
                            "Я бот-строитель, помогу вам создать графики опираясь на нужные данные.", ]
        else:
            reply_msg = ["Спасибо, что вы ещё с нами :)", ]
        reply_msg += ["Вы можете загрузите свои данные или воспользоваться уже имеющимися.", '', ]

        users[user_id]['state'] = 0


        users_files = self.get_users_files(user_id)

        if users_files['status'] == 0:
            reply_msg.append("Пришлите свой первый файл :)")
        else:
            reply_msg.append("Пришлите новый файл, выберите файл из списка уже загруженных, пришлите ссылку на файл или напишите /test, для загрузки тестовый данных (kiva_loans.csv):")
            users[user_id]['files'] = users_files['data'].copy()

        self.send_msg(reply_msg, user_id, users_files['keybord'])

    def next_graph(self, user_id):
        bot = self.tg_bot
        users = self.tg_users

        users[user_id]['configurator'].reset()

        if users[user_id]['last_message']:
            bot.delete_message(user_id, users[user_id]['last_message'].message_id)
            users[user_id]['last_message'] = None
        # чтобы не удалился готовый график
        users[user_id]['last_photo_message'] = None

        self.send_or_update(user_id)

    def processing(self) -> None:
        ''' Обработка сообщений боту '''

        bot = self.tg_bot
        users = self.tg_users

        @bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            user_id = message.from_user.id
            msg_mtm = message.text
            msg_id = message.message_id

            if user_id not in users:
                # Франение информации о каждом юзере
                users[user_id] = {'state': -1,  # Статус пользвателя
                                    'files': [],  # Все файлы, которые загрузил пользватель
                                }

                # Новый пользователь либо перезапуск бота
            if message.text in ["/start", "/help"] or users[user_id]['state'] == -1:
                # Старт. Выбор файла
                self.start(user_id)

            # Пользователь выбрал файл из имеющихся
            if users[user_id]['state'] == 0 and (msg_mtm in users[user_id]['files'] or msg_mtm.count('.') >= 2 or msg_mtm=='/test'):
                users[user_id]['loading_message'] = self.send_msg('Отличный выбор! :)\nПожалуйста, чуть подождите, идет загрузка...', user_id)

                try:
                    if msg_mtm == '/test':
                        cur_file = '/Users/alex/PycharmProjects/SkillBox/project_group_8/test_data/kiva_loans.csv'

                    elif msg_mtm not in users[user_id]['files']:
                        url = msg_mtm
                        r = requests.get(url)
                        cur_file = self.user_dir(user_id) + str(url.split('/')[-1])

                        # Валидация файла
                        with open(cur_file, 'wb') as f:
                            f.write(r.content)

                        valid = DataFrameContainer.validate_csv(cur_file)
                        if valid:
                            self.send_msg('Данные загружены!', message.from_user.id)
                        else:
                            os.remove(cur_file)
                            self.send_msg('К сожалению файл не валиден... Попробуйте снова.', message.from_user.id)



                    else:
                        cur_file = self.user_dir(user_id) + '/' + str(msg_mtm)

                    users[user_id]['df_container'] = DataFrameContainer(cur_file)
                    users[user_id]['configurator'] = ConcreteConfigurator(users[user_id]['df_container'])
                    users[user_id]['configurator'].set_file_name(msg_mtm)

                    users[user_id]['state'] = 1

                    self.send_or_update(user_id)
                except Exception as err:
                    self.send_msg(f'Не удалось загрузить файл... Пожалуйста, попробуйте ещё раз: /start', user_id)
                    self.log_w(user_id, 'get_text_messages', err)


            if users[user_id]['waiting_for_input'] == True:
                bot.delete_message(user_id, msg_id)
                # удаляю всегда, т. к. из-за ReplyKeyboardRemove проблема с редактированием простого текстового сообщения
                # https://github.com/eternnoir/pyTelegramBotAPI/issues/1104
                if users[user_id].get('error_message', None) is not None:
                    bot.delete_message(user_id, users[user_id]['error_message'].message_id)
                    users[user_id]['error_message'] = None

                try:
                    users[user_id]['configurator'].update_menu_state(message.text)
                    users[user_id]['waiting_for_input'] = False
                    self.send_or_update(user_id)
                except ValueError as err:
                    users[user_id]['error_message'] = self.send_msg(str(err), user_id)

        # Обработка команд (кнопок)
        @bot.callback_query_handler(func=lambda call: True)
        def get_callback(call):
            user_id = call.from_user.id
            selected_data = json.loads(call.data)
            is_done = None
            command = None

            if users[user_id].get('error_message', None) is not None:
                bot.delete_message(user_id, users[user_id]['error_message'].message_id)
                users[user_id]['error_message'] = None

            try:
                is_done, command = users[user_id]['configurator'].update_menu_state(selected_data['value'], selected_data['command'])
            except ValueError as err:
                self.log_w(user_id, 'get_callback_value_error', err)
                users[user_id]['error_message'] = self.send_msg(str(err), user_id)
                return
            except Exception as err:
                self.log_w(user_id, 'get_callback_other', err)
                return

            if is_done:
                self.next_graph(user_id)
            elif command == 'change_file':
                self.start(user_id)
            else:
                bot.edit_message_text(users[user_id]['last_message'].text + ' обработка...', user_id,
                                        users[user_id]['last_message'].message_id)
                self.send_or_update(user_id)

        # Обработка присланных файлов
        @bot.message_handler(content_types=['document'])
        def handle_docs(message):
            user_id = message.from_user.id
            msg_mtm = message.text

            if user_id in users and users[user_id]['state'] == 0:
                try:
                    self.send_msg('Загрузка и проверка...', message.from_user.id)
                    file_info = bot.get_file(message.document.file_id)
                    downloaded_file = bot.download_file(file_info.file_path)

                    user_dic = self.user_dir(user_id)
                    try:
                        os.mkdir(user_dic)
                    except Exception as err:
                        self.log_w(user_id, 'handle_docs', err)

                    file_name = message.document.file_name
                    src = user_dic + file_name
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file)

                    #  Проверка файла на валидность

                    valide = DataFrameContainer.validate_csv(src)

                    if valide:
                        self.send_msg('Успешно!', message.from_user.id)
                        cur_file = src
                        users[user_id]['df_container'] = DataFrameContainer(cur_file)
                        users[user_id]['configurator'] = ConcreteConfigurator(users[user_id]['df_container'])
                        users[user_id]['configurator'].set_file_name(file_name)

                        users[user_id]['state'] = 1

                        self.send_or_update(user_id)
                    else:
                        os.remove(src)
                        self.send_msg('К сожалению файл не валиден... Попробуйте снова.', message.from_user.id)
                except Exception as err:
                    self.send_msg(f'Ошибка загрузки :(', message.from_user.id)
                    self.log_w(message.from_user.id, 'handle_docs', err)
            else:
                self.send_msg('Если вы хотите отправить новый файл, вернитесь к этапу выбора файла: /start',
                              message.from_user.id)

    def run_bot(self) -> None:
        ''' Запусить бот '''
        # дважды стартуешь бота?
        self.processing()
        # self.tg_bot.polling(none_stop=True)

        # вот тут второй раз в отдельном потоке?
        def th():
            self.tg_bot.polling(none_stop=True)

        import threading
        my_thread = threading.Thread(target=th)
        my_thread.start()


if __name__ == '__main__':
    interface = Main(token)

    interface.log_w(None, '__main__', 'Server started')

    interface.run_bot()

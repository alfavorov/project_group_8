from GraphVisualizer import GraphVisualizer
from DataFrameContainer import DataFrameContainer
from Configurator import ConcreteConfigurator, BaseConfigurator

# Инициализация бота
import telebot, os, json
from typing import Any
from telebot.types import KeyboardButton, ReplyKeyboardRemove, InputMedia, InputMediaPhoto

token = '5226703033:AAEC2VNvrB9A7ZuRuEYwbflag3qNEKMeUtg'


class Main:
    def __init__(self, token: str) -> None:
        self.tg_token = token
        self.tg_bot = telebot.TeleBot(token)
        self.tg_users = {}
        self.main_dir = os.getcwd() + '/data/'

        try:
            os.mkdir(self.main_dir)
        except:
            pass

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
            markup.row(*buttons)

        return markup

    def get_users_files(self, user_id: int):
        ''' Получение списка файлов, загруженных пользователем '''

        user_files_path = f'{self.main_dir}/{user_id}/'
        try:
            all_files = list(os.listdir(user_files_path))
            files = []
            for i in all_files:
                if i[0] != '.':
                    files.append(i)

            if len(files) == 0:
                raise Exception('Файлов нет.')
            else:
                return {'keybord': self.get_keybord(files),
                        'data': files,
                        'status': 1}
        except:
            return {'status': 0,
                    'keybord': None}
            # return {'msg': 'Вы ещё не загружали файлы, пожалуйста, загрузите новый.'}

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

        self.tg_bot.send_message(user_id,
                                 data,
                                 reply_markup=keybord or ReplyKeyboardRemove(),
                                 parse_mode='Markdown' if markdown else None,
                                 )

    def show_menu(self, user_id, configurator, df_container, visualizer, last_message=None, last_photo_message=None):
        bot = self.tg_bot

        current_menu_page = configurator.current_menu_page
        text = current_menu_page['title'] + ':'
        photo = None
        reply_markup = self.generate_buttons(current_menu_page.get('items', []), current_menu_page.get('layout', []))

        if current_menu_page.get('show_graph', None) is not None:
            config = configurator.config
            data = None
            figure = None

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

            # TODO: настроить пути для каждого пользователя отдельно
            ph = 'test_data/tmp/test.png'
            figure.savefig(ph)
            photo = ph

        if photo is not None:
            with open(photo, 'rb') as img:
                if last_photo_message:
                    # TODO: если график не изменился, то падает ошибка, стоит присмотреться, если нечего будет делать
                    try:
                        bot.edit_message_media(telebot.types.InputMediaPhoto(img), user_id,
                                               last_photo_message.message_id)
                    except:
                        pass
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

        if current_menu_page.get('type', None) in ['int', 'float', 'str']:
            global configurator_wait_input
            configurator_wait_input = True

        return last_message, last_photo_message

    def send_choice(self, user_id: int):  # Не искользуется
        # ''' Отправить пользователю возможные зависимости графика'''
        #
        # ans = 'Выберите, какой график вы хотите построить?\n\n'
        # # count = 1
        # # for i in graphs_types:
        # #     ans += f'{count}. {graphs_types[i]} (/graph\_{i}).\n'
        # #     count += 1
        #
        # self.send_msg(ans, user_id, markdown=True)
        pass

    def send_or_update(self, user_id):
        users = self.tg_users

        self.show_menu(
            user_id,
            users[user_id]['configurator'],
            users[user_id]['df_container'],
            users[user_id]['visualizer'],
            users[user_id]['last_message'],
            users[user_id]['last_photo_message'],
        )

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
                users[user_id]: str[Any] = {'state': -1,  # Статус пользвателя
                                            'files': [],  # Все файлы, которые загрузил пользватель
                                            'cur_file': '',
                                            }

                # Новый пользователь либо перезапуск бота
            if message.text in ["/start", "/help"] or users[user_id]['state'] == -1:
                users[user_id]['cur_file'] = ''  # Файл, с которым сейчас работает пользватель
                users[user_id]['last_message'] = None
                users[user_id]['last_photo_message'] = None
                users[user_id]['df_container'] = DataFrameContainer('test_data/kiva_loans.csv')
                users[user_id]['configurator'] = ConcreteConfigurator(users[user_id]['df_container'].get_columns())
                users[user_id]['visualizer'] = GraphVisualizer()

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
                    reply_msg.append("Пришлите новый файл, или выберите файл из списка уже загруженных:")
                    users[user_id]['files'] = users_files['data'].copy()

                self.send_msg(reply_msg, user_id, users_files['keybord'])

            # Пользователь выбрал файл из имеющихся
            if users[user_id]['state'] == 0 and msg_mtm in users[user_id]['files']:
                self.send_msg('Отличный выбор! :)', user_id)

                users[user_id]['cur_file'] = self.main_dir + str(user_id) + '/' + str(msg_mtm)
                users[user_id]['state'] = 1

                self.send_or_update(user_id)

            # Ожидание графика
            if users[user_id]['state'] == 1 and '/graph_' in msg_mtm:
                try:
                    type_of_graph = msg_mtm.split('_')[-1]

                    if type_of_graph not in graphs_types:
                        raise Exception("Такого варианта нет.")

                    dependency_name = graphs_types[type_of_graph]

                    # Тут будет осуществлятся запрос построения графика
                    #######
                    src = '/content/tmp/1.jpg' if type_of_graph % 2 == 0 else '/content/tmp/2.jpg'
                    # Тут будет осуществлятся запрос построения графика

                    with open(src, 'rb') as img:
                        if users[user_id]['last_grapf_msg_id'] == -1:  # TODO Убрать
                            senden_msg = bot.send_photo(user_id, img, caption=dependency_name)
                            users[user_id]['last_grapf_msg_id'] = senden_msg.message_id  # TODO Убрать
                            self.send_msg('Чтобы вернуться к выбору файла перезапустите бот: /start', user_id)
                        else:
                            bot.edit_message_media(InputMediaPhoto(media=img, caption=dependency_name), chat_id=user_id,
                                                   message_id=users[user_id]['last_grapf_msg_id'])  # TODO Убрать
                    bot.delete_message(user_id, msg_id)

                except Exception as err:
                    self.send_msg('Ошибка при построении графика :(\n' + str(err), user_id)

        # Обработка команд (кнопок)
        @bot.callback_query_handler(func=lambda call: True)
        def get_callback(call):
            try:
                user_id = call.from_user.id
                selected_data = json.loads(call.data)

                users[user_id]['configurator'].update_menu_state(selected_data['value'], selected_data['command'])

                self.send_or_update(user_id)
            except Exception as err:
                print('Error: ', str(err))

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

                    user_dic = self.main_dir + str(user_id) + '/'
                    try:
                        os.mkdir(user_dic)
                    except:
                        pass

                    src = user_dic + message.document.file_name;
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file)

                    # Тут будет проверка файла на валидность
                    valide = True
                    # Тут будет проверка файла на валидность

                    if valide:
                        self.send_msg('Успешно!', message.from_user.id)
                        users[user_id]['cur_file'] = src
                        users[user_id]['state'] = 1

                        self.send_or_update(user_id)
                    else:
                        os.remove(src)
                        self.send_msg('К сожалению файл не валиден... Попробуйте снова.', message.from_user.id)
                except:
                    self.send_msg('Ошибка загрузки :(', message.from_user.id)
            else:
                self.send_msg('Если вы хотите отправить новый файл, вернитесь к этапу выбора файла: /start',
                              message.from_user.id)

    def run_bot(self) -> None:
        ''' Запусить бот '''
        self.processing()
        self.tg_bot.polling(none_stop=True)

        def th(): self.tg_bot.polling(none_stop=True)

        import threading
        my_thread = threading.Thread(target=th)
        my_thread.start()


if __name__ == '__main__':
    interface = Main(token)
    interface.run_bot()

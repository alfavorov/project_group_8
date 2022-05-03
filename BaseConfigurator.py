class BaseConfigurator:
    def __init__(self, columns):
        self.columns = columns
        self.commands = ['back', 'reset', 'finish']
        self.reset()

    def reset(self):
        self.config = dict()
        self.soft_reset()

    def soft_reset(self):
        self.is_done = False
        self.menu_history = ['root']
        self.current_menu_page = None
        self.update_menu_structure()

    def update_menu_structure(self):
        self.menu_structure = self.make_menu_structure()

        current_menu_page = self.menu_structure

        for page in self.menu_history:
            current_menu_page = current_menu_page['items'][page]

        self.current_menu_page = current_menu_page

    def update_menu_state(self, value, command=None):
        if command in self.commands:
            self.call_command(command)
            return self.is_done, command

        page_type = self.current_menu_page.get('type', None)

        if page_type == 'category':
            self.menu_history.append(value)
            self.update_menu_structure()
        elif page_type == 'select':
            self.select(value)
        elif page_type == 'int':
            self.set_int(value)
        elif page_type == 'float':
            self.set_float(value)
        elif page_type == 'str':
            self.set_str(value)

        return self.is_done, command

    def call_command(self, command):
        if command == 'back':
            self.go_back()
        elif command == 'reset':
            self.reset()
        elif command == 'finish':
            self.finish()

    def finish(self):
        self.is_done = True

    def select(self, value):
        current_item = self.menu_history[-1]

        if value == 'None':
            value = None

        if value == 'True':
            value = True

        if value == 'False':
            value = False

        self.config[current_item] = value

        self.go_back()

    def set_int(self, value):
        current_menu_page_id = self.menu_history[-1]
        current_menu_page_type = self.current_menu_page.get('type', None)

        if current_menu_page_type != 'int':
            raise TypeError('TODO')

        if value == 'None':
            value = None
        else:
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f'Значение "{value}" невозможно использовать как целое число')

        self.config[current_menu_page_id] = value
        self.go_back()

    def set_str(self, value):
        current_menu_page_id = self.menu_history[-1]
        current_menu_page_type = self.current_menu_page.get('type', None)

        if current_menu_page_type != 'str':
            raise TypeError('TODO')

        if value == 'None':
            value = None
        else:
            try:
                value = str(value)
            except ValueError:
                raise ValueError(f'Значение "{value}" невозможно использовать как строку')

        self.config[current_menu_page_id] = value
        self.go_back()

    def set_float(self, value):
        current_menu_page_id = self.menu_history[-1]
        current_menu_page_type = self.current_menu_page.get('type', None)

        if current_menu_page_type != 'float':
            raise TypeError('TODO')

        if value == 'None':
            value = None
        else:
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f'Значение "{value}" невозможно использовать как дробное число')

        self.config[current_menu_page_id] = value
        self.go_back()

    def go_back(self):
        if len(self.menu_history) > 1:
            self.menu_history.pop()
            self.update_menu_structure()

    def make_menu_structure(self):
        return {
            'items': {
                'root': {
                    'items': []
                }
            }
        }

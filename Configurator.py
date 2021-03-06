from BaseConfigurator import BaseConfigurator
from pandas.api.types import is_numeric_dtype

class ConcreteConfigurator(BaseConfigurator):
    def __init__(self, df_container):
        self.df_container = df_container
        self.columns = df_container.get_columns()
        self.file_name = None
        super().__init__()
        self.commands.append('change_file')

    def set_file_name(self, file_name):
        self.file_name = file_name
        self.update_menu_structure()

    def update_menu_state(self, value, command=None):
        current_menu_page_id = self.menu_history[-1]
        current_menu_page_type = self.current_menu_page.get('type', None)

        if current_menu_page_type == 'category' and current_menu_page_id == 'root':
            self.config = self.make_default_config(value)

        if command == 'validate':
            is_valid, error_text = self.validate(current_menu_page_id)
            if is_valid is False:
                raise ValueError(error_text)

        return super().update_menu_state(value, command)

    def make_default_config(self, graph_type):
        if graph_type == 'bar':
            return self.make_bar_default_config()
        elif graph_type == 'hist':
            return self.make_hist_default_config()
        elif graph_type == 'pie':
            return self.make_pie_default_config()
        elif graph_type == 'scatter':
            return self.make_scatter_default_config()

    def validate(self, graph_type):
        if graph_type == 'bar':
            return self.validate_bar()
        elif graph_type == 'hist':
            return self.validate_hist()
        elif graph_type == 'pie':
            return self.validate_pie()
        elif graph_type == 'scatter':
            return self.validate_scatter()

    def make_menu_structure(self):
        return {
            'items': {
                'root': {
                    'title': f'Файл: {self.file_name}\nВыберите тип графика',
                    'type': 'category',
                    'items': {
                        'bar': self.make_bar_menu_structure(),
                        'hist': self.make_hist_menu_structure(),
                        'scatter': self.make_scatter_menu_structure(),
                        'pie': self.make_pie_menu_structure(),
                        'change_file': {'title': 'Сменить рабочий файл', 'command': 'change_file'}
                    },
                    'layout': [
                        ['bar', 'scatter'],
                        ['hist', 'pie'],
                        ['change_file']
                    ]
                }
            }
        }

    def make_bar_menu_structure(self):
        return {
            'title': 'Столбчатая диаграмма',
            'type': 'category',
            'items': {
                'x': self.make_xaxis_menu_structure('Ось X'),
                'y': self.make_yaxis_menu_structure('Ось Y'),
                'group_by': self.make_group_by_menu_structure(),
                'agg': self.make_agg_menu_structure(),
                'clean_outliers': self.make_clean_outliers_menu_structure(),
                'bar_submenu': self.make_bar_submenu_structure(),
                'back': {'title': 'Назад', 'command': 'reset'}
            },
            'layout': [
                ['x', 'y'],
                ['group_by'],
                ['agg'],
                ['clean_outliers'],
                ['back', 'bar_submenu']
            ]
        }

    def make_bar_submenu_structure(self):
        is_current_page = self.menu_history[-1] == 'bar_submenu'
        structure = {
            'type': 'category',
            'title': 'Дополнительно' if is_current_page else 'Далее',
            'items': {
                'sort_by': self.make_sort_by_menu_structure(),
                'sort_type': self.make_sort_type_menu_structure(),
                'head': self.make_input_menu_structure('int', 'head', 'Введите целое число',
                                                       'Взять первые n элементов'),
                'graph_title': self.make_input_menu_structure('str', 'graph_title', 'Введите заголовок графика',
                                                              'Заголовок графика'),
                'xlabel': self.make_input_menu_structure('str', 'xlabel', 'Введите подпись для оси X', 'Подпись оси X'),
                'ylabel': self.make_input_menu_structure('str', 'ylabel', 'Введите подпись для оси Y', 'Подпись оси Y'),
                'back': {'title': 'Назад', 'command': 'back'},
                'finish': {'title': 'Готово', 'command': 'finish'}
            },
            'layout': [
                ['sort_by'],
                ['sort_type'],
                ['head'],
                ['graph_title'],
                ['xlabel'],
                ['ylabel'],
                ['back'],
                ['finish']
            ],
            'show_graph': True,
            'command': 'validate'
        }

        return structure

    def make_scatter_menu_structure(self):
        return {
            'title': 'Точечная диаграмма',
            'type': 'category',
            'items': {
                'x': self.make_xaxis_menu_structure('Ось X'),
                'y': self.make_yaxis_menu_structure('Ось Y'),
                'clean_outliers': self.make_clean_outliers_menu_structure(),
                'scatter_submenu': self.make_scatter_submenu_structure(),
                'back': {'title': 'Назад', 'command': 'reset'}
            },
            'layout': [
                ['x', 'y'],
                ['clean_outliers'],
                ['back', 'scatter_submenu']
            ]
        }

    def make_scatter_submenu_structure(self):
        is_current_page = self.menu_history[-1] == 'scatter_submenu'
        structure = {
            'type': 'category',
            'title': 'Дополнительно' if is_current_page else 'Далее',
            'items': {
                'alpha': self.make_input_menu_structure('float', 'alpha', 'Введите дробное число от 0 до 1',
                                                        'Прозрачность точек'),
                'graph_title': self.make_input_menu_structure('str', 'graph_title', 'Введите заголовок графика',
                                                              'Заголовок графика'),
                'xlabel': self.make_input_menu_structure('str', 'xlabel', 'Введите подпись для оси X', 'Подпись оси X'),
                'ylabel': self.make_input_menu_structure('str', 'ylabel', 'Введите подпись для оси Y', 'Подпись оси Y'),
                'back': {'title': 'Назад', 'command': 'back'},
                'finish': {'title': 'Готово', 'command': 'finish'}
            },
            'layout': [
                ['alpha'],
                ['graph_title'],
                ['xlabel'],
                ['ylabel'],
                ['back'],
                ['finish']
            ],
            'show_graph': True,
            'command': 'validate'
        }

        return structure

    def make_hist_menu_structure(self):
        return {
            'title': 'Гистограмма',
            'type': 'category',
            'items': {
                'x': self.make_xaxis_menu_structure('Ось X'),
                'clean_outliers': self.make_clean_outliers_menu_structure(),
                'hist_submenu': self.make_hist_submenu_structure(),
                'back': {'title': 'Назад', 'command': 'reset'}
            },
            'layout': [
                ['x'],
                ['clean_outliers'],
                ['back', 'hist_submenu']
            ]
        }

    def make_hist_submenu_structure(self):
        is_current_page = self.menu_history[-1] == 'hist_submenu'
        structure = {
            'type': 'category',
            'title': 'Дополнительно' if is_current_page else 'Далее',
            'items': {
                'bins': self.make_input_menu_structure('int', 'bins', 'Введите целое число', 'Количество столбцов'),
                'discrete': self.make_discrete_menu_structure(),
                'graph_title': self.make_input_menu_structure('str', 'graph_title', 'Введите заголовок графика',
                                                              'Заголовок графика'),
                'xlabel': self.make_input_menu_structure('str', 'xlabel', 'Введите подпись для оси X', 'Подпись оси X'),
                'ylabel': self.make_input_menu_structure('str', 'ylabel', 'Введите подпись для оси Y', 'Подпись оси Y'),
                'back': {'title': 'Назад', 'command': 'back'},
                'finish': {'title': 'Готово', 'command': 'finish'}
            },
            'layout': [
                ['bins', 'discrete'],
                ['graph_title'],
                ['xlabel'],
                ['ylabel'],
                ['back'],
                ['finish']
            ],
            'show_graph': True,
            'command': 'validate'
        }

        return structure

    def make_pie_menu_structure(self):
        return {
            'title': 'Круговая диаграмма',
            'type': 'category',
            'items': {
                'x': self.make_xaxis_menu_structure('Стобец признака деления', False),
                'y': self.make_yaxis_menu_structure('Значение'),
                'agg': self.make_agg_menu_structure(),
                'pie_submenu': self.make_pie_submenu_structure(),
                'back': {'title': 'Назад', 'command': 'reset'}
            },
            'layout': [
                ['x', 'y'],
                ['agg'],
                ['back', 'pie_submenu']
            ]
        }

    def make_pie_submenu_structure(self):
        is_current_page = self.menu_history[-1] == 'pie_submenu'
        structure = {
            'type': 'category',
            'title': 'Дополнительно' if is_current_page else 'Далее',
            'items': {
                'pie_group_percent': self.make_input_menu_structure('float', 'pie_group_percent',
                                                                    'Введите дробное число от 0 до 1',
                                                                    'Объединять, если процент меньше'),
                'pie_group_name': self.make_input_menu_structure('str', 'pie_group_name',
                                                                 'Введите подпись для сгруппированных данных',
                                                                 'Имя прочего'),
                'graph_title': self.make_input_menu_structure('str', 'graph_title', 'Введите заголовок графика',
                                                              'Заголовок графика'),
                'back': {'title': 'Назад', 'command': 'back'},
                'finish': {'title': 'Готово', 'command': 'finish'}
            },
            'layout': [
                ['pie_group_percent'],
                ['pie_group_name'],
                ['graph_title'],
                ['back'],
                ['finish']
            ],
            'show_graph': True,
            'command': 'validate'
        }

        return structure

    def make_xaxis_menu_structure(self, title, add_count_value=True):
        structure = self.make_menu_columns_structure()
        structure['title'] = title

        if add_count_value and self.config.get('y', None) != '$count_x_values':
            structure['items']['$count_y_values'] = {'title': 'Кол-во значений Y'}
            structure['layout'].append('$count_y_values')

        current_value = self.config.get('x', None)

        if current_value is not None:
            structure['title'] += f" \n({structure['items'][current_value]['title']})"

        return structure

    def make_yaxis_menu_structure(self, title, add_count_value=True):
        structure = self.make_menu_columns_structure()
        structure['title'] = title

        if add_count_value and self.config.get('x', None) != '$count_y_values':
            structure['items']['$count_x_values'] = {'title': 'Кол-во значений X'}
            structure['layout'].append('$count_x_values')

        current_value = self.config.get('y', None)

        if current_value is not None:
            structure['title'] += f" \n({structure['items'][current_value]['title']})"

        return structure

    def make_menu_columns_structure(self):
        return {
            'type': 'select',
            'items': {col: {'title': col} for col in self.columns},
            'layout': list(map(lambda x, y: [x, y], self.columns[0::2], self.columns[1::2]))
        }

    def make_group_by_menu_structure(self):
        structure = {
            'title': 'Группировать по',
            'type': 'select',
            'items': {
                'None': {'title': 'Не группировать'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['None'],
                ['back']
            ]
        }

        x = self.config.get('x', None)
        y = self.config.get('y', None)

        if y is not None and y != '$count_x_values':
            structure['items'][y] = {'title': y}
            structure['layout'].insert(0, y)

        if x is not None and x != '$count_y_values':
            structure['items'][x] = {'title': x}
            structure['layout'].insert(0, x)

        current_value = self.config.get('group_by', None)

        structure['title'] += f" \n({structure['items'][str(current_value)]['title']})"

        return structure

    def make_agg_menu_structure(self):
        if self.config.get('group_by', None) is None or (
                self.config.get('graph_type', None) == 'pie' and self.config.get('y', None) == '$count_x_values'):
            return None

        structure = {
            'title': 'Агрегирующая функция',
            'type': 'select',
            'items': {
                'mean': {'title': 'Среднее'},
                'median': {'title': 'Медиана'},
                'sum': {'title': 'Сумма'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['mean', 'median', 'sum'],
                ['back']
            ]
        }

        current_value = self.config.get('agg', None)

        if current_value is not None:
            structure['title'] += f" \n({structure['items'][str(current_value)]['title']})"

        return structure

    def make_clean_outliers_menu_structure(self):
        structure = {
            'title': 'Очистка выбросов',
            'type': 'select',
            'items': {
                '0.75': {'title': 'Перцентиль 75'},
                '0.90': {'title': 'Перцентиль 90'},
                '0.99': {'title': 'Перцентиль 99'},
                'None': {'title': 'Не очищать'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['0.75', '0.90', '0.99'],
                ['None'],
                ['back']
            ]
        }

        current_value = self.config.get('clean_outliers', None)

        structure['title'] += f" \n({structure['items'][str(current_value)]['title']})"

        return structure

    def make_sort_by_menu_structure(self):
        structure = {
            'title': 'Сортировать по',
            'type': 'select',
            'items': {
                'None': {'title': 'Не сортировать'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['None'],
                ['back']
            ],
            'show_graph': True
        }

        x = self.config.get('x', None)
        y = self.config.get('y', None)

        if y is not None and y != '$count_x_values':
            structure['items'][y] = {'title': y}
            structure['layout'].insert(0, y)

        if x is not None and x != '$count_y_values':
            structure['items'][x] = {'title': x}
            structure['layout'].insert(0, x)
        current_value = self.config.get('sort_by', None)

        structure['title'] += f" \n({structure['items'][str(current_value)]['title']})"

        return structure

    def make_sort_type_menu_structure(self):
        if self.config.get('sort_by', None) is None:
            return None

        structure = {
            'title': 'Порядок сортировки',
            'type': 'select',
            'items': {
                'ascending': {'title': 'По возрастанию'},
                'descending': {'title': 'По убыванию'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['ascending', 'descending'],
                ['back']
            ],
            'show_graph': True
        }

        current_value = self.config.get('sort_type', None)

        if current_value is not None:
            structure['title'] += f" \n({structure['items'][current_value]['title']})"

        return structure

    def make_input_menu_structure(self, input_type, id, title, button_title, show_graph=True):
        is_current_page = self.menu_history[-1] == id
        structure = {
            'title': title if is_current_page else button_title,
            'type': input_type,
            'items': {
                'None': {'title': 'Сбросить'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['None', 'back']
            ],
            'show_graph': show_graph
        }

        current_value = self.config.get(id, None)

        if current_value is not None:
            structure['title'] += f" \n({str(current_value)})"

        return structure

    def make_discrete_menu_structure(self):
        structure = {
            'title': 'Дискретность',
            'type': 'select',
            'items': {
                'True': {'title': 'Да'},
                'False': {'title': 'Нет'},
                'back': {'title': 'Назад', 'command': 'back'}
            },
            'layout': [
                ['True', 'False'],
                ['back']
            ],
            'show_graph': True
        }

        current_value = self.config.get('discrete', None)

        if current_value is not None:
            structure['title'] += f" \n({structure['items'][str(current_value)]['title']})"

        return structure

    def make_bar_default_config(self):
        return {
            'graph_type': 'bar',
            'x': None,
            'y': None,
            'group_by': None,
            'agg': 'mean',
            'clear_outliers': None,
            'sort_by': None,
            'sort_type': 'ascending',
            'head': None,
            'graph_title': None,
            'xlabel': None,
            'ylabel': None
        }

    def make_hist_default_config(self):
        return {
            'graph_type': 'hist',
            'x': None,
            'clear_outliers': None,
            'graph_title': None,
            'xlabel': None,
            'ylabel': None,
            'bins': 10,
            'discrete': False
        }

    def make_pie_default_config(self):
        return {
            'graph_type': 'pie',
            'x': None,
            'y': '$count_x_values',
            'agg': 'sum',
            'graph_title': None,
            'pie_group_percent': 0.015,
            'pie_group_name': None
        }

    def make_scatter_default_config(self):
        return {
            'graph_type': 'scatter',
            'x': None,
            'y': None,
            'alpha': 0.6,
            'clear_outliers': None,
            'graph_title': None,
            'xlabel': None,
            'ylabel': None
        }

    def select(self, value):
        current_menu_page_id = self.menu_history[-1]

        if current_menu_page_id in ['x', 'y']:
            self.config['group_by'] = None
            self.config['sort_by'] = None

        if current_menu_page_id == 'group_by':
            current_agg_value = self.config.get('agg', None)
            current_agg_value = 'mean' if current_agg_value is None else current_agg_value

            self.config['agg'] = None if value is None else current_agg_value

        if current_menu_page_id == 'sort_by':
            current_sort_type_value = self.config.get('sort_type', None)
            current_sort_type_value = 'ascending' if current_sort_type_value is None else current_sort_type_value

            self.config['sort_type'] = None if value is None else current_sort_type_value

        if self.config.get('graph_type', None) == 'pie':
            if current_menu_page_id == 'x' or current_menu_page_id == 'y':
                x_value = value if current_menu_page_id == 'x' else self.config.get('x', None)
                y_value = value if current_menu_page_id == 'y' else self.config.get('y', None)
                self.config['group_by'] = None if y_value == '$count_x_values' else x_value
                self.config['sort_by'] = None if y_value == '$count_x_values' else y_value

                current_agg_value = self.config.get('agg', None)
                current_agg_value = 'mean' if current_agg_value is None else current_agg_value

                self.config['agg'] = None if y_value == '$count_x_values' else current_agg_value

        super().select(value)

    def validate_bar(self):
        if self.config['x'] is None:
            return False, 'Выберите колонку X'
            
        if self.config['y'] is None:
            return False, 'Выберите колонку Y'

        if self.config['x'] == self.config['y']:
            return False, 'Колонка X не должна быть равна колонке Y'

        if self.config['group_by'] is not None:
            aggregated_col = self.config['x'] if self.config['group_by'] == self.config['y'] else self.config['y']

            if not is_numeric_dtype(self.df_container.dataframe[aggregated_col]):
                return False, 'Применить агрегацию к полю не числового типа невозможно.'

        return True, None

    def validate_hist(self):
        if self.config['x'] is None:
            return False, 'Выберите колонку X'

        return True, None

    def validate_pie(self):
        if self.config['x'] is None:
            return False, 'Выберите колонку X'
            
        if self.config['y'] is None:
            return False, 'Выберите колонку Y'
        
        if self.config['x'] == self.config['y']:
            return False, 'Признак деления не должен быть равен значению'

        return True, None

    def validate_scatter(self):
        if self.config['x'] is None:
            return False, 'Выберите колонку X'
            
        if self.config['y'] is None:
            return False, 'Выберите колонку Y'

        if self.config['x'] == self.config['y']:
            return False, 'Колонка X не должна быть равна колонке Y'

        return True, None
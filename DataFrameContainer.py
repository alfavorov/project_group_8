from typing import Union
import pandas as pd
import io


class DataFrameContainer:
    # после того как пользователь выбрал конкретный файл, создаем с ним экземпляр этого класса
    # при инициализации произойдет один раз очистка и подготовка данных, merge с табличкой макрорегионов.
    # дальше уже будем вызвать методы для подготовки данных на этом экземпляре.
    def __init__(self, file_csv: Union[bytes, str] = None):
        if file_csv:
            if type(file_csv) is bytes:
                file_csv = io.BytesIO(file_csv)

            self.dataframe = pd.read_csv(file_csv)

    def get_columns(self):
        return list(self.dataframe.columns)

    def make_bar_data(self, config):
        df = self.make_axes(config)
        df = self.clean_outliers(df, config)
        df = self.group_values(df, config)
        df = self.sort_values(df, config)
        if config.get('head', None) is not None:
            df = df.head(config['head'])
        df = self.normalize_data(df, config)

        return df

    def make_hist_data(self, config):
        df = self.make_axes(config)
        df = self.clean_outliers(df, config)
        df = self.normalize_data(df, config)

        return df

    def make_pie_data(self, config):
        df = self.make_axes(config)
        df = self.group_values(df, config)
        df = self.sort_values(df, config)
        df = self.clean_pie(df, config)
        df = self.normalize_data(df, config)

        return df

    def make_scatter_data(self, config):
        df = self.make_axes(config)
        df = self.clean_outliers(df, config)
        df = self.group_values(df, config)
        df = self.normalize_data(df, config)

        return df

    def make_axes(self, config):
        columns = list()

        x, y = config.get('x', None), config.get('y', None)

        if x is not None and x != '$count_y_values':
            columns.append(x)

        if y is not None and y != '$count_x_values':
            columns.append(y)

        df = self.dataframe[columns]

        if x == '$count_y_values':
            df = df[y].value_counts()

        if y == '$count_x_values':
            df = df[x].value_counts()

        return df

    def clean_outliers(self, df, config):
        x, y = config.get('x', None), config.get('y', None)
        percent = config.get('clean_outliers', None)

        if percent is not None:
            percent = float(percent)
            point_desc = df.describe([percent])
            percent_str = f'{int(percent * 100)}%'

            if x is not None:
                point = point_desc[point_desc.index == percent_str][x][0]
                max_point = point_desc[point_desc.index == 'max'][x][0]
                min_point = point_desc[point_desc.index == 'min'][x][0]

                # убираем выбросы сверху или наоборот по x
                if max_point - point >= point - min_point:
                    df = df[df[x] <= point]
                else:
                    df = df[df[x] >= point]

            if y is not None:
                point = point_desc[point_desc.index == percent_str][y][0]
                max_point = point_desc[point_desc.index == 'max'][y][0]
                min_point = point_desc[point_desc.index == 'min'][y][0]

                # убираем выбросы сверху или наоборот по y
                if max_point - point >= point - min_point:
                    df = df[df[y] <= point]
                else:
                    df = df[df[y] >= point]

        return df

    def clean_pie(self, df, config):
        if config.get('pie_group_percent', None) is not None:
            group_percent = config.get('pie_group_percent', None)
            x = config['x']
            y = config['y']
            if config.get('pie_group_name', None) is not None:
                group_name = config.get('pie_group_name', None)
            else:
                group_name = 'other'

            if type(df) is pd.DataFrame:
                total = df.sum()[y]
                mask = df[y] / total >= group_percent
                df = df[mask].append(df[~mask].sum().rename(group_name))
            else:
                total = df.sum()
                mask = df / total >= 0.05
                other = df[~mask].sum()
                df = df[mask]
                df[group_name] = other

        return df

    def sort_values(self, df, config):
        if config.get('sort_by', None) is not None:
            ascending = config.get('sort_type', 'ascending') == 'ascending'

            if type(df) is pd.Series:
                df = df.sort_values(ascending=ascending)
            else:
                df = df.sort_values(by=config['sort_by'], ascending=ascending)

        return df

    def group_values(self, df, config):
        if config.get('group_by', None) is not None:
            df = df.groupby(config['group_by']).agg(config.get('agg', 'mean'))

        return df

    def normalize_data(self, df, config):
        if type(df) is pd.Series:
            x, y = None, None

            if config['x'] == '$count_y_values':
                x = df.values
                y = df.index
            else:
                x = df.index
                y = df.values

            return pd.DataFrame({'x': x, 'y': y})
        else:
            x, y = config.get('x', None), config.get('y', None)
            df = df.reset_index()

            normalized_df = pd.DataFrame()

            if x is not None:
                normalized_df['x'] = df[x]
            if y is not None:
                normalized_df['y'] = df[y]

            return normalized_df

    # статический метод, обращаемся к нему без создания экземпляра класса при загрузке пользователем файла.
    # если файл невалиден, то не сохраняем его.
    # downloaded_file из бота это поток байтов, поэтому сначала надо его преобразовать.
    # для совместимости оставил возможность передать просто строчку (вдруг где-то еще пригодится).
    @classmethod
    def validate_csv(cls, file: Union[bytes, str]):
        if type(file) is bytes:
            file = io.BytesIO(file)

        try:
            dataframe = pd.read_csv(file)
        except:
            return False

        # TODO: проверить файл, если надо

        return True

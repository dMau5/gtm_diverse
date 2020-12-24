# импорт сторонних библиотек
import dash
import dash_html_components as html
import dash_core_components as dcc
import os
import shutil
from dash.dependencies import Input, Output, State
from flask import Flask, send_from_directory
from diverse.gtm_diverse import gtm_diverse
from rdkit.Chem import SDWriter
from urllib.parse import quote as urlquote

DIRECTORY = 'gtm/files'  # папка для хранения результатов

# проверка на существование папки, чтобы при создании данного пути не возникло ошибки
if os.path.exists(DIRECTORY):
    shutil.rmtree(DIRECTORY, ignore_errors=True)
os.makedirs(DIRECTORY)

# сторонние стили для веб-страницы
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# указываем сервер для работы приложения
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

# порядок действий пользователя при работе с приложением на странице
desc = '''
__Instruction for calculate set of molecules with gtm1 diverse:__
* Choose the sdf file with correct blocks of molecules (example.sdf);
* Choose output set of molecules size (number of molecules must not be bigger than input count of molecules in file);
* Click __Calculate__ button;
* After the link appears, click to link for download result. 
'''
# добавление областей для разметки страницы под различные функции приложения
app.layout = html.Div([
    html.H1("GTM diverse", ),  # добавление названия приложения
    html.Hr(),  # добавление линии для разделения
    html.Div(dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                        }, multiple=True)),  # добавление области для загрузки файла
    html.Div(dcc.Input(id='count-box', type='number', placeholder='number of molecules', value=5, min=1, max=10 ** 6,
                       step=1, style={
                                   'width': '10%',
                                   'lineHeight': '60px',
                                   'borderWidth': '1px',
                                   'borderRadius': '5px',
                                   'textAlign': 'center',
                                   'margin': '10px 0'
                               })),  # добавления области для выбора размера библиотеки молекул
    html.Button('calculate', id='button'),  # добавление кнопки для расчета библиотеки молекул заданного размера
    html.Hr(),  # добавление линии для разделения
    html.Div(id='output-container-button',
             children='Enter a value and press submit', className='event'),  # добавление области для выходных данных
    html.Hr(),  # добавление линии для разделения
    html.Div([dcc.Markdown(desc)])  # добавление области для описания последовательности действий пользователя
], style={'textAlign': 'center'})


# функция, предназначенная для генерации ссылки на скачивание файла
@server.route("/download/<path:path>")
def download(path):
    return send_from_directory(DIRECTORY, path, as_attachment=True)


# функция, предназначенная для чтения входных данных, а также сохранения результата расчета модулем gtm_diverse
def save_file(names, contents, value):
    name = names[0]
    data = gtm_diverse(contents, value)
    w = SDWriter(os.path.join(DIRECTORY, f'{name[:-4]}_modified.sdf'))
    for m in data:
        w.write(m)


# функция, предназначенная для добавления ссылки на скачивание файла в область для выходных данных
def file_download_link(filename):
    return html.A('Download results', href=f"/download/{urlquote(filename)}")


# фунция, для получения доступных (уже записанных) файлов из определенной папки, где хранятся выходные данные
def uploaded_files():
    files = []
    for filename in os.listdir(DIRECTORY):
        path = os.path.join(DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


# функция, предназначенная для получения входных данных, а также их последовательная проверка для дальнейших расчетов
# она возвращает ссылку на скачивание файла
@app.callback(Output("output-container-button", "children"),
              [Input('button', 'n_clicks')], [State("upload-data", "filename"), State("upload-data", "contents")],
              [State("count-box", "value")])
def update_output(n_clicks, uploaded_filenames, uploaded_file_contents, value):
    if not n_clicks:
        return [html.Li('Click to Calculate')]
    if uploaded_filenames is None:
        return [html.Li('Choose the sdf file')]
    if uploaded_file_contents == ['data:']:
        return [html.Li('Your file is empty')]
    if value is None:
        return [html.Li('Please, choose the number of molecules')]
    if not all(name.endswith('.sdf') for name in uploaded_filenames):
        return [html.Li(f'Choose the *.sdf file (ex. molecules.sdf), given {" ".join(uploaded_filenames)}')]

    try:
        save_file(uploaded_filenames, uploaded_file_contents, value)
    except Exception as e:
        return [html.Li(f'Incorrect file, finished with error {e}')]

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        for file in files:
            old_file = f'{file[:-13]}.sdf'
            if old_file in uploaded_filenames:
                return [html.Li(file_download_link(file))]


server.secret_key = os.environ.get('SECRET_KEY', 'development')

# инструкция для запуска программы
if __name__ == '__main__':
    app.run_server(host='0.0.0.0')

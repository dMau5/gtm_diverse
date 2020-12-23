import dash
import dash_html_components as html
import dash_core_components as dcc
import os
from flask import Flask, send_from_directory
from urllib.parse import quote as urlquote
from dash.dependencies import Input, Output, State
import shutil
from rdkit.Chem import SDWriter
from gtm_diverse import gtm_diverse

DIRECTORY = 'gtm/files'

if os.path.exists(DIRECTORY):
    shutil.rmtree(DIRECTORY, ignore_errors=True)
os.makedirs(DIRECTORY)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.Div(dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                        },
                        multiple=True)),
    html.Div(dcc.Input(id='count-box', type='number', placeholder='number of molecules', min=1, max=10**6, step=1,
                       style={
                            'width': '10%',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0'
                       })),
    html.Button('Submit', id='button'),
    html.Div(id='output-container-button',
             children='Enter a value and press submit', className='event')
], style={'textAlign': 'center'})


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(DIRECTORY, path, as_attachment=True)


def func(molecules):
    return [molecules[0]]


def save_file(names, contents, value):
    """Decode and store a file uploaded with Plotly Dash."""
    name = names[0]
    data = gtm_diverse(contents, value)
    w = SDWriter(os.path.join(DIRECTORY, f'{name[:-4]}_modified.sdf'))
    for m in data:
        w.write(m)


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    return html.A('Download results', href=f"/download/{urlquote(filename)}")


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(DIRECTORY):
        path = os.path.join(DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


@app.callback(Output("output-container-button", "children"),
              [Input('button', 'n_clicks')], [State("upload-data", "filename"), State("upload-data", "contents")],
              [State("count-box", "value")])
def update_output(n_clicks, uploaded_filenames, uploaded_file_contents, value):
    """Save uploaded files and regenerate the file list."""
    if not n_clicks:
        return [html.Li('Click to submit')]
    if value is None:
        return [html.Li('Please, choose the number of molecules')]
    if uploaded_filenames is None:
        return [html.Li('Your filename is empty')]
    if uploaded_file_contents == ['data:']:
        return [html.Li('Your file is empty')]
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


if __name__ == '__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq
import plotly.graph_objects as go
import scipt as sc

data = []


# html.Img(src="assets/cat.gif", width=60, height=60),
def banner():
    return html.Div(
        id='banner',
        className='banner',
        children=[
            html.Div('PRACTICE', style={'font-size': '80px', 'padding': '10px 0px 0px 0px', 'line-height': '60px'}),
            html.Div(
                className='Flex',
                children=
                [
                    html.Div("High-Level languages", style={'font-size': '50px', 'padding': '0px 0px 0px 0px',
                                                            'line-height': '20px'}),
                    html.Div(
                        className='headlines',
                        children=
                        [
                            html.Div("Student: ", style={'font-size': '30px'}),
                            html.Div('Pepelina Natalia')
                        ], style={'padding': '0px 40px 0px 600px'}
                    ),
                    html.Div(
                        className='headlines',
                        children=
                        [
                            html.Div("Group: ", style={'font-size': '30px'}),
                            html.Div('K3-24Б')
                        ]
                    ),

                ]
            ),
        ]
    )


def upload_():
    return html.Div(
        children=[
            html.Div(dcc.Upload(html.Button('upload', className='button'), id='upload',
                                style={'padding': '40px 0px 0px 0px'}), ),
            html.Div([
                html.Div(daq.BooleanSwitch(id='heat', on=True, label='heat sens', color='rgb(8, 135, 255)')),
                html.Div(daq.BooleanSwitch(id='GisMeteo', on=False, label='GisMeteo', color='rgb(239, 125, 250)'))
            ], style={'display': 'flex', 'justify-content': 'space-between'}
            )

        ]
    )


def appliance_():
    return html.Div(
        children=[
            "Appliance",
            dcc.Dropdown(id='appliances', multi=True, style={'color': 'black'}),
            "Sensors",
            dcc.Dropdown(id='sensors', multi=True, style={'color': 'black'}),
        ],
        style={'width': '20%', 'display': 'inline-block', 'padding': '10px 0px 30px 50px'}
    )


def sensation_():
    return html.Div(
        children=[
            "Temperature",
            dcc.Dropdown(id='temp', multi=False, style={'color': 'black'}),
            "Humidity",
            dcc.Dropdown(id='hum', multi=False, style={'color': 'black'}),
        ],
        style={'width': '20%', 'display': 'inline-block', 'padding': '10px 0px 30px 50px'}
    )


def treatment_():
    return html.Div(
        children=[
            "Average",
            dcc.Dropdown(
                id='average',
                options=[
                    {'label': 'none', 'value': 'none'},
                    {'label': 'hour', 'value': 'hour'},
                    {'label': '3 hours', 'value': 'hour3'},
                    {'label': '12 hours', 'value': 'hour12'},
                    {'label': '24 hours', 'value': 'day'},
                    {'label': 'maximum per day', 'value': 'MAX'},
                    {'label': 'minimum per day', 'value': 'MIN'},
                ],
                value='none',
                style={'color': 'black'}
            ),

            "Type",
            dcc.Dropdown(
                id='type',
                options=[
                    {'label': 'lines', 'value': 'lines'},
                    {'label': 'markers', 'value': 'markers'},
                    {'label': 'lines and markers', 'value': 'lines+markers'},
                ],
                value='lines',
                style={'color': 'black'}
            ),
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px 0px 0px 50px'}
    )


def matrix_():
    return html.Div(
        children=[
            "Measured",
            dcc.Dropdown(id='measured', multi=False, style={'color': 'black'}),
            "Etolonic",
            dcc.Dropdown(id='etolonic', multi=False, style={'color': 'black'}),
        ],
        style={'width': '20%', 'display': 'inline-block', 'padding': '10px 0px 30px 50px'}
    )

app = dash.Dash(__name__)
app.title = 'Practice Pepelina'

app.layout = html.Div(
    children=[
        banner(),
        html.Div(
            className='banner opas',
            children=
            [
                upload_(),
                appliance_(),
                treatment_(),
                sensation_(),
                matrix_()
            ], style={'display': 'flex'}
        ),

        html.Div(
            className='banner opas',
            children=
            [
                dcc.Graph(id='graph', config={"staticPlot": False, "editable": False, "displayModeBar": False}),
            ], style={'width': '99.55%', 'padding': '10px 5px 5px 5px'}

        )
    ]
)


@app.callback([Output('appliances', 'options'), Output('appliances', 'value')], [Input('upload', 'contents')],
              [State('upload', 'filename'), State('upload', 'last_modified')])
def update_dropdown(list_of_contents, list_of_names, list_of_dates):
    global data
    if list_of_contents is not None:

        if '.txt' in list_of_names or '.json' in list_of_names or '.JSON' in list_of_names:
            data = sc.read_json(list_of_contents)
        if '.csv' in list_of_names or '.CSV' in list_of_names:
            data = sc.csv_to_json(sc.read_scv(list_of_contents))

    res = [dict(label=el, value=el) for el in sc.create_appliances_list(data).keys()]

    return res, None


@app.callback([Output('sensors', 'options'), Output('sensors', 'value'),
               Output('temp', 'options'), Output('temp', 'value'),
               Output('hum', 'options'), Output('hum', 'value'),
               Output('measured', 'options'), Output('measured', 'value'),
               Output('etolonic', 'options'), Output('etolonic', 'value')
               ],
              [Input('appliances', 'value')])
def update_sensor(appliances):
    res = []
    if appliances is not None:
        for i in appliances:
            lst = sc.create_appliances_list(data)[i]
            for el in lst:
                res.append(dict(label=el, value=el))

    return res, None, res, None, res, None, res, None, res, None


@app.callback(Output('graph', 'figure'),
              [Input('sensors', 'value'),
               Input('type', 'value'),
               Input('average', 'value'),
               Input('temp', 'value'),
               Input('hum', 'value'),
               Input('measured', 'value'),
               Input('etolonic', 'value'),
               dash.dependencies.Input('heat', 'on'),
               dash.dependencies.Input('GisMeteo', 'on')
               ])
def update_graph(sensor, type_, round_, temp_, hum_, measured_, etolonic_, heat_, gis_):
    fig = go.Figure()
    fig.update_layout(
        yaxis=dict(tickfont_size=20, title=''),
        xaxis=dict(tickfont_size=20, title=''),
        title='',
        #showlegend=True,
        autosize=True,
        height=710,
        colorway=['rgb(0,48,255)', 'rgb(0,204,58)', 'rgb(255,154,0)',
                  'rgb(255,0,0)', 'rgb(180,0,210)', 'rgb(0,205,255)',
                  'rgb(115,90,79)', 'rgb(76,118,76)', 'rgb(255,0,158)',
                  'rgb(208, 255, 0)', 'rgb(0,0,0)'],

        margin=dict(t=0, b=10, r=80, l=80),
        # font_color='white',
        plot_bgcolor='white',
        paper_bgcolor='rgb(216, 217, 254)',
        hovermode="x unified"

    )
    fig.update_xaxes(
        linecolor='Gainsboro',
        gridcolor='Gainsboro',
        zerolinecolor='Gainsboro',
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1H", step="hour", stepmode="backward"),
                dict(count=3, label="3H", step="hour", stepmode="backward"),
                dict(count=12, label="12H", step="hour", stepmode="backward"),
                dict(count=1, label="1D", step="day", stepmode="todate"),
                dict(step="all")
            ])
        )
    ),
    fig.update_yaxes(linecolor='Gainsboro', gridcolor='Gainsboro', zerolinecolor='Gainsboro', )

    if sensor is None and temp_ is None and hum_ is None:
        return fig

    min_, max_, dt_begin, dt_end = None, None, None, None

    if sensor:
        for el in sensor:
            uName, serial, item = sc.get_info(el)
            x_arr, y_arr = sc.get_data(uName, serial, item, data)
            x_arr, y_arr = sc.sort(round_, x_arr, y_arr)

            min_, max_ = sc.find_min_max(y_arr, min_, max_)
            dt_begin, dt_end = sc.find_date(x_arr[0], x_arr[-1], dt_begin, dt_end)

            fig.add_trace(go.Scatter(x=x_arr, y=y_arr, mode=type_, name="{} ({})".format(uName + ' ' + serial, item),
                                     hovertemplate="<b>%{y}</b>", showlegend=False))

    if temp_ and hum_:
        uName_temp, serial_temp, item_temp = sc.get_info(temp_)
        time, t_arr = sc.get_data(uName_temp, serial_temp, item_temp, data)

        uName_hum, serial_hum, item_hum = sc.get_info(hum_)
        time, h_arr = sc.get_data(uName_hum, serial_hum, item_hum, data)

        sens = sc.temp_efficiency(t_arr, h_arr)
        time, sens = sc.sort(round_, time, sens)

        min_, max_ = sc.find_min_max(sens, min_, max_)
        dt_begin, dt_end = sc.find_date(time[0], time[-1], dt_begin, dt_end)

        fig.add_trace(go.Scatter(x=time, y=sens, line_color="black", mode=type_, name="temp_efficiency",
                                 hovertemplate="<b>%{y}</b>", showlegend=False))

    if measured_ and etolonic_:
        uName_meas, serial_meas, item_meas = sc.get_info(measured_)
        time, meas_arr = sc.get_data(uName_meas, serial_meas, item_meas, data)

        uName_etolon, serial_etolon, item_etolon = sc.get_info(etolonic_)
        time, etolon_arr = sc.get_data(uName_etolon, serial_etolon, item_etolon, data)

        pol = sc.matrix(meas_arr, etolon_arr)
        time, sens = sc.sort(round_, time, pol)

        min_, max_ = sc.find_min_max(sens, min_, max_)
        dt_begin, dt_end = sc.find_date(time[0], time[-1], dt_begin, dt_end)

        fig.add_trace(go.Scatter(x=time, y=pol, line_color="violet", mode=type_, name="матричная хуйня",
                                 hovertemplate="<b>%{y}</b>", showlegend=False))

    if gis_ and dt_begin and dt_end:
        from datetime import date
        x_arr, y_temp, y_hum = sc.GetMeteo(date(dt_begin.year, dt_begin.month, 1), date(dt_end.year, dt_end.month, 1))
        x_arr, y_temp, y_hum = sc.Meteosort(x_arr, y_temp, y_hum, dt_begin, dt_end)

        min_, max_ = sc.find_min_max(y_temp, min_, max_)

        fig.update_layout(
            legend=dict(orientation='h', yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        fig.add_trace(go.Scatter(x=x_arr, y=y_temp, mode=type_, name="GisMeteo temp", hovertemplate="<b>%{y}</b>",
                                 visible='legendonly')),
        fig.add_trace(go.Scatter(x=x_arr, y=y_hum, mode=type_, name="GisMeteo press", hovertemplate="<b>%{y}</b>",
                                 visible='legendonly'))

    if heat_ and min_ and max_:
        dc, ann = sc.heat(dt_begin, dt_end, min_, max_)
        fig.update_layout(shapes=dc, annotations=ann)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

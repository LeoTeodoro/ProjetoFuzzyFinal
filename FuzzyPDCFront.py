import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import skfuzzy as fuzzy
import skfuzzy.control as ctrl
from dash.dependencies import Input, Output

FA = 1
Umax = 6
Erro = ctrl.Antecedent(np.arange(0, 1001, 5), 'Erro')
Erro['Z'] = fuzzy.trapmf(Erro.universe, [0, 0, 0, 5])  # Zero
Erro['MB'] = fuzzy.trimf(Erro.universe, [0, 5, 100])    # Muito Baixo
Erro['B'] = fuzzy.trimf(Erro.universe, [5, 100, 500])   # Baixo
Erro['A'] = fuzzy.trimf(Erro.universe, [100, 500, 750]) # Alto
Erro['MA'] = fuzzy.trapmf(Erro.universe, [500, 750, 1000, 1000]) # Muito Alto

DeltaErro = ctrl.Antecedent(np.arange(-1000, 1001, 1), 'DeltaErro')
DeltaErro['MN'] = fuzzy.trapmf(DeltaErro.universe, [-1000, -1000, -3, -1.5])
DeltaErro['PN'] = fuzzy.trimf(DeltaErro.universe, [-3, -1.5, 0])
DeltaErro['ZE'] = fuzzy.trimf(DeltaErro.universe, [-1, 0, 1])
DeltaErro['PP'] = fuzzy.trimf(DeltaErro.universe, [0, 1.5, 3])
DeltaErro['MP'] = fuzzy.trapmf(DeltaErro.universe, [1.5, 3, 1000, 1000])

PMotor = ctrl.Consequent(np.arange(0, 1.25, 0.25), 'PMotor')
PMotor['MB'] = fuzzy.trimf(PMotor.universe, [0, 0, 0.25])   # Muito Baixa
PMotor['B'] = fuzzy.trimf(PMotor.universe, [0, 0.25, 0.5])   # Baixa
PMotor['N'] = fuzzy.trimf(PMotor.universe, [0.25, 0.5, 0.75]) # Normal
PMotor['A'] = fuzzy.trimf(PMotor.universe, [0.5, 0.75, 1])   # Alta
PMotor['MA'] = fuzzy.trimf(PMotor.universe, [0.75, 1, 1])    # Muito Alta

regras = [
    ctrl.Rule(Erro['Z'] & DeltaErro['MN'], PMotor['MA']),
    ctrl.Rule(Erro['Z'] & DeltaErro['PN'], PMotor['MA']),
    ctrl.Rule(Erro['Z'] & DeltaErro['ZE'], PMotor['A']),
    ctrl.Rule(Erro['Z'] & DeltaErro['PP'], PMotor['N']),
    ctrl.Rule(Erro['Z'] & DeltaErro['MP'], PMotor['N']),
    ctrl.Rule(Erro['MB'] & DeltaErro['MN'], PMotor['MA']),
    ctrl.Rule(Erro['MB'] & DeltaErro['PN'], PMotor['A']),
    ctrl.Rule(Erro['MB'] & DeltaErro['ZE'], PMotor['A']),
    ctrl.Rule(Erro['MB'] & DeltaErro['PP'], PMotor['N']),
    ctrl.Rule(Erro['MB'] & DeltaErro['MP'], PMotor['N']),
    ctrl.Rule(Erro['B'] & DeltaErro['MN'], PMotor['MA']),
    ctrl.Rule(Erro['B'] & DeltaErro['PN'], PMotor['A']),
    ctrl.Rule(Erro['B'] & DeltaErro['ZE'], PMotor['N']),
    ctrl.Rule(Erro['B'] & DeltaErro['PP'], PMotor['N']),
    ctrl.Rule(Erro['B'] & DeltaErro['MP'], PMotor['N']),
    ctrl.Rule(Erro['A'] & DeltaErro['MN'], PMotor['B']),
    ctrl.Rule(Erro['A'] & DeltaErro['PN'], PMotor['B']),
    ctrl.Rule(Erro['A'] & DeltaErro['ZE'], PMotor['A']),
    ctrl.Rule(Erro['A'] & DeltaErro['PP'], PMotor['MA']),
    ctrl.Rule(Erro['A'] & DeltaErro['MP'], PMotor['MA']),
    ctrl.Rule(Erro['MA'] & DeltaErro['MN'], PMotor['B']),
    ctrl.Rule(Erro['MA'] & DeltaErro['PN'], PMotor['B']),
    ctrl.Rule(Erro['MA'] & DeltaErro['ZE'], PMotor['N']),
    ctrl.Rule(Erro['MA'] & DeltaErro['PP'], PMotor['MA']),
    ctrl.Rule(Erro['MA'] & DeltaErro['MP'], PMotor['MA']),
]

sistema_PMotor = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("Simulação Fuzzy - Controle de Altura do Drone", style={
            'text-align': 'center', 
            'font-family': 'Arial, sans-serif', 
            'color': '#333'
        }),
    ], style={'padding': '20px', 'background-color': '#f7f7f7'}),

    html.Div([
        html.Label("Defina o Setpoint (Altura desejada):", style={
            'font-size': '18px', 
            'color': '#333',
            'margin-bottom': '10px'
        }),
        dcc.Input(id='setpoint-input', type='number', value=200, step=1, style={
            'font-size': '16px',
            'padding': '10px',
            'border-radius': '8px',
            'border': '1px solid #ccc',
            'width': '100px',
            'margin-bottom': '20px',
        }),
    ], style={'text-align': 'center', 'margin-bottom': '30px'}),

    dcc.Graph(id='fuzzy-graph', style={
        'border': '1px solid #ccc',
        'border-radius': '10px',
        'box-shadow': '0px 0px 10px rgba(0, 0, 0, 0.1)',
        'margin-bottom': '20px'
    }),

    html.Div(id='status', style={
        'text-align': 'center',
        'font-size': '16px',
        'color': '#666',
        'margin-top': '20px'
    }),

    html.Div([
        html.Button('Subir', id='subir-btn', style={
            'color': '#ffffff',
            'background-color': '#2d63c8',
            'font-size': '19px',
            'border': '1px solid #2d63c8',
            'border-radius': '15px',
            'padding': '15px 50px',
            'cursor': 'pointer',
            'display': 'block',
            'margin': '0 auto',
            'margin-top': '20px',
            'transition': 'background-color 0.3s ease'
        }),
    ], style={'text-align': 'center', 'margin-top': '20px'}),

    html.Div([
        html.Button('Home', id='home-btn', style={
            'color': '#ffffff',
            'background-color': '#6e6e6e',
            'font-size': '19px',
            'border': '1px solid #6e6e6e',
            'border-radius': '15px',
            'padding': '10px 30px',
            'cursor': 'pointer',
            'position': 'absolute',
            'bottom': '10px',
            'left': '10px',
            'transition': 'background-color 0.3s ease'
        }),
    ])
])

@app.callback(
    [Output('setpoint-input', 'value'),
     Output('fuzzy-graph', 'figure'),
     Output('status', 'children'),
     Output('subir-btn', 'disabled')],  # Adiciona o controle de habilitação do botão Subir
    [Input('subir-btn', 'n_clicks'),
     Input('home-btn', 'n_clicks')],
    [dash.dependencies.State('setpoint-input', 'value')]
)
def iniciar_simulacao(n_clicks_subir, n_clicks_home, setpoint):
    # Caso o botão "Home" seja pressionado
    if n_clicks_home:
        # Limpa o gráfico, exibe a mensagem de reset e habilita o botão Subir
        figure = {
            'data': [],
            'layout': go.Layout(
                title='Posição vs. Tempo',
                xaxis={'title': 'Tempo (s)'},
                yaxis={'title': 'Posição (m)'},
                legend={'x': 0, 'y': 1},
            )
        }
        # Resetando o contador de clicks do botão "Subir" e habilitando-o
        return setpoint, figure, "Drone de volta ao estado inicial. Aguardando novo setpoint.", False
    
    # Caso o botão "Subir" seja pressionado
    if n_clicks_subir and setpoint is not None:
        FA = 1
        Umax = 6
        posicaoAtual, posicao = [0, [0]]
        erroAnterior = setpoint - posicaoAtual
        tempo = np.arange(0, 400, 1)

        # Processamento da simulação
        for _ in range(1, np.max(tempo) + 1):
            erroAtual = abs(setpoint - posicaoAtual)
            sistema_PMotor.input['Erro'] = erroAtual
            delta_erroAtual = erroAnterior - erroAtual
            sistema_PMotor.input['DeltaErro'] = delta_erroAtual
            sistema_PMotor.compute()
            PM = sistema_PMotor.output['PMotor']

            if 10 >= erroAtual < 50:
                FA -= 0.005
                PM = 0.35

            elif erroAtual < 10:
                FA -= 0.07
                PM = 0.35
            else:
                FA = 0.99

            posicaoAtual = FA * posicaoAtual * 1.01398 + 0.5 * (Umax * PM + Umax * PM)
            posicao = np.append(posicao, posicaoAtual)
            erroAnterior = erroAtual

        # Gerando gráfico com o resultado da simulação
        figure = {
            'data': [
                go.Scatter(x=tempo, y=posicao, mode='lines', name='Posição Atual'),
                go.Scatter(x=tempo, y=[setpoint] * len(tempo), mode='lines', name='SetPoint', line=dict(dash='dash', color='red'))
            ],
            'layout': go.Layout(
                title='Posição vs. Tempo',
                xaxis={'title': 'Tempo (s)'},
                yaxis={'title': 'Posição (m)'},
                legend={'x': 0, 'y': 1},
            )
        }

        return setpoint, figure, f"Simulação concluída! Setpoint: {setpoint}m", False

    return dash.no_update, dash.no_update, "Aguardando para iniciar a simulação.", False

if __name__ == '__main__':
    app.run_server(debug=True)

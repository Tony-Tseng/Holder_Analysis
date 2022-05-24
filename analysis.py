from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from utils import *
from datetime import datetime

import utils

interest_addr = "0x1919db36ca2fa2e15f9000fd9cdc2edcf863e685"
contract_addr = "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"

external_stylesheets = [dbc.themes.DARKLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)
DISPLAY_LIMIT = 15

balance_init = get_balance_plot(interest_addr)

erc20_table_init, erc20_bar_init = get_wallet_erc20_plot(interest_addr)
erc20_table_init = erc20_table_init.sort_values(by=["Erc20 Holding Num"], ascending=False)
erc20_table_init = erc20_table_init.iloc[:10]

nft_table_init = get_wallet_nft_table(interest_addr)
nft_table_init = nft_table_init.sort_values(by=["amount"], ascending=False)
nft_table_init = nft_table_init.iloc[:10]
nft_line_init = get_wallet_nft_plot(interest_addr, contract_addr)


app.layout = html.Div([
    html.Div(
        [html.H5('Final Project')],
        style={
            "display": "flex",
            "flex-direction": "row",
            "justify-content": "center",
            "background-color": "#2fa5ba"
        }),
    html.Div(
        [
            html.Div(
                children=[
                    html.H3('Analysis on ERC20 Token'),
                    html.Div(
                        children=[
                            html.H4(
                                'Please input Wallet Address',
                                style={'display': 'inline-block', 'margin-left': '3vw', 'margin-top': '1vw', 'justify-content': 'center'}
                            ),
                            dbc.Input(id="interest_address",
                                placeholder='Enter Address of NFT',
                                type='text',
                                value=f'{interest_addr}',
                                # debounce=True,
                                style={'display': 'inline-block', 'width': '25%', 'margin-left': '1vw', 'margin-top': '1vw', 'justify-content': 'center'}
                    ),
                ], style={'display': 'block'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id="balance_line",
                            figure=balance_init,
                        ),
                    ], 
                    style={'display': 'flex', 'margin-top': '1vw', 'width': '100%', 'justify-content': 'center'}
                ),
                html.Div(
                    children=[
                        html.Div([
                            dcc.Graph(
                                id="erc20_bar_chart",
                                figure=erc20_bar_init,
                            ),
                        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'}),
                        html.Div([
                            html.H5("Top 10 ERC20 Token Holding"),
                            dbc.Table.from_dataframe(erc20_table_init,
                                                        striped=True,
                                                        bordered=True,
                                                        hover=True),
                        ],
                        id="erc20_table_chart",
                        style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'})
                    ], 
                    style={'display': 'inline-block'}
                ),
                html.Div(
                    children=[
                        html.Div([
                            html.H5("Top 10 NFT Token Holding"),
                            dbc.Table.from_dataframe(nft_table_init,
                                                        striped=True,
                                                        bordered=True,
                                                        hover=True),
                        ],
                        id="nft_table_chart",
                        style={'display': 'inline-block', 'vertical-align': 'top', 'margin-top': '1vw'})
                    ], 
                    style={'display': 'flex', 'margin-top': '3vw', 'width': '100%', 'justify-content': 'center'}
                ),
                html.Div(
                    children=[
                        html.H4('Please input token/contract Address',
                                style={'display': 'inline-block', 'margin-left': '3vw', 'margin-top': '1vw', 'justify-content': 'center'}),
                        dbc.Input(id="contract_address",
                                placeholder='Enter Address of NFT',
                                type='text',
                                value=f'{contract_addr}',
                                # debounce=True,
                                style={'display': 'inline-block', 'width': '25%', 'margin-left': '3vw', 'margin-top': '1vw', 'justify-content': 'center'}
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="nft_line_plot",
                                    figure=nft_line_init,
                                ),
                            ],
                            style={'display': 'flex', 'margin-top': '1vw', 'width': '100%', 'justify-content': 'center'},
                        ),
                    ]
                ),
            ]),
        ],
        style={"padding": "30px", 'justify-content': 'center'}
    )
])

@app.callback(Output('erc20_bar_chart', 'figure'),
              Output('erc20_table_chart', 'children'),
              Input('interest_address', 'value'))
def update_erc20(interest_addr):
    table_df, erc20_bar_plot = get_wallet_erc20_plot(interest_addr)
    
    if table_df.shape[0]>0:
        table_df = table_df.sort_values(by=["Erc20 Holding Num"], ascending=False)
        table_df = table_df.iloc[:10]

    return erc20_bar_plot, [
        html.H5("Top 10 ERC20 Token Holding"),
        dbc.Table.from_dataframe(table_df,
                                 striped=True,
                                 bordered=True,
                                 hover=True)
    ]

@app.callback( Output('balance_line', 'figure'),
               Input('interest_address', 'value'))
def update_balance(interest_addr):
    balance_plot = get_balance_plot(interest_addr)
    
    return balance_plot

@app.callback( Output('nft_line_plot', 'figure'),
              [Input('interest_address', 'value'),
               Input('contract_address', 'value')])
def update_ntf_line(interest_addr, contract_addr):
    line_plot = get_wallet_nft_plot(interest_addr, contract_addr)
    
    return line_plot

@app.callback(Output('nft_table_chart', 'children'),
              Input('interest_address', 'value'))
def update_nft_table(interest_addr):
    table_df = get_wallet_nft_table(interest_addr)
    
    if table_df.shape[0]>0:
        table_df = table_df.sort_values(by=["amount"], ascending=False)
        table_df = table_df.iloc[:10]
    
    return [
        html.H5("Top 10 NFT Token Holding"),
        dbc.Table.from_dataframe(table_df,
                                 striped=True,
                                 bordered=True,
                                 hover=True)
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
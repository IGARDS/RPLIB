import dash_table

def get_standard_data_table(df,id):
    dataset_table = dash_table.DataTable(
        id=id,
        columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df.columns],
        data=df.to_dict("records"),
        is_focused=True,
        style_table={
            'height': 500,
            'overflowY': 'scroll',
        },
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold',
            "border": "1px solid white",
        },
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'textAlign': 'left'
        },
        filter_action='native',
        style_data={
            "backgroundColor": '#E3F2FD',
            "border-bottom": "1px solid #90CAF9",
            "border-top": "1px solid #90CAF9",
            "border-left": "1px solid #E3F2FD",
            "border-right": "1px solid #E3F2FD"},
        style_data_conditional=[
            {
                "if": {"state": "selected"},
                "backgroundColor": '#E3F2FD',
                "border-bottom": "1px solid #90CAF9",
                "border-top": "1px solid #90CAF9",
                "border-left": "1px solid #E3F2FD",
                "border-right": "1px solid #E3F2FD",
            }
        ]
    )
    return dataset_table

from dash import Dash, html, dcc,\
                 page_container, page_registry


app = Dash(__name__, use_pages=True, title="Football Stats")

app.layout = html.Div([
    html.H1('NGS / Adv Stats Grapher'),
    html.Div([
        dcc.Link(f"{page['name']}", href=page["relative_path"],
                 className='home-link', id=f"{page['name'].lower()}-home-link")
        for page in page_registry.values()
    ], style={'display':'flex', 'flex-direction':'row', 
              'justify-content': 'center'}),
    page_container
])


"""Deploy Application"""
# if __name__ == '__main__':
    # app.run_server(debug=False) # set to False for deployment
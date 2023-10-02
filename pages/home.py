from dash import html, dcc, register_page

register_page(__name__, path='/')

layout = html.Div([
    html.H1('↑ options ↑', style={
        'text-align':'center', 'color':'lightseagreen',
        'text-decoration':'underline dotted'}
            ),
    html.Div([
        html.Span('Explore advanced 2023 NFL statistics from '),
        dcc.Link('NGS ', href='https://nextgenstats.nfl.com/', className='home-body-link'),
        html.Span('and '),
        dcc.Link('PFR', href='https://www.pro-football-reference.com/', className='home-body-link'),
        html.Span('; choose an option above.'),
        
        # html.Img(id='passing-hover-image', style={'display':'none'},
                 # src="https://i.giphy.com/media/QA0xNtskSh4k7ghCc8/giphy.webp"),
        # html.Img(id='rushing-hover-image', style={'display':'none'},
                 # src="https://i.giphy.com/media/VEbJZZ4vkEnl2otr6C/giphy.webp"),
        # html.Img(id='receiving-hover-image', style={'display':'none'},
                 # src="https://i.giphy.com/media/ZESriDfKf1kIccGCIY/giphy.webp"),
                 
             ], className='home-body'),
        html.Div([
            html.Hr(style={'border-color':'khaki'}),
            dcc.Link('data provided by nflverse', className='home-body-link',
                     href='https://github.com/nflverse/nflverse-data', 
                     style={'float':'right', 'font-style':'italic'}),
            html.Br(),
            dcc.Link('Source Code', className='home-link home-link-2', 
     href='#', target='_blank'),
            dcc.Link('NGS Glossary', className='home-link home-link-2', 
     href='https://nextgenstats.nfl.com/glossary', target='_blank'),
            dcc.Link('PFR Glossary', className='home-link home-link-2', 
     href='https://www.pro-football-reference.com/about/glossary.htm',
                     target='_blank'),
            ], style={'margin-top':'400px'})
                  ])
# -*- coding: utf-8 -*-

"""
Created on Wed Dec 19 16:07:38 2018

@author: Amanda Gao

A script to run and log MCPC data through a Dash web app without too much headache.
"""
import serial
import time
import os

# Dash properties.
import dash
import dash_core_components as dcc
import dash_html_components as html
import ser_fun as sf
from dash.dependencies import Input, Output, State

import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go

# Initialize variables
data = []
times = []
time0 = time.time()
bauds = [9600, 19200, 38400, 57600]

# Streaming stuff.
api_key='rxagIqoTubGcgJmeaPDY'
stream_id = u'kavb4p4feq' # Streaming token.
stream_obj=go.scatter.Stream(
                 token=stream_id,
                 maxpoints=200)

# Initializing the streaming graph.
trace=go.Scatter(x=[],y=[], 
                 mode='lines+markers',
                 stream=stream_obj
                 )

# Available COM ports.
com_ports = sf.find_ports()
# Changing Button Styles
green_button_style={'border':'0px','background-color':'#B2FE8D',
                    'font-size':'20px', 'width':'95%'}
red_button_style={'border':'1px solid #FF6A6A','background-color':'#FA8072',
                  'font-size':'20px', 'width':'95%'}
# Changing visibility of the error div.
invisi_style={'text-align':'center', 'width':'90%','display':'none'}
visi_style={'text-align':'center', 'display':'inline-block','background-color':'#FED5FC',
            'border-radius':'5px','border-top':'10px solid #FED5FC', 'border-bottom':'10px solid #FED5FC', 
            'width':'90%'}
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    # Title.
    html.H2('MCPC Logger', style={'text-align':'center', 'font-weight':'bold'}),  

    # Div on the left with all the buttons and stuff.                       
    html.Div([
        
        # Div containing the file upload options.
            
            # dcc.Markdown('''**Filename:**'''),
        html.Div([
                  dcc.Input(id='filepath', value=os.getcwd()+'\\'+sf.gen_default_filename(), type='text',
                      style={'width':'95%', 'height':'30px','display':'inline-block','vertical-align':'top',}),
                            ],
            style={'width':'90%','text-align':'center'}, id='fileddiv'),
      
    # Baud rate and COM port
        html.Div([
            html.Div([
            dcc.Dropdown(
                id='com-dropdown',
                options=[{'label':name, 'value':name} for name in com_ports],
                placeholder='COM Port',
                style={'width':'100%', 'float':'left'}),
            html.Button('Refresh COM Ports',id='refresh', style={'width':'95%',
                                                                 'border':'0px',
                                                                 'height':'15px',
                                                                 'lineHeight':'15px',
                                                                 'margin':'0 auto',
                                                                 'float':'left',
                                                                 'text-align':'left',
                                                                 'vertical-align':'text-bottom'})],
            style={'width':'47.5%', 'display':'inline-block', 
                   'vertical-align':'top'}),
        
            html.Div([
                dcc.Dropdown(
                    id='baud-dropdown',
                    options=[{'label':str(baud)+' Hz', 'value':baud} for baud in bauds],
                              placeholder='Baud Rate',style={'width':'100%',
                                                             'float':'right'})],
                style={'width':'47.5%', 'display':'inline-block',
                   'vertical-align':'top','text-align':'center'})
            ],
            style={'width':'90%', 'text-align':'center'}),
        html.Div([

            html.P(),
            # Button that Starts the Program
            html.Button('Start Logging!', id='go_button',  n_clicks_timestamp=time.time(),
                        style=green_button_style)],
            style={'text-align':'center', 'width':'90%'}
        ),
        
        # Error messages go here.
        html.Div(['hold'], id='errors', style=invisi_style)
        ],
        style={'float':'left', 
        'width':'50%', 
        'borderRadius': '5px',
        }),
   
    # The rest of the page is the graph.
    html.Div([dcc.Graph(
                id='stream_plot',
                figure={
                    'data':[trace],
                    'layout':go.Layout(
                            xaxis={'title':'Time Elapsed'},
                                       )   
                        }  
              ,style={'float':'left'}),
              dcc.Interval(id='interval-conpoment',interval=1*1000,n_intervals=0)],
    style={'float':'right', 'width':'50%'})
])

#                      style={'maxWidth':'95%', 'width':'300px', 'margin':'0 auto'})],
#            html.Div([dcc.Upload(id='upload', children=[html.A('Select File')],
#                        style={
#                               'width':'95%',
#                               'height':'30px',
#                               'lineHeight': '30px',
#                               'borderWidth': '1px',
#                               'borderStyle': 'dashed',
#                               'borderRadius': '5px',
#                               'textAlign': 'center',
#                               'display':'inline-block',
#                               'float':'rigt',
#                               },
#                        multiple=False
#                        )],style={'width':'22.2%', 'display':'inline-block',
#                   'vertical-align':'top','text-align':'center'})                    

#try:
#    while (time.time() - time0 < 6):  
#        cnxn.write(b'status\r\n')
#        res = cnxn.read(254).decode('utf-8')    
#finally:
#    cnxn.close()

#======= DASH RELATED FUNCTIONS =======
# The various page element ids are:
    # com-dropdown: COM port selection.
    # refresh: Button to refresh COM selection.
    # filepath: Path and filename of .csv file.
    # baud-dropdown: Dropdown menu to choose baud rate.
    # errors: error messages

@app.callback(
    Output(component_id='com-dropdown', component_property='options'),
    [Input(component_id='refresh', component_property='n_clicks')]
)

def update_com_options(n_clicks):
    """
    Updates the COM ports.
    """
    com_ports = sf.find_ports()
    if n_clicks==0:
        return
    else:
        return [{'label':name, 'value':name} for name in com_ports]

@app.callback(
    Output(component_id='errors', component_property='children'),
    [Input(component_id='go_button', component_property='n_clicks')],
     [State(component_id='com-dropdown',component_property='value'),
     State(component_id='baud-dropdown',component_property='value'),
     State(component_id='filepath',component_property='value')
     ]
    )
def def_errors(n_clicks, com, baud, filepath):
    """
    Main function to check that everything is ready. Returns [] if there are no errors.
    """
    
    # Check to see that the button was clicked
    error_msgs=['''**ERROR**: Invalid File Path''', 
            '''**ERROR**: Invalid COM Port''']
    if n_clicks>0:
         # Existing errors cleared.
        error_list=[]
        # Check whether or not path is valid.
        if not sf.is_path_valid(filepath):
            error_list.append(dcc.Markdown(error_msgs[0],style={'width':'90%','display':'inline-block'}))
            
         # First check to connect to the COM Port.
        try:
            ser=serial.Serial(port=com,baudrate=baud, timeout=2)
        except:
            error_list.append(dcc.Markdown(error_msgs[1],containerProps={'width':'90%','display':'inline-block'}))
            return error_list
        file = open(filepathe,"w")
        file.write('Time,Conc,Raw Conc,Counts,Optics Block T,Optics Block P,Condenser T,Condenser P,Sat Top T,Sat Top P,Sat Bot T,Sat Bot P,Sat Flow,Sat Pump P,Sample Flow,Inlet T,Fill Count\n')
        file.close()
        ser.close()
        
@app.callback(Output(component_id='stream_plot', component_property='figure'),
              [Input(component_id='interval-component', component_property='n_intervals')],
              [State(component_id='errors', component_property='children'),
               State(component_id='com-dropdown',component_property='value'),
               State(component_id='baud-dropdown',component_property='value'),
               State(component_id='filepath',component_property='value')])
def log_and_plot_conc(n_intervs,errors,com,baud,filepath):
    if not errors:
        ser=serial.Serial(port=com,baudrate=baud, timeout=2)
        sf.log_mcpc_data(ser, filepath)
        
        time_vals=[]
        conc_vals=[]
        with open(filepath) as f:
            for row in f:
                time_vals.append(row.split()[0])
                conc_vals.append(row.split()[1])
        trace=go.Scatter(
                y=conc_vals,
                line=Line(color='#42C4F7'),mode='lines')
        layout=go.Layout(
                xaxis=dict(range=[0,200],showgrid=False,
                           showline=False,zeroline=False,fixedrange=True,
                           tickvals=['200','150','100','50','0'],
                           title='Time Elapsed (sec)'),
                yaxis=dict(range=[min(0, min(conc_vals)), max(10,max(conc_vals))],
                                  showline=False,
                                  fixedrange=True,
                                  zeroline=False,
                                  showgrid=False)
                )
        # Read the existing data.
        return go.Figure(data=[trace],layout=layout)
    else:
        return
    
@app.callback(
    Output(component_id='errors', component_property='style'),
    [Input(component_id='errors', component_property='children')])
def change_error_div(msgs):
    ''' Changes the style of the error message box if errors are detected'''
    if not msgs:
        return invisi_style
    elif 'hold' in msgs:
        return invisi_style
    else:
        return visi_style

@app.callback(
    Output(component_id='go_button', component_property='style'),
    [Input(component_id='go_button', component_property='n_clicks')],
    [State(component_id='errors', component_property='children')])             
    
def change_button_style(n_clicks, msgs):
    """
    Changes the color of the button.
    """
    # Check to see if the button was recently clicked.
    if n_clicks>0:
        # if there are no errors and the program needs to be started.
        time.sleep(1)
        if not msgs:
            return red_button_style    
        # if the program is running and needs to stop:
        elif 'running' in msgs:
            return green_button_style
    return green_button_style
  
@app.callback(
    Output(component_id='go_button', component_property='children'),
    [Input(component_id='go_button', component_property='style')]
) 
def change_button_text(style):
    """
    Changes the button text
    """
    if style==green_button_style:  
        return 'Start Logging!'
    else:
        return 'Stop Logging! '
    
#========================= RUN THE APP ====================================
if __name__ == '__main__':
    app.run_server(debug=False)
    
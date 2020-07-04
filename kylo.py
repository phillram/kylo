####################################################################
# Importing requirements 
####################################################################
import os, random, urllib3, json
from pyngrok import ngrok
from flask import Flask, request, got_request_exception, render_template, Markup, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_nav import Nav
from flask_nav.elements import *
from wtforms import StringField, TextField, SubmitField, SelectField
from wtforms.validators import DataRequired

# Logging imports you may not need
# import logging, certifi
# import ssl as ssl_lib


####################################################################
# Initializing Flask
# Load it with bootstrap and set a totally secret key for CSRF
# Then initializing the top navbar and adding it to the page
####################################################################
app = Flask(__name__)
Bootstrap(app)
nav = Nav()
nav.init_app(app)
app.config['SECRET_KEY'] = str(random.randint(0,100000000000))


####################################################################
# Flask Routing 
####################################################################

# Navbar for top of page
@nav.navigation()
def mynavbar():
    return Navbar(
        'Kylo',
        View('Home', 'index'),
    )

# Favicon routing
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = create_message_form(meta={'csrf': False})
    # Perform action when Submit is clicked
    if form.validate_on_submit():
        # Pull data from form to be used
        post_client_token = form.post_client_token.data
        post_server_token = form.post_server_token.data
        rollbar_environment = form.rollbar_environment.data
        message_type = form.message_type.data
        rollbar_message = form.rollbar_message.data

        # Confirming values recieved from form
        # print('Form Post Client Token:' + post_client_token) 
        # print('Form Post Server Token:' + post_server_token)
        # print('Form Rollbar Environment Type:' + rollbar_environment) 
        # print('Form Message Type:' + message_type) 
        # print('Form Rollbar Message:' + rollbar_message) 

        # POST the API request to create an item
        perform_api_request('POST', post_client_token, post_server_token, 
            rollbar_environment, message_type, rollbar_message)

    # Renders the page
    return render_template('index.html', form = form)


####################################################################
# Functions
####################################################################
# Use flask-wtf to create the fields for the form generation
class create_message_form(FlaskForm):
    # Fields for user to fill out
    post_server_token = StringField('Your post_server_item token',
        [ DataRequired() ]
    )
    post_client_token = StringField('Your post_client_item token',
    )
    rollbar_environment = StringField('Environment',
    )
    message_type = SelectField( 'Message Type',
        choices=[ ('critical', 'Critical'), ('debug', 'Debug'),('error', 'Error'),('info', 'Info'),('warning', 'Warning') ]
    )
    rollbar_message = StringField('Message to send',
    )


# Use the Rollbar API to perform an action
# Method is the API method
# Currently it's only creating items
# I'll likely edit this to create an endpoint

def perform_api_request(method, post_client_token, post_server_token, 
    rollbar_environment, message_type, rollbar_message):


    # Taking information from the form and creating a new item via Rollbar API
    rollbar_response_raw = urllib3.PoolManager().request('POST', 
        'https://api.rollbar.com/api/1/item/',
        headers = {
            'X-Rollbar-Access-Token' : post_server_token,
        },
        body = json.dumps({
            'data':{
                'environment': rollbar_environment,
                'level': message_type,
                'body' : {
                    'message' : {
                        'body': rollbar_message,
                        },
                },
            }
        })
    )

    # Parsing the API result above and saves the response to display in UI
    rollbar_response = json.loads(rollbar_response_raw.data.decode('utf-8'))

    if rollbar_response['err'] == 0 :
        flash_message = Markup(rollbar_response['result'])
    else:
        flash_message = Markup(rollbar_response['message'])
    
    # There shouldn't be a case where flash_message isn't set (hopefully!)
    flash('Response from Rollbar: ' + flash_message)

    return 'banana'

####################################################################
# Start Maul and run flask on set port
####################################################################
if __name__ == '__main__':
    port = '5066'

    # Flask logging information
    ####################################################################
    # ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(logging.StreamHandler())

    # This section is for using the script on Heroku
    # Only if the HEROKU environment variable is set to True
    ####################################################################
    try:
        os.environ['HEROKU'] == 'True'
        # print('Starting on Heroku')
        app.run(port=port)

    # If the HEROKU environment variable is not set
    # It will open an ngrok instance on the same port as Flask
    # This will allow public traffic be able to access your localhost Flask instance
    ####################################################################
    except:
        # print('Starting with Ngrok')
        public_url = ngrok.connect(port=port)
        tunnels = ngrok.get_tunnels()
        # Print the Ngrok URL in console
        print(str(tunnels[0]))

        # Using the port specificed to match Ngrok and to start Flask
        app.run(port=port)
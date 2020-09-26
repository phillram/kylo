####################################################################
# Kylo -- A hopefully useful tool for Rollbar
####################################################################

####################################################################
# Importing requirements 
####################################################################
from kylo_functions import *

import os, random, rollbar
from pyngrok import ngrok
from flask import Flask, request, got_request_exception, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *

# Logging imports you may not need
# import logging, certifi
# import ssl as ssl_lib


####################################################################
# Initializing & test Rollbar
# To catch errors that Kylo throws
####################################################################
rollbar.init(os.environ['ROLLBAR_POST_SERVER_TOKEN'])
rollbar.report_message('Rollbar is reporting properly')

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
        Link('Github', 'https://github.com/phillram/kylo'),
    )

# Favicon routing
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Home Page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = create_item(meta={'csrf': False})
    # Perform action when Submit is clicked
    if form.validate_on_submit():
        # Pull data from form to be used
        endpoint = form.endpoint.data
        api_token = form.api_token.data
        rollbar_environment = form.rollbar_environment.data
        message_type = form.message_type.data
        rollbar_message = form.rollbar_message.data

        # POST the API request to create an item
        perform_api_request('POST', endpoint, api_token, 
            rollbar_environment, message_type, rollbar_message)

    return render_template('index.html', form = form)


####################################################################
# Start Kylo and run flask on set port
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
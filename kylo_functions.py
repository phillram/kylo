####################################################################
# Kylo Functions
####################################################################

####################################################################
# Importing requirements 
####################################################################
import json
import urllib3
from flask import flash, Markup
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


####################################################################
# Use flask-wtf to generate forms
####################################################################
class create_item(FlaskForm):
    # Fields for user to fill out
    endpoint = RadioField( 'Function',
        choices=[ ('item', 'Create Item'), ('items', 'List Items')], default = 'item'
    )
    api_token = StringField('Your API token',
        [ DataRequired() ]
    )
    rollbar_environment = StringField('Environment',
    )
    message_type = SelectField( 'Message Type',
        choices=[ ('critical', 'Critical'), ('debug', 'Debug'),('error', 'Error'),('info', 'Info'),('warning', 'Warning') ]
    )
    rollbar_message = StringField('Message to send',
    )


####################################################################
# Use the Rollbar API
####################################################################
def perform_api_request(method, endpoint, api_token, 
    rollbar_environment, message_type, rollbar_message):

    # Building the API call
    url = 'https://api.rollbar.com/api/1/' + endpoint + '/'

    header = {
            'X-Rollbar-Access-Token' : api_token,
        }

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

    # Add the information to display a cURL  in the UI
    flash('Your not fully implemented to be API call:\n' + str(url) + str(header) + str(body) + '\n', 'api_request')

    # Taking information from the form and creating a new item via Rollbar API
    rollbar_response_raw = urllib3.PoolManager().request(method, url, headers=header, body=body)

    # Parsing the API result above and saves the response to display in UI
    rollbar_response = json.loads(rollbar_response_raw.data.decode('utf-8'))

    # Check if it's an error response or not, then display error messages or links to the ocurrence
    if rollbar_response['err'] == 0 :
        flash_message = Markup(rollbar_response['result'])
        flash('Response from Rollbar: ' + flash_message, 'api_response')
        flash('Your occurrence can be found here: https://rollbar.com/occurrence/uuid/?uuid=' + rollbar_response['uuid'], 'api_response')
    else:
        flash_message = Markup(rollbar_response['message'])
        flash('Response from Rollbar: ' + flash_message, 'api_response')


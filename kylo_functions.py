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
from wtforms import StringField, TextField, SubmitField, SelectField
from wtforms.validators import DataRequired


####################################################################
# Use flask-wtf to generate forms
####################################################################
class home_page(FlaskForm):
    # Fields for user to fill out
    # post_server_token = StringField('Your post_server_item token',
    #     [ DataRequired() ]
    # )
    # post_client_token = StringField('Your post_client_item token',
    # )
    # rollbar_environment = StringField('Environment',
    # )
    # message_type = SelectField( 'Message Type',
    #     choices=[ ('critical', 'Critical'), ('debug', 'Debug'),('error', 'Error'),('info', 'Info'),('warning', 'Warning') ]
    # )
    rollbar_message = StringField('Message to send',
    )


class create_item(FlaskForm):
    # Fields for user to fill out
    api_token = StringField('Your post_server_item token',
        [ DataRequired() ]
    )
    # api_token = StringField('Your post_client_item token',
    # )
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

    # Check if it's an error response or not, then display it in the UI
    if rollbar_response['err'] == 0 :
        flash_message = Markup(rollbar_response['result'])
    else:
        flash_message = Markup(rollbar_response['message'])
    
    # There shouldn't be a case where flash_message isn't set (hopefully!)
    flash('Response from Rollbar: ' + flash_message, 'api_response')


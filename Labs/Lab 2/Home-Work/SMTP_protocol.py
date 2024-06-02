# ####################################### #
# Title: SMTP_protocol.py
# Author: Yehuda Gurovich
# Course: Avanced Computer Networks
# Lab Number: 2
# ###################################### #


PORT = 25

CLIENT_ADDRESS = "localhost"
SERVER_ADDRESS = "localhost"
SMTP_SERVICE_READY = "220"
REQUESTED_ACTION_COMPLETED = "250"
COMMAND_SYNTAX_ERROR = "501 Syntax error in parameters or arguments"
INCORRECT_AUTH = "535"
ENTER_MESSAGE = "354"
AUTH_INPUT = "334"
AUTH_SUCCESS = "235"
EMAIL_END = "\r\n.\r\n"  # Find which combination of chars indicates email end
SERVER_QUIT = "221 Service closing transmission channel"
CLIENT_QUIT = "QUIT"
# Email was rejected by the recipient's mail server
SERVER_EMAIL_REJECION = "521 <domain> does not accept mail"

DATA_HEADER_SIZE = 8
AUTH_TYPE = "AUTH LOGIN"
DATA_COMMAND = "DATA"

MAIL_FROM_COMMAND = "MAIL FROM:"
RCPT_TO_COMMAND = "RCPT TO:"

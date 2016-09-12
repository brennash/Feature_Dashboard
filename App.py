#########################################################################################
# The Feature Dashboard Python flask application. 					#
#											#
# Version: 1.3										#
# Date:    20160519									#
#########################################################################################

#!/usr/bin/env python
from flask import render_template
from flask import make_response, send_from_directory, redirect, url_for
from flask import Flask, request, Response
from functools import wraps
import json
import io
import os
import csv
import logging
import datetime
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

@app.route('/')
def index():

	# The logger
	timeStamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	reqIPAddr = request.remote_addr
	app.logger.info('%s - Analytics Request GET REQUEST index.html request from %s',timeStamp, reqIPAddr)

	# Render the template
	return render_template('index.html')


if __name__ == '__main__':
	handler = RotatingFileHandler('/home/ubuntu/Feature_Dashboard/application.log', maxBytes=10000, backupCount=3)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(host='0.0.0.0', debug=True, port=1234)

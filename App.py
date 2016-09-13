#########################################################################################
# The Feature Dashboard Python flask application. 					#
#											#
# Version: 0.0 										#
# Date:    20160012									#
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
import MySQLdb
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

@app.route('/submit', methods=['GET','POST'])
def submit():
	if request.method == 'GET':
		timeStamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		reqIPAddr = request.remote_addr
		app.logger.info('%s - Analytics Request GET REQUEST submit request from %s',timeStamp, reqIPAddr)
		return render_template('index.html')
	elif request.method == 'POST':
		print "SUBMIT POST "
		timeStamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		reqIPAddr = request.remote_addr
		app.logger.info('%s - Analytics Request POST REQUEST submit request from %s',timeStamp, reqIPAddr)
		
		utilType = str(request.form.get('util-type'))
		betType  = str(request.form.get('bet-type'))
		minProb  = float(request.form.get('min-prob'))
		maxProb  = float(request.form.get('max-prob'))
		minUtil  = float(request.form.get('min-util'))
		maxUtil  = float(request.form.get('max-util'))

		values = getValues(utilType, betType, minProb, maxProb, minUtil, maxUtil)

		return render_template('gains.html', values=values)

def getValues(utilType, betType, minProb, maxProb, minUtil, maxUtil):
	try:
		db = MySQLdb.connect(host="localhost", user='USERNAME', passwd='PASSWD', db='DATABASE')
		cursor = db.cursor()
		tableName = "Features"
		if betType == 'Single':
			sql =  'SELECT * FROM Features WHERE '
			if utilType == 'BEST':
				sql += '(ProbWin - (1.0/BestOdds)) >= {0} AND '.format(minUtil)
				sql += '(ProbWin - (1.0/BestOdds)) <= {0} AND '.format(maxUtil)
			elif utilType == 'AVG':
				sql += '(ProbWin - (1.0/AvgOdds)) >= {0} AND '.format(minUtil)
				sql += '(ProbWin - (1.0/AvgOdds)) <= {0} AND '.format(maxUtil)
			elif utilType == 'WORST':
				sql += '(ProbWin - (1.0/WorstOdds)) >= {0} AND '.format(minUtil)
				sql += '(ProbWin - (1.0/WorstOdds)) <= {0} AND '.format(maxUtil)
			sql += 'ProbWin >= {0} AND '.format(minProb)
			sql += 'ProbWin <= {0};'.format(maxProb)
		query = text(sql)
		resultSet = self.db.execute(query, tableName=tableName)	
		rows = resultSet.fetchall()
		for row in rows:
			print row
		cursor.close()
		db.close()
	except MySQLdb.Error as e:			
		print 'Error - {0}'.format( str(e) )

	# { x : "Jul 2016", y : 6 },

if __name__ == '__main__':
	handler = RotatingFileHandler('/home/ubuntu/Feature_Dashboard/log/application.log', maxBytes=10000, backupCount=3)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(host='0.0.0.0', debug=True, port=1234)

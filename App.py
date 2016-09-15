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
import sqlalchemy
from sqlalchemy import text
from sqlalchemy import exc
from logging.handlers import RotatingFileHandler

app = Flask(__name__, static_url_path='/static')
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
		timeStamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		reqIPAddr = request.remote_addr
		app.logger.info('%s - Analytics Request POST REQUEST submit request from %s',timeStamp, reqIPAddr)
		
		utilType = str(request.form.get('util-type'))
		betType  = str(request.form.get('bet-type'))
		minProb  = float(request.form.get('min-prob'))
		maxProb  = float(request.form.get('max-prob'))
		minUtil  = float(request.form.get('min-util'))
		maxUtil  = float(request.form.get('max-util'))

		dataSet = getData(utilType, betType, minProb, maxProb, minUtil, maxUtil)
		values = getValues(dataSet)
		lossStreak, winStreak = getStreak(dataSet)
		print 'WIN STREAK: {0}, LOSS STREAK: {1}'.format(winStreak, lossStreak)

		return render_template('gains.html', values=values, betType=betType, lossStreak=lossStreak, winStreak=winStreak)

def getData(utilType, betType, minProb, maxProb, minUtil, maxUtil):
	""" Function with queries the database and returns a list of lists giving the
		data breakdowns for either single or accumulator bets.
	"""
	if betType == 'SINGLE':
		sql = getSingleSQL(utilType, minProb, maxProb, minUtil, maxUtil)
	else:
		sql = getAccumSQL(utilType, minProb, maxProb, minUtil, maxUtil)

	try:
		engine = sqlalchemy.create_engine("mysql://leaguepredict:leaguepredict@localhost/leaguepredict")
		db = engine.connect()
		resultSet = db.execute(sql, tableName='Features')
		rows = resultSet.fetchall()
		db.close()
		return rows
	except exc.SQLAlchemyError, err:
		print 'Error - {0}'.format( str(e) )
		return None

def getValues(dataSet):
	""" Parses the data returned from the database and constructs a 
	    list of values for the cumulative gains over all the seasons.
	"""
	xList = []
	yList = []
	total = 0.0

	for row in dataSet:
		batchNum     = row[0]
		seasonCode   = row[1]
		result       = row[2]
		fixtureDate  = row[3]
		worstOdds    = row[4]
		numFixtures  = row[5]

		xList.append(fixtureDate)
		if result > 0.0:
			total += worstOdds - 1.0
		else:
			total -= 1.0
		yList.append(total)

	output = ''
	for index, xValue in enumerate(xList):
		yValue = yList[index]
		output += '\t{'
		output += 'x:"{0}", y:{1}'.format(xValue, yValue)
		output += '},\n'
	output = output[:-2]
	return output

def getStreak(dataSet):
	winStreak  = 0
	lossStreak = 0
	bestWinStreak  = 0
	bestLossStreak = 0
	prevResult = None

	for row in dataSet:
		batchNum     = row[0]
		seasonCode   = row[1]
		result       = row[2]
		fixtureDate  = row[3]
		worstOdds    = row[4]
		numFixtures  = row[5]

		if prevResult is None:
			prevResult = result
		elif prevResult == result:
			if result > 0:
				winStreak += 1
			else:
				lossStreak += 1
		elif prevResult != result:
			if result > 0:
				if lossStreak > bestLossStreak:
					bestLossStreak = lossStreak
				lossStreak = 0
				winStreak = 0
			else:
				if winStreak > bestWinStreak:
					bestWinStreak = winStreak
				winStreak = 0
				lossStreak = 0

	return bestWinStreak, bestLossStreak


def getSingleSQL(utilType, minProb, maxProb, minUtil, maxUtil):

	if utilType == 'BEST':
		utilText = 'BestOdds'
	elif utilType == 'WORST':
		utilText = 'WorstOdds'
	else:
		utilText = 'AvgOdds'

	sql =  'SELECT BatchNum, SeasonCode, Result, DATE(FixtureDate), WorstOdds, 1 FROM Features WHERE '
	sql += 'ProbWin >= {0} AND '.format(minProb)
	sql += 'ProbWin <= {0} AND '.format(maxProb)
	sql += '(ProbWin - (1.0/{0})) >= {1} AND '.format(utilText, minUtil)
	sql += '(ProbWin - (1.0/{0})) <= {1} '.format(utilText, maxUtil)
	sql += 'ORDER BY FixtureDate ASC;'
	return sql


def getAccumSQL(utilType, minProb, maxProb, minUtil, maxUtil):

	if utilType == 'BEST':
		utilText = 'BestOdds'
	elif utilType == 'WORST':
		utilText = 'WorstOdds'
	else:
		utilText = 'AvgOdds'

	sql =  'SELECT BatchNum, SeasonCode, MIN(Result), MIN(DATE(FixtureDate)) AS FixtureDate, '
	sql += 'EXP(SUM(LOG(ABS(worstOdds)))) AS WorstOdds, COUNT(*) FROM Features WHERE '
	sql += 'ProbWin >= {0} AND '.format(minProb)
	sql += 'ProbWin <= {0} AND '.format(maxProb)
	sql += '(ProbWin - (1.0/{0})) >= {1} AND '.format(utilText, minUtil)
	sql += '(ProbWin - (1.0/{0})) <= {1} '.format(utilText, maxUtil)
	sql += 'GROUP BY BatchNum, SeasonCode ORDER BY FixtureDate ASC;'
	return sql

if __name__ == '__main__':
	handler = RotatingFileHandler('/home/ubuntu/Feature_Dashboard/log/application.log', maxBytes=10000, backupCount=3)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(host='0.0.0.0', debug=True, port=1234)

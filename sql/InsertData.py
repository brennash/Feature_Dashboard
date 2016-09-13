import sys
import io
import os
import csv
import logging
import datetime
import random
import MySQLdb
from pprint import pprint
from optparse import OptionParser

class InsertData:

	def __init__(self, inputFilename):
		self.database    = 'DATABASE'
		self.username    = 'USERNAME'
		self.password    = 'PASSWORD'
		self.db          = None
		self.cursor      = None

		connected = self.initConnection()

		if not connected:
			print 'Error - cannot connect to MySQL database'
			exit(1)

		# Read in the CSV data
		inputFile    = open(inputFilename, 'r')
		inputCSV     = csv.reader(inputFile)
		index = 0

		# Add the CSV to the database
		for row in inputCSV:
			if index > 0:
				batchNum    = row[0]
				result      = row[1]
				probWin     = row[2]
				seasonCode  = row[3]
				leagueCode  = row[4]
				fixtureDate = row[5]
				homeTeam    = row[6]
				homeFT      = row[7]
				awayFT      = row[8]
				awayTeam    = row[9]
				bestOdds    = row[10]
				worstOdds   = row[11]
				avgOdds     = row[12]
				sql =  'INSERT INTO Features (BatchNum, Result, ProbWin, SeasonCode, '
				sql += 'LeagueCode, FixtureDate, HomeTeam, HomeFT, AwayFT, AwayTeam, '
				sql += 'BestOdds, WorstOdds, AvgOdds) VALUES '
				sql += "({0},{1},{2},'{3}','{4}','{5}','{6}',{7},{8},'{9}',{10},{11},{12});".format(
					batchNum,
					result,
					probWin,
					seasonCode,
					leagueCode,
					fixtureDate,
					homeTeam,
					homeFT,
					awayFT,
					awayTeam,
					bestOdds,
					worstOdds,
					avgOdds)

				try:
					self.cursor.execute(sql);
		                except MySQLdb.Error as e:
                		        print 'Error Inserting - {0}'.format( str(e) )

				print 'Inserted {0} lines'.format(index)
			index += 1
		self.cursor.execute('COMMIT;')


	def initConnection(self):
		try:
			self.db = MySQLdb.connect(host="localhost", user=self.username, passwd=self.password, db=self.database)
                        self.cursor = self.db.cursor()
			return True
                except MySQLdb.Error as e:
			print 'Error Initializing MySQL Database Connection - {0}'.format( str(e) )
			return False

        def closeConnection(self):
                try:
			self.mySQLCursor.close()
			self.mySQLdb.close()
                except MySQLdb.Error as e:
                        print 'Error Closing MySQL Database Connection - {0}'.format( str(e) )

def main(argv):
	parser = OptionParser(usage="Usage: InsertData filename")

	parser.add_option("-v", "--verbose",
		action="store_true",
		dest="verboseFlag",
		default=False,
		help="Verbose output, print the DB status to the console.")

	(options, filename) = parser.parse_args()

	if len(filename) != 1:
		parser.print_help()
		print '\nYou need to provide an input file.'
		exit(1)

	bridge = InsertData(filename[0])

if __name__ == "__main__":
    sys.exit(main(sys.argv))


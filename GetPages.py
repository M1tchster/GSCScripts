#!/usr/bin/python

"""
	Function:
		Writes the CTR, Position, Impressions, and Clicks for all the URLs in the list to the Data folder

	Requirements:
		A Google account's developer page Client ID and a Client Secret (store in client_secrets.json) - saves token in webmasters.dat

	Sample usage: (no quotes)
		$ python GetPages.py '2016-01-01' '2016-01-31' 'URLList.txt'
		1 (Start date YYYY-MM-DD)
		2 (End date YYYY-MM-DD)
		3 (File containing a new line deliminated list of URLS/pages belonging to website)
"""

import argparse
import sys
import csv
import os
import time

from googleapiclient import sample_tools
from apiclient.http import BatchHttpRequest

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('start_date', type=str, help=('Start date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str, help=('End date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('url_file', type=str, help=('Text file containing new line deliminated list of pages (protocols needed).'))


def main(argv):

	lService, lFlags = sample_tools.init(
		argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
		scope='https://www.googleapis.com/auth/webmasters.readonly')

	lLines = [line.rstrip('\n') for line in open(lFlags.url_file)]

	wipe_data()

	lPos = 0
	lBatch = BatchHttpRequest()

	for lURL in lLines:

		# TODO: Is it possible to minimize the request count (send one get two)?
		lRequest = {
			'startDate': lFlags.start_date,
			'endDate': lFlags.end_date,
			'dimensions': ['page'],
			'dimensionFilterGroups': [
				{
					'filters': [{
						'dimension': 'page',
						'expression': lURL
					}]
				}
			],
		}

		# TODO: Test with arg (maybe split '?')
		#lURL.split("//")[-1].split("/")[0]
		theSiteURL = (lURL.split("//")[0]+"//"+(lURL.split("//")[-1].split("/")[0]))
		#theSiteURL = lURL
		print "Adding "+lURL
		lBatch.add(lService.searchanalytics().query(siteUrl=theSiteURL, body=lRequest), HandleRequest)
		lPos += 1


		# Try 10 QPS and 20 QPS -- 10 should work... Analytics is 5? Webmasters is 10? Search Analytics is 3?

		if lPos == 5:												# 5 queries per second is a Google imposed limit
			lBatch.execute()
			time.sleep(1)											# If it runs too fast Google will deny the request.
			lBatch = BatchHttpRequest()
			lPos = 0

	if lPos:
		lBatch.execute()



def HandleRequest(lRequest, lResponse, lException):

	if lException is not None:

		#Handle exception
		print lException._get_reason()
		pass

	else:

		if 'rows' in lResponse:

			append_data(lResponse)

		else:
			print 'No data'




def wipe_data():
	'''
		Wipes the Data directory
	'''
	if not os.path.exists('Data'):
		os.makedirs('Data')

	if os.path.exists('Data/URLs.txt'):
		os.remove('Data/URLs.txt')
	if os.path.exists('Data/Click.txt'):
		os.remove('Data/Click.txt')
	if os.path.exists('Data/Imp.txt'):
		os.remove('Data/Imp.txt')
	if os.path.exists('Data/CTR.txt'):
		os.remove('Data/CTR.txt')
	if os.path.exists('Data/Pos.txt'):
		os.remove('Data/Pos.txt')


def append_data(aResponse):
	"""
	Writes the data for the top pages in five files.
	The files contain: URL(s), clicks, impressions, CTR, and average positional.
	Args:
		aResponse: The server response to be printed as a table.
	"""

	lKeyFile = open('Data/URLs.txt', "a")
	lClickFile = open('Data/Click.txt', "a")
	lImpFile = open('Data/Imp.txt', "a")
	lCTRFile = open('Data/CTR.txt', "a")
	lPosFile = open('Data/Pos.txt', "a")

	lRows = aResponse['rows']
	for lRow in lRows:

		aKey = 'N/A'

		if 'keys' in lRow:
			aKey  = u','.join(lRow['keys']).encode('utf-8')

		lKeyFile.write(aKey+'\n')
		lClickFile.write(("%.0f"%lRow['clicks'])+'\n');
		lImpFile.write(("%.0f"%lRow['impressions'])+'\n');
		lCTRFile.write(("%.3f"%(lRow['ctr']*100))+'%'+'\n');
		lPosFile.write(("%.9f"%lRow['position'])+'\n');

	lKeyFile.close()
	lClickFile.close()
	lImpFile.close()
	lCTRFile.close()
	lPosFile.close()



if __name__ == '__main__':
  main(sys.argv)

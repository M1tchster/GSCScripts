#!/usr/bin/python

"""
	Function:
		Writes the list of top x pages/URLS for the website in the data folder
		Writes the CTR, Position, Impressions, and Clicks for all these pages in the data folder

	Requirements:
		A Google account's developer page Client ID and a Client Secret (store in client_secrets.json) - saves token in webmasters.dat

	Sample usage: (no quotes)
		$ python TopPages.py 'http://www.example.com' '2016-01-01' '2016-01-31' '5000'
		1 (URI)
		2 (Start date YYYY-MM-DD)
		3 (End date YYYY-MM-DD)
		4 (Number of top pages to output data for, max is 5000)
"""

import argparse
import sys
import csv
import os

from googleapiclient import sample_tools

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('property_uri', type=str, help=('Site or app URI to query data for (including trailing slash).'))
argparser.add_argument('start_date', type=str, help=('Start date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str, help=('End date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('page_num', type=str, help=('The number of top pages to get the data for.'))


def main(argv):

	lService, lFlags = sample_tools.init(
		argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
		scope='https://www.googleapis.com/auth/webmasters.readonly')

	# Get top pages for the date range, sorted by click count, descending.
	lRequest = {
		'startDate': lFlags.start_date,
		'endDate': lFlags.end_date,
		'dimensions': ['page'],
		'rowLimit': lFlags.page_num
	}
	lResponse = execute_request(lService, lFlags.property_uri, lRequest)

	wipe_data()

	if 'rows' in lResponse:
		write_data(lResponse)
	else:
		print 'NO RESPONSE!'


def execute_request(service, property_uri, request):
	"""
		Executes a searchAnalytics.query request.

		Args:
			service: The webmasters service to use when executing the query.
			property_uri: The site or app URI to request data for.
			request: The request to be executed.
		Returns:
			An array of response rows.
	"""
	return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()


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


def write_data(aResponse):
	"""
	Writes the data for the top pages in five files.
	The files contain: URL(s), clicks, impressions, CTR, and average positional.
	Args:
		aResponse: The server response to be printed as a table.
	"""

	print "Writing data"

	lKeyFile = open('Data/URLs.txt', "w")
	lClickFile = open('Data/Click.txt', "w")
	lImpFile = open('Data/Imp.txt', "w")
	lCTRFile = open('Data/CTR.txt', "w")
	lPosFile = open('Data/Pos.txt', "w")

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

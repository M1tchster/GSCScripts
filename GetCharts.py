#!/usr/bin/python

"""
	Function:
		Outputs the top 5,000 google searches (Top Searches.csv) that have the website in the output folder
		Outputs the date stats (Date Stats.csv) in the output folder

	Requirements:
		A Google account's developer page Client ID and a Client Secret (store in client_secrets.json) - saves token in webmasters.dat

	Sample usage: (no quotes)
		$ python GetCharts.py 'C:\output' 'http://www.example.com' '2016-01-01' '2016-01-31' '5000'
		1 (Output folder)
		2 (URI)
		3 (Start date YYYY-MM-DD)
		4 (End date YYYY-MM-DD)
"""

import argparse
import sys
import csv
import os

from googleapiclient import sample_tools

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('output_dir', type=str, help=('Output folder to write the charts in.'))
argparser.add_argument('property_uri', type=str, help=('Site or app URI to query data for (including trailing slash).'))
argparser.add_argument('start_date', type=str, help=('Start date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str, help=('End date of the requested date range in YYYY-MM-DD format.'))

def main(argv):

	lService, lFlags = sample_tools.init(
		argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
		scope='https://www.googleapis.com/auth/webmasters.readonly')

	if not os.path.exists(lFlags.output_dir):
		os.makedirs(lFlags.output_dir)

	lURLFile = lFlags.property_uri
	lURLFile = lURLFile.replace("/", "_")
	lURLFile = lURLFile.replace(".", "-")
	lURLFile = lURLFile.replace(":", "-")
	lURLFile = lURLFile.replace("?", "_")

	# Stats for the dates in the range specified, sorted by date, earliest first.
	lRequest = {
		'startDate': lFlags.start_date,
		'endDate': lFlags.end_date,
		'dimensions': ['date']
	}
	lResponse = execute_request(lService, lFlags.property_uri, lRequest)
	if 'rows' in lResponse:
		write_table(lResponse, lFlags.output_dir+'/'+lURLFile+' Date Stats.csv')
	else:
		print 'Empty response'

	# Get top Google queries for the date range, sorted by click count, descending.
	lRequest = {
		'startDate': lFlags.start_date,
		'endDate': lFlags.end_date,
		'dimensions': ['query'],
		'rowLimit': 5000
	}
	lResponse = execute_request(lService, lFlags.property_uri, lRequest)
	if 'rows' in lResponse:
		write_table(lResponse, lFlags.output_dir+'/'+lURLFile+' Top Keywords.csv')
	else:
		print 'Empty response'


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


def write_table(aResponse, aFile):
	"""
		Writes a response (csv) table
		Each row contains key(s), clicks, impressions, CTR, and average position.

		Args:
			aResponse: The server response to be printed as a table.
			aFile: The file name for the table (in the output folder).
	"""

	print "Writing CSV for "+aFile

	lCsvFile = open(aFile, "wb")
	lCsvWriter = csv.writer(lCsvFile)

	lRows = aResponse['rows']
	lCsvWriter.writerow(('Keywords', 'Clicks', 'Impressions', 'CTR', 'Position'))

	for lRow in lRows:

		aKey = 'N/A'

		if 'keys' in lRow:
			aKey = u','.join(lRow['keys']).encode('utf-8')

		lCsvWriter.writerow((
			aKey,
			("%.0f"%lRow['clicks']),
			("%.0f"%lRow['impressions']),
			("%.3f"%(lRow['ctr']*100))+'%',
			("%.9f"%lRow['position'])
		))

	lCsvFile.close();


if __name__ == '__main__':
  main(sys.argv)

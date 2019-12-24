#!/usr/bin/python

"""
	Function:
		Outputs the Google search/keyword chart for a list of pages/URLs to output/PAGE_NAME/keywords.csv
			PAGE_NAME is the URL of the page, with the characters '/', '.', ':', '?', '=', and '&' removed

	Requirements:
		A Google account's developer page Client ID and a Client Secret (store in client_secrets.json) - saves token in webmasters.dat

	Sample usage: (no quotes)
		$ python GetKeywords.py 'C:\output' '2016-01-01' '2016-01-31' 'URLList.txt'
		1 (Output folder)
		2 (Start date YYYY-MM-DD)
		3 (End date YYYY-MM-DD)
		4 (File containing a new line deliminated list of URLS/pages belonging to website)
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
argparser.add_argument('output_dir', type=str, help=('Output folder to write the charts in.'))
argparser.add_argument('start_date', type=str, help=('Start date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str, help=('End date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('url_file', type=str, help=('Text file containing new line deliminated list of pages (protocols needed).'))


lCurUrl = 0
lLines = 0
lFlags = 0


def main(argv):

	global lLines
	global lFlags

	lService, lFlags = sample_tools.init(
		argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
		scope='https://www.googleapis.com/auth/webmasters.readonly')

	lLines = [line.rstrip('\n') for line in open(lFlags.url_file)]

	lPos = 0
	lBatch = BatchHttpRequest()

	for lURL in lLines:

		lRequest = {
			'startDate': lFlags.start_date,
			'endDate': lFlags.end_date,
			'dimensions': ['query'],
			'dimensionFilterGroups': [{
				'filters': [{
					'dimension': 'page',
					'expression': lURL
				}]
			}]
		}

		theSiteURL = (lURL.split("//")[0]+"//"+(lURL.split("//")[-1].split("/")[0]))
		lBatch.add(lService.searchanalytics().query(siteUrl=theSiteURL, body=lRequest), HandleRequest)
		lPos += 1

		if lPos == 5:
			lBatch.execute()
			time.sleep(0.5)											# If it runs too fast Google will deny the request.
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

		global lCurUrl

		lURL = lLines[lCurUrl]
		lCurUrl += 1

		if 'rows' in lResponse:

			lURLFolder = lURL
			lURLFolder = lURLFolder.replace("/", "_")
			lURLFolder = lURLFolder.replace(".", "-")
			lURLFolder = lURLFolder.replace(":", "-")
			lURLFolder = lURLFolder.replace("?", "_")

			if lURLFolder.endswith('_'):
				lURLFolder = lURLFolder[:-1]

			lFolder = lFlags.output_dir+"/Pages/"+lURLFolder

			lFileName = 'GSC '+lURLFolder.rsplit('_', 1)[-1]
			if lFileName.endswith('-html'):
				lFileName = lFileName[:-5]

			lFileName = lFileName[:59]+'.csv'

			if not os.path.exists(lFolder):
				os.makedirs(lFolder)

			print "Writing data for "+lURL
			write_table(lFlags.start_date, lFlags.end_date, lResponse, lFolder+'/'+lFileName)

		else:
			print 'No data for '+lURL


def write_table(aStart, aEnd, aResponse, aFile):
	"""
		Writes a response (csv) table
		Each row contains key(s), clicks, impressions, CTR, and average position.

		Args:
			aResponse: The server response to be printed as a table.
			aFile: The file name for the table (in the output folder).
	"""

	lCsvFile = open(aFile, "wb")
	lCsvWriter = csv.writer(lCsvFile)

	lRows = aResponse['rows']
	lCsvWriter.writerow(('Start timestamp', 'End timestamp'))
	lCsvWriter.writerow((aStart, aEnd));
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

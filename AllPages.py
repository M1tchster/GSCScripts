#!/usr/bin/python

"""
	Function:
		Writes a list containing every site URL in the account into URLs.txt inside the temp folder
		Writes the CTR, Position, Impressions, and Clicks for all these pages in the temp folder

	Limitations:
		Up to 5,000 URLs per website will be reported. If an individual site has more URLs, only the top ones are returned.

	Requirements:
		A Google account's developer page Client ID and a Client Secret (store in client_secrets.json) - saves token in webmasters.dat

	Sample usage: (no quotes)
		$ python AllPages.py 'http://www.example.com' '2016-01-01' '2016-01-31' '5000'
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
argparser.add_argument('start_date', type=str, help=('Start date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('end_date', type=str, help=('End date of the requested date range in YYYY-MM-DD format.'))
argparser.add_argument('ignore_list', type=str, default="", help=('List of URLs to ignore from the account.'))


def main(argv):

	lService, lFlags = sample_tools.init(
		argv, 'webmasters', 'v3', __doc__, __file__, parents=[argparser],
		scope='https://www.googleapis.com/auth/webmasters.readonly')


	lResponse = lService.sites().list().execute()
	lRows = lResponse['siteEntry']

	# Read the ignore list
	lIgnoreList = []
	if os.path.isfile(lFlags.ignore_list):
		lIgnoreList = [line.rstrip('\n') for line in open(lFlags.ignore_list)]
	else:
		print "No Ignore List... continuing"

	lURLList = []

	lKeyFile = open('Temp/URLs.txt', "w")
	lClickFile = open('Temp/Click.txt', "w")
	lImpFile = open('Temp/Imp.txt', "w")
	lCTRFile = open('Temp/CTR.txt', "w")
	lPosFile = open('Temp/Pos.txt', "w")

	# TODO: Auto-sort rows?
	# We want root sites (like http://adobe.com/) to come later than sub-sites (http://adobe.com/jp/)
	for lRow in lRows:
		if not 'siteUnverifiedUser' in lRow['permissionLevel']:
			if not "sc-set:" in lRow['siteUrl']:

				theSubURL = lRow['siteUrl']

				lContinue = 1
				for lStr in lIgnoreList:
						if theSubURL.startswith(lStr):
							lContinue = 0

				if lContinue:

					lIgnoreList.append(theSubURL)

					# TODO: Batch request this?
					lRequest = {
						'startDate': lFlags.start_date,
						'endDate': lFlags.end_date,
						'dimensions': ['page'],
						'rowLimit': 5000
					}
					lResponse = execute_request(lService, theSubURL, lRequest)

					print theSubURL

					if 'rows' in lResponse:
						for lRow in lResponse['rows']:

							aKey = 'N/A'
							if 'keys' in lRow:
								aKey  = u','.join(lRow['keys']).encode('utf-8')

							lExists = 0
							if aKey in lURLList:		# Skip duplicates...
								lExists = 1

							if lExists == 0:
								lKeyFile.write(aKey+'\n')
								lClickFile.write(("%.0f"%lRow['clicks'])+'\n');
								lImpFile.write(("%.0f"%lRow['impressions'])+'\n');
								lCTRFile.write(("%.3f"%(lRow['ctr']*100))+'%'+'\n');
								lPosFile.write(("%.9f"%lRow['position'])+'\n');
								lURLList.append(aKey)
					else:
						print 'NO DATA'

	lKeyFile.close()
	lClickFile.close()
	lImpFile.close()
	lCTRFile.close()
	lPosFile.close()


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

if __name__ == '__main__':
  main(sys.argv)

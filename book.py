#!/usr/bin/env python
"""
SYNOPSIS

    book.py [-v,--verbose]

DESCRIPTION

    Books a court for the following week.

AUTHOR

    Sean Hodges <seanhodges84@gmail.com>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.
"""

import sys, os, traceback, optparse
import time
import re
import requests
from collections import namedtuple
from bs4 import BeautifulSoup
#from pexpect import run, spawn

class AspActionHelper:

    AspSession = namedtuple("AspSession", "sessionid viewstate eventvalidation")
    AspRequest = namedtuple("AspRequest", "cookies payload")

    @staticmethod
    def getActionUrl(path):
        return 'https://www.hertsmereleisurebookings.co.uk/Horizons/' + path

    @staticmethod
    def getSessionId(r):
        val = r.cookies['ASP.NET_SessionId']
        return val

    @staticmethod
    def getEventValidation(r):
        return re.search('__EVENTVALIDATION" value="(.*)"', r.text).group(1)

    @staticmethod
    def getViewState(r):
        return re.search('__VIEWSTATE" value="(.*)"', r.text).group(1)

    @staticmethod
    def getSession(r):
        sessionid = AspActionHelper.getSessionId(r)
        viewstate = AspActionHelper.getViewState(r)
        eventvalidation = AspActionHelper.getEventValidation(r)
        return AspActionHelper.AspSession(sessionid, viewstate, eventvalidation)

    @staticmethod
    def buildAspAction(session, args):
        cookies = {
            'ASP.NET_SessionId' : session.sessionid
        }
        payload = {
            '__VIEWSTATE' : session.viewstate,
            '__EVENTVALIDATION' : session.eventvalidation
        }
        payload.update(args)
        return AspActionHelper.AspRequest(cookies, payload)


class BookingTableDigester:

    @staticmethod
    def getCourtAvailability(data, time):
        # Grab the booking table
        soup = BeautifulSoup(data)
        bookingtable = soup.find(id='ctl00_cphMain_WucBookingSheet1_tabBookingGrid')

        # Process the court information
        cells = bookingtable.find(text=time).parent.parent.find_all('td')
        availability = (
            cells[1]['class'][0] == 'TD7',
            cells[2]['class'][0] == 'TD7',
            cells[3]['class'][0] == 'TD7',
            cells[4]['class'][0] == 'TD7'
        )
        return availability

    @staticmethod
    def checkItemIsInBasket(data):
        soup = BeautifulSoup(data)
        bookingtable = soup.find(id='ctl00_cphMain_WucBasket1_tabBasketItems')
        return bookingtable is not None and len(bookingtable.find_all('tr')) > 0

    @staticmethod
    def getItemInBasket(data):
        soup = BeautifulSoup(data)
        bookingtable = soup.find(id='ctl00_cphMain_WucBasket1_tabBasketItems')
        entryname = bookingtable.find('input')['name']
        return entryname


def main ():
    global options, args

    # Initialise session and grab keys
    url = AspActionHelper.getActionUrl('/Login/Default.aspx?regionid=4')
    response = requests.get(url)
    session = AspActionHelper.getSession(response)

    # Login to site
    request = AspActionHelper.buildAspAction(session, {
        '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
        '__EVENTARGUMENT' : '',
        'ctl00$cphLogin$txtEmail' : 'seanhodges84@gmail.com',
        'ctl00$cphLogin$txtPassword' : 'do4love'
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)

    # Hop to the booking page, we force the viewstate to make this happen
    # TODO: why do we need to do this? perhaps we should store the viewstates rather than grabbing them?
    viewstate = '/wEPDwULLTE5MTM4MzU3MzAPZBYCZg9kFgICAQ9kFggCAQ8WAh4EVGV4dAU4PGltZyBzcmM9ImdyYXBoaWNzL1dQLWdyYXBoaWNzL2xvZ28uZ2lmIiBib3JkZXI9Im5vbmUiLz5kAgMPZBYOAgEPDxYCHwAFBEhvbWVkZAIDDw8WAh8ABQtNeSBTZXR0aW5nc2RkAgcPDxYGHghDc3NDbGFzcwUDSEwzHwAFDE1ha2UgQm9va2luZx4EXyFTQgICZGQCCw8PFgIfAAUJTXkgQmFza2V0ZGQCDQ8PFgQfAAUHRW5xdWlyeR4HVmlzaWJsZWhkZAIPDw8WAh8ABQRIZWxwZGQCEQ9kFgICAQ8PFgQfAAUmQmFza2V0IGxvY2tlZC4gQ2xpY2sgaGVyZSBmb3IgZGV0YWlscy4fA2hkZAIFD2QWCgIBDw8WAh8ABRVTZWFuIEhvZGdlcyAoNjAxNTE0NylkZAIDDxBkZBYAZAIHDw8WAh8ABRRXaWxsaWFtIFBlbm4gTGVpc3VyZWRkAgkPDxYEHghJbWFnZVVybAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9jaGFuZ2V1c2VyLmdpZh8DaGRkAgsPDxYCHwQFIX4vZ3JhcGhpY3MvV1AtZ3JhcGhpY3MvTG9nb3V0LmdpZmRkAgcPZBYEAgEPZBYGAgEPZBYCZg9kFgQCAg9kFgJmDw8WAh8EBSN+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL3Njcl91cF93LmdpZmRkAgMPZBYCZg8PFgIfBAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9zY3JfZG93bl93LmdpZmRkAgUPZBYCZg9kFgQCAg9kFgJmDw8WAh8EBSN+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL3Njcl91cF93LmdpZmRkAgMPZBYCZg8PFgIfBAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9zY3JfZG93bl93LmdpZmRkAgkPZBYCAgIPZBYCZg8PZBYCHgVzdHlsZQUPY3Vyc29yOkRlZmF1bHQ7ZAIDD2QWBgIBD2QWAgIBDw8WBB4FV2lkdGgbAAAAAAAAgEABAAAAHwICgAJkZAICD2QWAgIBDw8WBB8GGwAAAAAAAIBAAQAAAB8CAoACFgIfBWRkAgMPDxYCHwAFGlNhdHVyZGF5LCAwMSBGZWJydWFyeSAyMDE0ZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFHWN0bDAwJFd1Y1N0YXR1c0JhcjEkaW1nTG9nb3V0KfuGxfPhBfWsyzL9xMmDL6Qee68='
    eventvalidation = '/wEWAwLE/ez7AwKes/m8BALkjd6TAXcJExGuzloGKiBfOtb2GhFh2jbc'
    session = AspActionHelper.AspSession(session.sessionid, viewstate, eventvalidation)

    # Get badminton booking data for next week
    url = AspActionHelper.getActionUrl('/MakeBooking.aspx')
    request = AspActionHelper.buildAspAction(session, {
        '__SITEPOSTED' : '',
        '__ACTIVITYPOSTED' : '1000',
        '__SITETOP' : '',
        '__ACTIVITYTOP' : '0',
        '__SITEPOSITIONY' : '',
        '__ACTIVITYPOSITIONY' : '0',
        '__DATECHANGE' : '7',
        '__BOOKCOL' : '-2',
        '__BOOKS' : '-2',
        '__BOOKE' : '-2',
        '__BOOKCOUNT' : '0',
        '__BOOKLOC' : '',
        '__BOOKSUBLOCS' : '',
        '__BOOKFROM' : '',
        '__BOOKTO' : '',
        '__ACTION' : '',
        'ctl00$cphMain$WucBookingSheet1$hfMessage' : ''
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)

    # Find available courts for chosen time
    bookingdata = response.text
    availability = BookingTableDigester.getCourtAvailability(bookingdata, '20:00') # 20:00

    # Pick court in order of preference
    chosencourt = -1
    for i in [0, 3, 2, 1]:
        if availability[i] == True:
            chosencourt = i + 1
            break
    if chosencourt < 1:
        raise Exception('No courts free!')

    # Add to basket
    url = AspActionHelper.getActionUrl('/MakeBooking.aspx')
    request = AspActionHelper.buildAspAction(session, {
        '__SITEPOSTED' : '',
        '__ACTIVITYPOSTED' : '',
        '__SITETOP' : '',
        '__ACTIVITYTOP' : '',
        '__SITEPOSITIONY' : '',
        '__ACTIVITYPOSITIONY' : '',
        '__DATECHANGE' : '7',
        '__BOOKCOL' : str(chosencourt),
        '__BOOKS' : '18', # 20:00
        '__BOOKE' : '19', # 21:00
        '__BOOKCOUNT' : '1',
        '__BOOKLOC' : 'WP01',
        '__BOOKSUBLOCS' : str(chosencourt),
        '__BOOKFROM' : '2000', # 20:00
        '__BOOKTO' : '2100', # 21:00
        '__ACTION' : 'ADDTOBASKET',
        'ctl00$cphMain$WucBookingSheet1$hfMessage' : ''
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)

    basketdata = response.text
    success = BookingTableDigester.checkItemIsInBasket(basketdata)
    if not success:
        raise Exception('Nothing in basket!')
    entry = BookingTableDigester.getItemInBasket(basketdata)

    # Agree to T&Cs and submit basket
    request = AspActionHelper.buildAspAction(session, {
        '__SITE' : '',
        '__BOOKREF' : '',
        '__ACTION' : 'CHECKOUT',
        '__PWD' : 'do4love',
        '__PERSON' : '',
        'ctl00$cphMain$WucBasket1$hfLoginMethod' : 'Standard',
        'ctl00$cphMain$WucBasket1$hfMessage' : '',
        'ctl00$cphMain$WucBasket1$chkTerms' : '1',
        'ctl00$cphMain$WucBasket1$txtPassword' : 'do4love',
        entry : ''
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)

    # Check response to confirm booking
    print response.text

    # Logout
    request = AspActionHelper.buildAspAction(session, {
        '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
        '__EVENTARGUMENT' : '',
        'ctl00$WucStatusBar1$imgLogout.x' : '46',
        'ctl00$WucStatusBar1$imgLogout.y' : '14'
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)

    # Email result of booking
    print "Court %i booked for next Monday, 8pm" % chosencourt

if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        (options, args) = parser.parse_args()
        #if len(args) < 1:
        #    parser.error ('missing argument')
        if options.verbose: print time.asctime()
        main()
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME:',
        if options.verbose: print (time.time() - start_time)
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)

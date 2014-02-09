#!/usr/bin/env python
"""
SYNOPSIS

    book.py [-v,--verbose]

DESCRIPTION

    Books a court at Hertsmere Leisure Centre for the following week.

AUTHOR

    Sean Hodges <seanhodges84@gmail.com>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.
"""

import sys, os, traceback, optparse
import time
import re
import traceback
import requests
from collections import namedtuple
from bs4 import BeautifulSoup
#from pexpect import run, spawn

def HertsmereViewStates(page):
    viewstate = ''
    eventvalidation = ''

    if page == 'Login':
        viewstate = '/wEPDwULLTE5MTM4MzU3MzAPZBYCZg9kFgICAQ9kFggCAQ8WAh4EVGV4dAU4PGltZyBzcmM9ImdyYXBoaWNzL1dQLWdyYXBoaWNzL2xvZ28uZ2lmIiBib3JkZXI9Im5vbmUiLz5kAgMPZBYOAgEPDxYCHwAFBEhvbWVkZAIDDw8WAh8ABQtNeSBTZXR0aW5nc2RkAgcPDxYGHghDc3NDbGFzcwUDSEwzHwAFDE1ha2UgQm9va2luZx4EXyFTQgICZGQCCw8PFgIfAAUJTXkgQmFza2V0ZGQCDQ8PFgQfAAUHRW5xdWlyeR4HVmlzaWJsZWhkZAIPDw8WAh8ABQRIZWxwZGQCEQ9kFgICAQ8PFgQfAAUmQmFza2V0IGxvY2tlZC4gQ2xpY2sgaGVyZSBmb3IgZGV0YWlscy4fA2hkZAIFD2QWCgIBDw8WAh8ABRVTZWFuIEhvZGdlcyAoNjAxNTE0NylkZAIDDxBkZBYAZAIHDw8WAh8ABRRXaWxsaWFtIFBlbm4gTGVpc3VyZWRkAgkPDxYEHghJbWFnZVVybAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9jaGFuZ2V1c2VyLmdpZh8DaGRkAgsPDxYCHwQFIX4vZ3JhcGhpY3MvV1AtZ3JhcGhpY3MvTG9nb3V0LmdpZmRkAgcPZBYEAgEPZBYGAgEPZBYCZg9kFgQCAg9kFgJmDw8WAh8EBSN+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL3Njcl91cF93LmdpZmRkAgMPZBYCZg8PFgIfBAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9zY3JfZG93bl93LmdpZmRkAgUPZBYCZg9kFgQCAg9kFgJmDw8WAh8EBSN+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL3Njcl91cF93LmdpZmRkAgMPZBYCZg8PFgIfBAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9zY3JfZG93bl93LmdpZmRkAgkPZBYCAgIPZBYCZg8PZBYCHgVzdHlsZQUPY3Vyc29yOkRlZmF1bHQ7ZAIDD2QWBgIBD2QWAgIBDw8WBB4FV2lkdGgbAAAAAAAAgEABAAAAHwICgAJkZAICD2QWAgIBDw8WBB8GGwAAAAAAAIBAAQAAAB8CAoACFgIfBWRkAgMPDxYCHwAFGlNhdHVyZGF5LCAwMSBGZWJydWFyeSAyMDE0ZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFHWN0bDAwJFd1Y1N0YXR1c0JhcjEkaW1nTG9nb3V0KfuGxfPhBfWsyzL9xMmDL6Qee68='
        eventvalidation = '/wEWAwLE/ez7AwKes/m8BALkjd6TAXcJExGuzloGKiBfOtb2GhFh2jbc'
    elif page == 'MakeBooking':
        viewstate = '/wEPDwULLTE0MTMzMTQwMjMPZBYCZg9kFgICAQ9kFggCAQ8WAh4EVGV4dAU4PGltZyBzcmM9ImdyYXBoaWNzL1dQLWdyYXBoaWNzL2xvZ28uZ2lmIiBib3JkZXI9Im5vbmUiLz5kAgMPZBYOAgEPDxYGHghDc3NDbGFzcwUDSEwzHwAFBEhvbWUeBF8hU0ICAmRkAgMPDxYCHwAFC015IFNldHRpbmdzZGQCBw8PFgIfAAUMTWFrZSBCb29raW5nZGQCCw8PFgIfAAUJTXkgQmFza2V0ZGQCDQ8PFgQfAAUHRW5xdWlyeR4HVmlzaWJsZWhkZAIPDw8WAh8ABQRIZWxwZGQCEQ9kFgICAQ8PFgIfA2hkZAIFD2QWCgIBDw8WAh8ABRVTZWFuIEhvZGdlcyAoNjAxNTE0NylkZAIDDxBkZBYAZAIHDw8WAh8ABRRXaWxsaWFtIFBlbm4gTGVpc3VyZWRkAgkPDxYEHghJbWFnZVVybAUlfi9ncmFwaGljcy9XUC1ncmFwaGljcy9jaGFuZ2V1c2VyLmdpZh8DaGRkAgsPDxYCHwQFIX4vZ3JhcGhpY3MvV1AtZ3JhcGhpY3MvTG9nb3V0LmdpZmRkAgcPZBYIAgEPDxYCHwAFB1dlbGNvbWVkZAIDDw8WAh8ABSBXaGF0IHdvdWxkIHlvdSBsaWtlIHRvIGRvIHRvZGF5P2RkAgUPZBYCZg8PFgQeBkhlaWdodBsAAAAAAAA+QAEAAAAfAgKAAWRkAgcPZBYCAgEPZBYCZg9kFgJmDw8WBB8FGwAAAAAAAFlAAQAAAB8CAoABFgIeB29uY2xpY2sFNHNob3dNZXNzYWdlKCdjdGwwMF9jcGhNYWluX1d1Y05vdGljZUJvYXJkczFfY3RsMDAnKTtkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYDBR1jdGwwMCRXdWNTdGF0dXNCYXIxJGltZ0xvZ291dAUTY3RsMDAkY3BoTWFpbiRjdGwwNAUTY3RsMDAkY3BoTWFpbiRjdGwwNuwU0m1173NAO8x+vVWF41wG3gx8'
        eventvalidation = '/wEWBgKK87LoCAKes/m8BAL9qeagBAKYk4S2DgKz/KHLCALO5b/gAkkc7k53317LV0FWAHv1fnCBTkYh'
    elif page == 'Basket':
        viewstate = '/wEPDwUKMTk3NjczMDQyNA9kFgJmD2QWAgIBD2QWCAIBDxYCHgRUZXh0BTg8aW1nIHNyYz0iZ3JhcGhpY3MvV1AtZ3JhcGhpY3MvbG9nby5naWYiIGJvcmRlcj0ibm9uZSIvPmQCAw9kFg4CAQ8PFgIfAAUESG9tZWRkAgMPDxYCHwAFC015IFNldHRpbmdzZGQCBw8PFgIfAAUMTWFrZSBCb29raW5nZGQCCw8PFgYeCENzc0NsYXNzBQNITDMfAAUJTXkgQmFza2V0HgRfIVNCAgJkZAINDw8WBB8ABQdFbnF1aXJ5HgdWaXNpYmxlaGRkAg8PDxYCHwAFBEhlbHBkZAIRD2QWAgIBDw8WAh8DaGRkAgUPZBYKAgEPDxYCHwAFFVNlYW4gSG9kZ2VzICg2MDE1MTQ3KWRkAgMPEGRkFgBkAgcPDxYCHwAFFFdpbGxpYW0gUGVubiBMZWlzdXJlZGQCCQ8PFgQeCEltYWdlVXJsBSV+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL2NoYW5nZXVzZXIuZ2lmHwNoZGQCCw8PFgIfBAUhfi9ncmFwaGljcy9XUC1ncmFwaGljcy9Mb2dvdXQuZ2lmZGQCBw9kFgICAQ9kFgQCDQ9kFgJmD2QWAgIIDw8WAh8AZWRkAhEPZBYCAgEPDxYCHwAFMEl0ZW1zIHdpbGwgb25seSBzdGF5IGluIHRoZSBiYXNrZXQgZm9yIDUgbWludXRlc2RkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYCBR1jdGwwMCRXdWNTdGF0dXNCYXIxJGltZ0xvZ291dAUhY3RsMDAkY3BoTWFpbiRXdWNCYXNrZXQxJGNoa1Rlcm1zXsRzQkBrkRsa/ilbLIU0IoxqRLA='
        eventvalidation = '/wEWBwLGhtTAAwKes/m8BAL72p2FCQKLgP+hAQKbtfK5BgKuhuaXBwKx6ZLADNhcGcJx/p0qB2Ia3ZOIAVQ9w9Xw'
    elif page == 'Home':
        viewstate = '/wEPDwUKMTMwNzg2OTQ1Mw9kFgJmD2QWAgIBD2QWCAIBDxYCHgRUZXh0BTg8aW1nIHNyYz0iZ3JhcGhpY3MvV1AtZ3JhcGhpY3MvbG9nby5naWYiIGJvcmRlcj0ibm9uZSIvPmQCAw9kFhACAQ8PFgIfAAUESG9tZWRkAgMPDxYCHwAFC015IFNldHRpbmdzZGQCBQ8PFgQeCENzc0NsYXNzBQNITDMeBF8hU0ICAmRkAgcPDxYCHwAFDE1ha2UgQm9va2luZ2RkAgsPDxYCHwAFCU15IEJhc2tldGRkAg0PDxYEHwAFB0VucXVpcnkeB1Zpc2libGVoZGQCDw8PFgIfAAUESGVscGRkAhEPZBYCAgEPDxYCHwNoZGQCBQ9kFgoCAQ8PFgIfAAUVU2VhbiBIb2RnZXMgKDYwMTUxNDcpZGQCAw8QZGQWAGQCBw8PFgIfAAUUV2lsbGlhbSBQZW5uIExlaXN1cmVkZAIJDw8WBB4ISW1hZ2VVcmwFJX4vZ3JhcGhpY3MvV1AtZ3JhcGhpY3MvY2hhbmdldXNlci5naWYfA2hkZAILDw8WAh8EBSF+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL0xvZ291dC5naWZkZAIHD2QWAgIBD2QWBAIlDw8WAh8EBSN+L2dyYXBoaWNzL1dQLWdyYXBoaWNzL3Njcl91cF93LmdpZmRkAicPDxYCHwQFJX4vZ3JhcGhpY3MvV1AtZ3JhcGhpY3Mvc2NyX2Rvd25fdy5naWZkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUdY3RsMDAkV3VjU3RhdHVzQmFyMSRpbWdMb2dvdXQ908KTklcBh4vH2meu6t8frDRUFw=='
        eventvalidation = '/wEWBQLA1ZRjAp6z+bwEAoT6nbMIApWY9p8GAtjjqHJe6+bEkxqzZDJ0JX3lmWMt0Yu0Zg=='
    elif page == 'Fake':
        viewstate = '/wEPDwUJNDY='
        eventvalidation = '/wEWBgKCxaiC='

    return { 'viewstate' : viewstate, 'eventvalidation' : eventvalidation }

class AspActionHelper:

    AspRequest = namedtuple('AspRequest', 'cookies payload')

    @staticmethod
    def getActionUrl(path):
        return 'https://www.hertsmereleisurebookings.co.uk/Horizons/' + path

    @staticmethod
    def getSessionId(r):
        val = r.cookies['ASP.NET_SessionId']
        return val

    @staticmethod
    def parseViewState(r):
        viewstate = re.search('__VIEWSTATE" value="(.*)"', r.text).group(1)
        eventvalidation = re.search('__EVENTVALIDATION" value="(.*)"', r.text).group(1)
        return { 'viewstate' : viewstate, 'eventvalidation' : eventvalidation }

    @staticmethod
    def getViewState(page):
        return HertsmereViewStates(page)

    @staticmethod
    def buildAspAction(session, viewstate, args):
        cookies = {
            'ASP.NET_SessionId' : session
        }
        payload = {
            '__VIEWSTATE' : viewstate['viewstate'],
            '__EVENTVALIDATION' : viewstate['eventvalidation']
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

    # Initialise session
    url = AspActionHelper.getActionUrl('/Login/Default.aspx?regionid=4')
    viewstate = AspActionHelper.getViewState('Login')
    response = requests.get(url)
    session = AspActionHelper.getSessionId(response)

    # Login to site
    request = AspActionHelper.buildAspAction(session, viewstate, {
        '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
        '__EVENTARGUMENT' : '',
        'ctl00$cphLogin$txtEmail' : 'seanhodges84@gmail.com',
        'ctl00$cphLogin$txtPassword' : 'do4love'
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)

    try:
        # Get badminton booking data for next week
        url = AspActionHelper.getActionUrl('/MakeBooking.aspx')
        viewstate = AspActionHelper.getViewState('MakeBooking')
        request = AspActionHelper.buildAspAction(session, viewstate, {
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
        viewstate = AspActionHelper.getViewState('MakeBooking')
        request = AspActionHelper.buildAspAction(session, viewstate, {
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
        url = AspActionHelper.getActionUrl('/Basket.aspx')
        viewstate = AspActionHelper.getViewState('Basket')
        request = AspActionHelper.buildAspAction(session, viewstate, {
            '__SITE' : '',
            '__BOOKREF' : '',
            '__ACTION' : 'CHECKOUT',
            '__PWD' : 'do4love',
            '__PERSON' : '',
            'ctl00$cphMain$WucBasket1$hfLoginMethod' : 'Standard',
            'ctl00$cphMain$WucBasket1$hfMessage' : '',
            'ctl00$cphMain$WucBasket1$chkTerms' : 'on',
            'ctl00$cphMain$WucBasket1$txtPassword' : 'do4love',
            entry : ''
        })
        response = requests.post(url, data=request.payload, cookies=request.cookies)

        # Check response to confirm booking
        print response.text

        # Email result of booking
        print "Court %i booked for next Monday, 8pm" % chosencourt

    except Exception as e:
        print 'There was a problem with the booking process, could not complete booking'
        print traceback.format_exc()

    finally:
        # Logout
        viewstate = AspActionHelper.getViewState('Login')
        request = AspActionHelper.buildAspAction(session, viewstate, {
            '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
            '__EVENTARGUMENT' : '',
            'ctl00$WucStatusBar1$imgLogout.x' : '46',
            'ctl00$WucStatusBar1$imgLogout.y' : '14'
        })
        response = requests.post(url, data=request.payload, cookies=request.cookies)

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

#!/usr/bin/env python
"""
SYNOPSIS

    book.py [-v,--verbose,-t,--test]

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
import logging
import requests
from collections import namedtuple
from bs4 import BeautifulSoup
#from pexpect import run, spawn

class AspActionHelper:

    AspRequest = namedtuple('AspRequest', 'cookies payload')

    @staticmethod
    def getActionUrl(path):
        return 'https://www.hertsmereleisurebookings.co.uk/Horizons' + path

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
    def getViewState(session, url):
        out = {}

        if url == 'Fake':
            viewstate = '/wEPDwUJNDY='
            eventvalidation = '/wEWBgKCxaiC='
            out = { 'viewstate' : viewstate, 'eventvalidation' : eventvalidation }
        else:
            response = requests.get(url, cookies={
                'ASP.NET_SessionId' : session
            })
            out = AspActionHelper.parseViewState(response)

        return out

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

    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
    logger = logging.getLogger('book')

    # Initialise session
    logger.info('Initialising session')
    url = AspActionHelper.getActionUrl('/Login/Default.aspx?regionid=4')
    response = requests.get(url)
    session = AspActionHelper.getSessionId(response)

    # Login to site
    logger.info('Logging into site')
    request = AspActionHelper.buildAspAction(session, viewstate, {
        '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
        '__EVENTARGUMENT' : '',
        'ctl00$cphLogin$txtEmail' : 'seanhodges84@gmail.com',
        'ctl00$cphLogin$txtPassword' : 'do4love'
    })
    response = requests.post(url, data=request.payload, cookies=request.cookies)
    if response.status_code != 200:
        logger.error('Login failed with status %i, response body follows:', response.status_code)
        logger.error(response.text)
        raise Exception('Login failed!')

    try:
        # Get badminton booking data for next week
        logger.info('Retriving booking data for next week')
        url = AspActionHelper.getActionUrl('/MakeBooking.aspx')
        viewstate = AspActionHelper.getViewState(session, url)
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
        logger.debug(response.text)

        # Find available courts for chosen time
        logger.info('Finding available courts')
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
        logger.info('Chosen court is %i', chosencourt)

        if not options.test:
            # Add to basket
            logger.info('Adding to basket')
            url = AspActionHelper.getActionUrl('/MakeBooking.aspx')
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
            logger.info('Submitting basket')
            url = AspActionHelper.getActionUrl('/Basket.aspx')
            viewstate = AspActionHelper.getViewState(session, url)
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
            logger.debug(response.text)

            # Check response to confirm booking

        # Email result of booking
        logger.info("Court %i booked for next Monday, 8pm", chosencourt)

    except Exception as e:
        logger.error('There was a problem with the booking process, could not complete booking')
        logger.error(e)
        print traceback.format_exc()

    finally:
        # Logout
        viewstate = AspActionHelper.getViewState(session, url)
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
        parser.add_option ('-t', '--test-run', action='store_true', default=False, help='test script with fake booking')
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

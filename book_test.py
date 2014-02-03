#!/usr/bin/env python
#
#  Test the booking flow
#
#===============
#  This is based on a skeleton test file, more information at:
#
#     https://github.com/linsomniac/python-unittest-skeleton

import unittest
import requests

import re
import os
import sys
from bs4 import BeautifulSoup
import sqlite3
from collections import namedtuple

sys.path.append('.')
from book import AspActionHelper, BookingTableDigester

class FakeResponse():
    text = ''
    cookies = {}

class test_Asp_Action_Helper(unittest.TestCase):
    def assertContains(self, stack, needle):
        self.assertNotEqual(-1, stack.find(needle))

    def test_Gets_Action_Url_For_Login(self):
        expected = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Login/Default.aspx?regionid=4'
        url = AspActionHelper.getActionUrl('Login/Default.aspx?regionid=4')
        self.assertEqual(url, expected)

    def test_Gets_Action_Url_For_Booking(self):
        expected = 'https://www.hertsmereleisurebookings.co.uk/Horizons/MakeBooking.aspx'
        url = AspActionHelper.getActionUrl('MakeBooking.aspx')
        self.assertEqual(url, expected)

    def test_Gets_Action_Url_For_Basket(self):
        expected = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Basket.aspx'
        url = AspActionHelper.getActionUrl('Basket.aspx')
        self.assertEqual(url, expected)

    def test_Gets_Session_Id(self):
        r = FakeResponse()
        r.cookies = {
            'ASP.NET_SessionId' : '12345'
        }
        sessionid = AspActionHelper.getSessionId(r)
        self.assertEqual(sessionid, '12345')

    def test_Scrapes_ViewState_From_Page(self):
        r = FakeResponse()
        r.text = open('test/Default.aspx', 'r').read()
        viewstate = AspActionHelper.parseViewState(r)
        self.assertEqual(viewstate['viewstate'], '/wEPDwUJNDY=')
        self.assertEqual(viewstate['eventvalidation'], '/wEWBgKCxaiC=')

    def test_Gets_Mapped_ViewState_For_Fake_Page(self):
        page = 'Fake'
        viewstate = AspActionHelper.getViewState(page)
        self.assertEqual(viewstate['viewstate'], '/wEPDwUJNDY=')
        self.assertEqual(viewstate['eventvalidation'], '/wEWBgKCxaiC=')

    def test_Builds_Login_Asp_Action(self):
        session = '12345'
        viewstate = { 'viewstate' : '/wEPDwUJNDY=', 'eventvalidation' : '/wEWBgKCxaiC=' }
        request = AspActionHelper.buildAspAction(session, viewstate, {
            '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
            '__EVENTARGUMENT' : '',
            'ctl00$cphLogin$txtEmail' : 'seanhodges84@gmail.com',
            'ctl00$cphLogin$txtPassword' : 'do4love'
        })

        cookies = {
            'ASP.NET_SessionId' : '12345'
        }
        self.assertEqual(request.cookies, cookies)

        payload = {
            '__VIEWSTATE' : '/wEPDwUJNDY=',
            '__EVENTVALIDATION' : '/wEWBgKCxaiC=',
            '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
            '__EVENTARGUMENT' : '',
            'ctl00$cphLogin$txtEmail' : 'seanhodges84@gmail.com',
            'ctl00$cphLogin$txtPassword' : 'do4love'
        }
        self.assertEqual(request.payload, payload)

    def test_Builds_MakeBooking_Asp_Action(self):
        session = '12345'
        viewstate = { 'viewstate' : '/wEPDwUJNDY=', 'eventvalidation' : '/wEWBgKCxaiC=' }
        request = AspActionHelper.buildAspAction(session, viewstate, {
            '__SITEPOSTED' : '',
            '__ACTIVITYPOSTED' : '',
            '__SITETOP' : '',
            '__ACTIVITYTOP' : '',
            '__SITEPOSITIONY' : '',
            '__ACTIVITYPOSITIONY' : '',
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

        cookies = {
            'ASP.NET_SessionId' : '12345'
        }
        self.assertEqual(request.cookies, cookies)

        payload = {
            '__VIEWSTATE' : '/wEPDwUJNDY=',
            '__EVENTVALIDATION' : '/wEWBgKCxaiC=',
            '__SITEPOSTED' : '',
            '__ACTIVITYPOSTED' : '',
            '__SITETOP' : '',
            '__ACTIVITYTOP' : '',
            '__SITEPOSITIONY' : '',
            '__ACTIVITYPOSITIONY' : '',
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
        }
        self.assertEqual(request.payload, payload)

    def test_Builds_Add_To_Basket_Asp_Action(self):
        session = '12345'
        viewstate = { 'viewstate' : '/wEPDwUJNDY=', 'eventvalidation' : '/wEWBgKCxaiC=' }
        request = AspActionHelper.buildAspAction(session, viewstate, {
            '__SITEPOSTED' : '',
            '__ACTIVITYPOSTED' : '',
            '__SITETOP' : '',
            '__ACTIVITYTOP' : '',
            '__SITEPOSITIONY' : '',
            '__ACTIVITYPOSITIONY' : '',
            '__DATECHANGE' : '7',
            '__BOOKCOL' : '1',
            '__BOOKS' : '22',
            '__BOOKE' : '23',
            '__BOOKCOUNT' : '1',
            '__BOOKLOC' : 'WP01',
            '__BOOKSUBLOCS' : '1',
            '__BOOKFROM' : '1830',
            '__BOOKTO' : '1930',
            '__ACTION' : 'ADDTOBASKET',
            'ctl00$cphMain$WucBookingSheet1$hfMessage' : ''
        })

        cookies = {
            'ASP.NET_SessionId' : '12345'
        }
        self.assertEqual(request.cookies, cookies)

        payload = {
            '__VIEWSTATE' : '/wEPDwUJNDY=',
            '__EVENTVALIDATION' : '/wEWBgKCxaiC=',
            '__SITEPOSTED' : '',
            '__ACTIVITYPOSTED' : '',
            '__SITETOP' : '',
            '__ACTIVITYTOP' : '',
            '__SITEPOSITIONY' : '',
            '__ACTIVITYPOSITIONY' : '',
            '__DATECHANGE' : '7',
            '__BOOKCOL' : '1',
            '__BOOKS' : '22',
            '__BOOKE' : '23',
            '__BOOKCOUNT' : '1',
            '__BOOKLOC' : 'WP01',
            '__BOOKSUBLOCS' : '1',
            '__BOOKFROM' : '1830',
            '__BOOKTO' : '1930',
            '__ACTION' : 'ADDTOBASKET',
            'ctl00$cphMain$WucBookingSheet1$hfMessage' : ''
        }
        self.assertEqual(request.payload, payload)

    def test_Builds_Checkout_Asp_Action(self):
        entry = 'ctl00$cphMain$WucBasket1$HIDDENREF_6_50993_E_Badminton_9.2500'

        session = '12345'
        viewstate = { 'viewstate' : '/wEPDwUJNDY=', 'eventvalidation' : '/wEWBgKCxaiC=' }
        request = AspActionHelper.buildAspAction(session, viewstate, {
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

        cookies = {
            'ASP.NET_SessionId' : '12345'
        }
        self.assertEqual(request.cookies, cookies)

        payload = {
            '__VIEWSTATE' : '/wEPDwUJNDY=',
            '__EVENTVALIDATION' : '/wEWBgKCxaiC=',
            '__SITE' : '',
            '__BOOKREF' : '',
            '__ACTION' : 'CHECKOUT',
            '__PWD' : 'do4love',
            '__PERSON' : '',
            'ctl00$cphMain$WucBasket1$hfLoginMethod' : 'Standard',
            'ctl00$cphMain$WucBasket1$hfMessage' : '',
            'ctl00$cphMain$WucBasket1$chkTerms' : '1',
            'ctl00$cphMain$WucBasket1$txtPassword' : 'do4love',
            'ctl00$cphMain$WucBasket1$HIDDENREF_6_50993_E_Badminton_9.2500' : ''
        }
        self.assertEqual(request.payload, payload)

    def test_Builds_Logout_Asp_Action(self):
        session = '12345'
        viewstate = { 'viewstate' : '/wEPDwUJNDY=', 'eventvalidation' : '/wEWBgKCxaiC=' }
        request = AspActionHelper.buildAspAction(session, viewstate, {
            '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
            '__EVENTARGUMENT' : '',
            'ctl00$WucStatusBar1$imgLogout.x' : '46',
            'ctl00$WucStatusBar1$imgLogout.y' : '14'
        })

        cookies = {
            'ASP.NET_SessionId' : '12345'
        }
        self.assertEqual(request.cookies, cookies)

        payload = {
            '__VIEWSTATE' : '/wEPDwUJNDY=',
            '__EVENTVALIDATION' : '/wEWBgKCxaiC=',
            '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
            '__EVENTARGUMENT' : '',
            'ctl00$WucStatusBar1$imgLogout.x' : '46',
            'ctl00$WucStatusBar1$imgLogout.y' : '14'
        }
        self.assertEqual(request.payload, payload)


class test_Booking_Table_Digester(unittest.TestCase):

    def test_Gets_Booking_Data_From_Html(self):
        # Digest the HTML
        data = open('test/MakeBooking.aspx', 'r').read()
        soup = BeautifulSoup(data)

        # Grab the booking table
        bookingtable = soup.find(id='ctl00_cphMain_WucBookingSheet1_tabBookingGrid').find_all('tr')
        self.assertEqual(len(bookingtable), 26)

    def test_Eight_Pm_Is_Fully_Booked(self):
        # Digest the HTML
        data = open('test/MakeBooking.aspx', 'r').read()
        courts = BookingTableDigester.getCourtAvailability(data, '20:00')
        self.assertFalse(courts[0])
        self.assertFalse(courts[1])
        self.assertFalse(courts[2])
        self.assertFalse(courts[3])

    def test_Twelve_Pm_Has_Free_Slots_On_Court_One_And_Two(self):
        # Digest the HTML
        data = open('test/MakeBooking.aspx', 'r').read()
        courts = BookingTableDigester.getCourtAvailability(data, '12:00')
        self.assertTrue(courts[0])
        self.assertTrue(courts[1])
        self.assertFalse(courts[2])
        self.assertFalse(courts[3])

    def test_Store_Booking_Data_In_Database(self):
        def bookingDataGenerator(rows):
            for row in rows:
                cells = row.find_all('td')
                court = []
                for cell in cells:
                    if cell['class'][0] == 'TD12':
                        # Skip the time cells
                        continue
                    elif cell['class'][0] == 'TD7':
                        # Available slot
                        court.append(1)
                    else:
                        # Booked slot
                        court.append(0)
                yield (cells[0].text, court[0], court[1], court[2], court[3])

        # Digest the HTML
        data = open('test/MakeBooking.aspx', 'r').read()
        soup = BeautifulSoup(data)

        # Grab the booking table
        rows = soup.find(id='ctl00_cphMain_WucBookingSheet1_tabBookingGrid').find_all('tr')

        db = sqlite3.connect(':memory:')
        db.execute('''CREATE TABLE booking_data (
            time TEXT,
            court1 INTEGER,
            court2 INTEGER,
            court3 INTEGER,
            court4 INTEGER)''')
        db.executemany('''
            INSERT INTO booking_data (time, court1, court2, court3, court4)
            VALUES (?,?,?,?,?)''', bookingDataGenerator(rows))
        db.commit()

        c = db.execute('SELECT court1, court2, court3, court4 FROM booking_data WHERE time="12:00"')
        result = c.fetchone()
        # 1 = available, 0 = booked
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], 1)
        self.assertEqual(result[2], 0)
        self.assertEqual(result[3], 0)

unittest.main()

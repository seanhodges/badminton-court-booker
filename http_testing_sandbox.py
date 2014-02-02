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
sys.path.append('.')

class test_Logging_In(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertContains(self, stack, needle):
        self.assertNotEqual(-1, stack.find(needle))

    @unittest.skipIf('SKIP_SLOW_TESTS' in os.environ, 'Requested fast tests')
    def test_Hit_Login_Page(self):
        url = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Login/Default.aspx?regionid=4'
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r.text, 'Log On')

    @unittest.skipIf('SKIP_SLOW_TESTS' in os.environ, 'Requested fast tests')
    def test_Login_Request(self):
        url = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Login/Default.aspx?regionid=4'
        r = requests.get(url)

        # Grab the VIEWSTATE, EVENTVALIDATION and cookie
        sessionid = r.cookies['ASP.NET_SessionId']
        self.assertEqual(len(sessionid), 24)
        viewstate = re.search('__VIEWSTATE" value="(.*)"', r.text).group(1)
        self.assertEqual(len(viewstate), 436)
        eventvalidation = re.search('__EVENTVALIDATION" value="(.*)"', r.text).group(1)
        self.assertEqual(len(eventvalidation), 80)
        self.assertNotEqual(eventvalidation, viewstate)

        # Build the packet
        cookies = {
                'ASP.NET_SessionId' : sessionid
                }
        payload = {
                '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
                '__EVENTARGUMENT' : '',
                '__VIEWSTATE' : viewstate,
                '__EVENTVALIDATION' : eventvalidation,
                'ctl00$cphLogin$txtEmail' : 'seanhodges84@gmail.com',
                'ctl00$cphLogin$txtPassword' : 'do4love'
                }

        # Attempt the login request
        url = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Login/Default.aspx?regionid=4'
        r = requests.post(url, data=payload, cookies=cookies)

        # Were we successful?
        self.assertEqual(r.status_code, 200)
        self.assertContains(r.text, 'Sean Hodges')

        # Log back out
        cookies = {
                'ASP.NET_SessionId' : sessionid
                }
        payload = {
                '__EVENTTARGET' : 'ctl00$cphLogin$hlLogon',
                '__EVENTARGUMENT' : '',
                '__VIEWSTATE' : viewstate,
                '__EVENTVALIDATION' : eventvalidation,
                'ctl00$WucStatusBar1$imgLogout.x' : '46',
                'ctl00$WucStatusBar1$imgLogout.y' : '14'
                }

        url = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Login/Default.aspx?regionid=4'
        r = requests.post(url, data=payload, cookies=cookies)

        self.assertEqual(r.status_code, 200)
        self.assertContains(r.text, 'Log On')

unittest.main()

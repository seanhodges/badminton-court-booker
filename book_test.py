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

class test_Asp_Action_Helper(unittest.TestCase):
    def assertContains(self, stack, needle):
        self.assertNotEqual(-1, stack.find(needle))

    def test_Gets_Action_Url(self):
        url = 'https://www.hertsmereleisurebookings.co.uk/Horizons/Login/Default.aspx?regionid=4'
        target = url
        self.assertEqual(target, url)

    def test_Gets_Session_Id(self):
        sessionid = r.cookies['ASP.NET_SessionId']
        self.assertEqual(len(sessionid), 24)

    def test_Gets_Event_Validation(self):
        eventvalidation = re.search('__EVENTVALIDATION" value="(.*)"', r.text).group(1)
        self.assertEqual(len(eventvalidation), 80)
        self.assertNotEqual(eventvalidation, viewstate)

    def test_Gets_View_State(self):
        viewstate = re.search('__VIEWSTATE" value="(.*)"', r.text).group(1)
        self.assertEqual(len(viewstate), 436)

    def test_Builds_Asp_Action(self):
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

unittest.main()

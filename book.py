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
#from pexpect import run, spawn

def main ():
    global options, args

    # Initialise session and grab keys
    # Login to site
    # Get badminton booking data for next week
    # Parse available slots (slots x courts)
    # Find available courts for chosen time
    # Pick court in order of preference
    # Add to basket
    # Agree to T&Cs and submit basket
    # Check response to confirm booking
    # Email result of booking

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

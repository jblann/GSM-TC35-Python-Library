#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Automatic test of GSMTC35 library (not complete and without MOCK => not perfect at all)
  Feel free to create mock test for better unit-test.
"""

import unittest
from GSMTC35 import GSMTC35
from unittest.mock import patch
import logging
import re
import datetime
import time

class MockSerial:
  """
  TODO: Explanation of the class + functions
  """
  __is_open = True
  __read_write = []
  __timestamp_begin_delay = None

  __default_serial_for_setup = [
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: READY\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ]

  @staticmethod
  def getDefaultConfigForSetup():
    return MockSerial.__default_serial_for_setup + []

  @staticmethod
  def initializeMock(read_write, is_open = True):
    MockSerial.__is_open = is_open
    MockSerial.__read_write = read_write

  def __init__(self, port="", baudrate="", parity="", stopbits="", bytesize="", timeout=""):
    return

  def inWaiting(self):
    if MockSerial.__is_open and len(MockSerial.__read_write) > 0:
      if 'OUT' in MockSerial.__read_write[0]:
        if 'wait_ms' in MockSerial.__read_write[0]:
          if MockSerial.__timestamp_begin_delay == None:
            MockSerial.__timestamp_begin_delay = 1000*time.time()
          elif MockSerial.__timestamp_begin_delay + int(MockSerial.__read_write[0]['wait_ms']) > 1000*time.time():
            return 0
          else:
            MockSerial.__timestamp_begin_delay = None
        return len(MockSerial.__read_write[0]['OUT'])
    return 0

  def read(self, dummy):
    if MockSerial.__is_open and len(MockSerial.__read_write) > 0:
      if 'OUT' in MockSerial.__read_write[0]:
        if 'wait_ms' in MockSerial.__read_write[0]:
          if MockSerial.__timestamp_begin_delay == None:
            MockSerial.__timestamp_begin_delay = 1000*time.time()
          elif MockSerial.__timestamp_begin_delay + int(MockSerial.__read_write[0]['wait_ms']) > 1000*time.time():
            return 0
          else:
            MockSerial.__timestamp_begin_delay = None
        val = MockSerial.__read_write[0]['OUT']
        MockSerial.__read_write.pop(0)
        return val
    return ""

  def write(self, data):
    if MockSerial.__is_open and len(MockSerial.__read_write) > 0:
      if 'IN' in MockSerial.__read_write[0]:
        check_val = MockSerial.__read_write[0]['IN']

        test_mode = "strict_compare"
        if 'mode' in MockSerial.__read_write[0]:
          test_mode = MockSerial.__read_write[0]["mode"]

        if test_mode == "strict_compare":
          if str(data) != str(check_val):
            raise AssertionError('Mock Serial: Should write "' + str(check_val) + '" but "'+str(data)+'" requested (strict compare)')
        elif test_mode == "regex":
          if not re.search(check_val, data):
            raise AssertionError('Mock Serial: Should write "' + str(check_val) + '" but "'+str(data)+'" requested (regex compare)')
        else:
          raise AssertionError('Mock Serial: Invalid test_mode (should be "regex" or "strict_compare" (default)')

        MockSerial.__read_write.pop(0)
        return len(data)
    return 0

  def isOpen(self):
    return MockSerial.__is_open

  def close(self):
    return True

class TestGSMTC35(unittest.TestCase):
  """
  TODO: Explanation of the class + functions
  """
  # TODO: Add more case and use mock
  def test_fail_cmd(self):
    logging.debug("test_fail_cmd")
    # Request failed because nothing requested
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((['--baudrate', '115200', '--serialPort', 'COM_Invalid', '--pin', '1234', '--puk', '12345678', '--pin2', '1234', '--puk2', '12345678', '--nodebug', '--debug']))
    self.assertNotEqual(cm.exception.code, 0)

    # Request failed because invalid argument
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((['--undefinedargument']))
    self.assertNotEqual(cm.exception.code, 0)

  # TODO: Add more case and use mock
  def test_all_cmd_help(self):
    logging.debug("test_all_cmd_help")
    # No paramaters
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main()
    self.assertNotEqual(cm.exception.code, 0)

    # Request basic help
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help"]))
    self.assertEqual(cm.exception.code, 0)

    # Request extended help
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "help"]))
    self.assertEqual(cm.exception.code, 0)

    # Request extended help
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "baudrate"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "serialport"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "pin"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "puk"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "pin2"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "puk2"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "isalive"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "call"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "hangupcall"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "issomeonecalling"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "pickupcall"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "sendsms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "sendencodedsms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "sendtextmodesms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "getsms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "getencodedsms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "gettextmodesms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "deletesms"]))
    self.assertEqual(cm.exception.code, 0)
    with self.assertRaises(SystemExit) as cm:
      GSMTC35.main((["--help", "information"]))
    self.assertEqual(cm.exception.code, 0)

  @patch('serial.Serial', new=MockSerial)
  def test_fail_setup(self):
    logging.debug("test_fail_setup")
    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: READY\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678"))

  @patch('serial.Serial', new=MockSerial)
  def test_success_setup(self):
    logging.debug("test_success_setup")
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: READY\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'ERROR\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

  @patch('serial.Serial', new=MockSerial)
  def test_success_pin_during_setup(self):
    logging.debug("test_success_pin_during_setup")
    # Entered PIN/PUK/PIN2/PUK2
    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PUK2\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=87654321\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PIN2\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=4321\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PUK\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=12345678\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PIN\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=1234\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: READY\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678", _pin2="4321", _puk2="87654321"))

    # No PIN/PUK/PIN2/PUK2 specified in entry (bypassing)
    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PUK2\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PIN2\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PUK\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PIN\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

  @patch('serial.Serial', new=MockSerial)
  def test_fail_pin_during_setup(self):
    logging.debug("test_fail_pin_during_setup")
    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PUK2\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=87654321\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678", _pin2="4321", _puk2="87654321"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PIN2\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=4321\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678", _pin2="4321", _puk2="87654321"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PUK\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=12345678\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678", _pin2="4321", _puk2="87654321"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: SIM PIN\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN=1234\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678", _pin2="4321", _puk2="87654321"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CPIN?\r\n'}, {'OUT': b'+CPIN: UNDEFINED\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    gsm = GSMTC35.GSMTC35()
    self.assertFalse(gsm.setup(_port="COM_FAKE", _pin="1234", _puk="12345678", _pin2="4321", _puk2="87654321"))

  @patch('serial.Serial', new=MockSerial)
  def test_all_change_baudrate(self):
    logging.debug("test_all_change_baudrate")
    gsm = GSMTC35.GSMTC35()

    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup() + [{'IN': b'AT+IPR=9600\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.changeBaudrateMode(115200, 9600, "COM_FAKE"))

    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup() + [{'IN': b'AT+IPR=9600\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.changeBaudrateMode(115200, 9600, "COM_FAKE"))

    MockSerial.initializeMock([
      {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATE0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'ATV1\r\n'}, {'OUT': b'ERROR\r\n'},
      {'IN': b'AT+CMEE=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'},
      {'IN': b'AT+IPR=115200\r\n'}, {'OUT': b'OK\r\n'}
    ])
    self.assertFalse(gsm.changeBaudrateMode(115200, 9600, "COM_FAKE"))

  @patch('serial.Serial', new=MockSerial)
  def test_all_is_initialized(self):
    logging.debug("test_fail_pin_during_setup")
    gsm = GSMTC35.GSMTC35()

    MockSerial.initializeMock([])
    self.assertFalse(gsm.isInitialized())

    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([])
    self.assertTrue(gsm.isInitialized())

  @patch('serial.Serial', new=MockSerial)
  def test_all_close(self):
    logging.debug("test_all_close")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock([{'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.close(), None)
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))
    MockSerial.initializeMock([{'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.close(), None)

  @patch('serial.Serial', new=MockSerial)
  def test_all_reboot(self):
    logging.debug("test_all_reboot")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CFUN=1,1\r\n'}, {'OUT': b'OK\r\n'},
                               {'OUT': b'... Rebooting ...\r\n'}, {'OUT': b'^SYSSTART\r\n'},
                               {'IN': b'AT+IPR=0\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.reboot())

    MockSerial.initializeMock([{'IN': b'AT+CFUN=1,1\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.reboot())

  @patch('serial.Serial', new=MockSerial)
  def test_all_is_alive(self):
    logging.debug("test_all_is_alive")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.isAlive())

    MockSerial.initializeMock([{'IN': b'AT\r\n'}])
    self.assertFalse(gsm.isAlive())

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_manufacturer_id(self):
    logging.debug("test_all_get_manufacturer_id")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CGMI\r\n'}, {'OUT': b'FAKE_MANUFACTURER\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(str(gsm.getManufacturerId()), "FAKE_MANUFACTURER")

    MockSerial.initializeMock([{'IN': b'AT+CGMI\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getManufacturerId()), "")

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_model_id(self):
    logging.debug("test_all_get_model_id")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CGMM\r\n'}, {'OUT': b'FAKE_MODEL\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(str(gsm.getModelId()), "FAKE_MODEL")

    MockSerial.initializeMock([{'IN': b'AT+CGMM\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getModelId()), "")

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_revision_id(self):
    logging.debug("test_all_get_revision_id")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CGMR\r\n'}, {'OUT': b'FAKE_REVISION\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(str(gsm.getRevisionId()), "FAKE_REVISION")

    MockSerial.initializeMock([{'IN': b'AT+CGMR\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getRevisionId()), "")

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_imei(self):
    logging.debug("test_all_get_imei")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CGSN\r\n'}, {'OUT': b'FAKE_IMEI\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(str(gsm.getIMEI()), "FAKE_IMEI")

    MockSerial.initializeMock([{'IN': b'AT+CGSN\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getIMEI()), "")

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_imsi(self):
    logging.debug("test_all_get_imsi")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CIMI\r\n'}, {'OUT': b'FAKE_IMSI\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(str(gsm.getIMSI()), "FAKE_IMSI")

    MockSerial.initializeMock([{'IN': b'AT+CIMI\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getIMSI()), "")

  @patch('serial.Serial', new=MockSerial)
  def test_all_set_module_to_manufacturer_state(self):
    logging.debug("test_all_set_module_to_manufacturer_state")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT&F0\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setModuleToManufacturerState())

    MockSerial.initializeMock([{'IN': b'AT&F0\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.setModuleToManufacturerState())

  @patch('serial.Serial', new=MockSerial)
  def test_all_switch_off(self):
    logging.debug("test_all_switch_off")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT^SMSO\r\n'}, {'OUT': b'MS OFF\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.switchOff())

    MockSerial.initializeMock([{'IN': b'AT^SMSO\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.switchOff())

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_operator_name(self):
    logging.debug("test_all_get_operator_name")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+COPS=3,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+COPS?\r\n'}, {'OUT': b'+COPS: 0,1,\"FAKE_OPERATOR\"\r\n'},
                               {'OUT': b'OK\r\n'}])
    self.assertEqual(str(gsm.getOperatorName()), "FAKE_OPERATOR")

    MockSerial.initializeMock([{'IN': b'AT+COPS=3,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+COPS?\r\n'}, {'OUT': b'+COPS: \"FAKE_OPERATOR\"\r\n'}])
    self.assertEqual(str(gsm.getOperatorName()), "")

    MockSerial.initializeMock([{'IN': b'AT+COPS=3,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+COPS?\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getOperatorName()), "")

    MockSerial.initializeMock([{'IN': b'AT+COPS=3,0\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(str(gsm.getOperatorName()), "")

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_signal_strength(self):
    logging.debug("test_all_get_signal_strength")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CSQ\r\n'}, {'OUT': b'+CSQ: 60,USELESS\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getSignalStrength(), 7)

    MockSerial.initializeMock([{'IN': b'AT+CSQ\r\n'}, {'OUT': b'+CSQ: 100,USELESS\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getSignalStrength(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CSQ\r\n'}, {'OUT': b'+CSQ: -1,USELESS\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getSignalStrength(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CSQ\r\n'}, {'OUT': b'+CSQ: \r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getSignalStrength(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CSQ\r\n'}, {'OUT': b'+CSQ: WRONG,USELESS\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getSignalStrength(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CSQ\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getSignalStrength(), -1)

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_operator_names(self):
    logging.debug("test_all_get_operator_names")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+COPN\r\n'}, {'OUT': b'+COPN: 1,\"FAKE1\"\r\n'},
                               {'OUT': b'+COPN: 2,\"FAKE 2\"\r\n'}, {'OUT': b'+COPN: 3,\"Fake Three\"\r\n'},
                               {'OUT': b'+COPN: DUMMY_ERROR\r\n'},{'OUT': b'DUMMY_ERROR\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getOperatorNames(), ["FAKE1", "FAKE 2", "Fake Three"])

    MockSerial.initializeMock([{'IN': b'AT+COPN\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getOperatorNames(), [])

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_neighbour_cells(self):
    logging.debug("test_all_get_neighbour_cells")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT^MONP\r\n'},
                               {'OUT': b'chann rs  dBm   PLMN   BCC C1 C2\r\n'},
                               {'OUT': b'504   18  -78   26203  1   27 28\r\n'},
                               {'OUT': b'505   19  -77   26204  2   28 29\r\n'},
                               {'OUT': b'Inva  lid param eters  he  r  e \r\n'}, # Invalid parameters
                               {'OUT': b'1     2   3     4      5\r\n'},         # Invalid number of parameters
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getNeighbourCells(), [{"chann": 504, "rs": 18, "dbm": -78, "plmn": 26203, "bcc": 1, "c1": 27, "c2": 28},
                                               {"chann": 505, "rs": 19, "dbm": -77, "plmn": 26204, "bcc": 2, "c1": 28, "c2": 29}])

    MockSerial.initializeMock([{'IN': b'AT^MONP\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getNeighbourCells(), [])

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_accumulated_call_meter(self):
    logging.debug("test_all_get_accumulated_call_meter")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CACM?\r\n'}, {'OUT': b'+CACM: FF05\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getAccumulatedCallMeter(), 0xFF05)

    MockSerial.initializeMock([{'IN': b'AT+CACM?\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getAccumulatedCallMeter(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CACM?\r\n'}, {'OUT': b'+CACM: INVALID_NUMBER\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getAccumulatedCallMeter(), -1)

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_accumulated_call_meter_maximum(self):
    logging.debug("test_all_get_accumulated_call_meter_maximum")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CAMM?\r\n'}, {'OUT': b'+CAMM: FFFF\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getAccumulatedCallMeterMaximum(), 0xFFFF)

    MockSerial.initializeMock([{'IN': b'AT+CAMM?\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getAccumulatedCallMeterMaximum(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CAMM?\r\n'}, {'OUT': b'+CAMM: INVALID_NUMBER\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getAccumulatedCallMeterMaximum(), -1)

  @patch('serial.Serial', new=MockSerial)
  def test_all_is_temperature_critical(self):
    logging.debug("test_all_is_temperature_critical")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT^SCTM?\r\n'}, {'OUT': b'^SCTM: DUMMY,0,OTHER_DUMMY\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.isTemperatureCritical(), False)

    MockSerial.initializeMock([{'IN': b'AT^SCTM?\r\n'}, {'OUT': b'^SCTM: DUMMY,1,OTHER_DUMMY\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.isTemperatureCritical(), True)

    MockSerial.initializeMock([{'IN': b'AT^SCTM?\r\n'}, {'OUT': b'^SCTM: DUMMY,INVALID_BOOL,OTHER_DUMMY\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.isTemperatureCritical(), False)

    MockSerial.initializeMock([{'IN': b'AT^SCTM?\r\n'}, {'OUT': b'^SCTM: DUMMY\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.isTemperatureCritical(), False)

    MockSerial.initializeMock([{'IN': b'AT^SCTM?\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.isTemperatureCritical(), False)

    MockSerial.initializeMock([{'IN': b'AT^SCTM?\r\n'}, {'OUT': b'+CAMM: INVALID_NUMBER\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.isTemperatureCritical(), False)

  @patch('serial.Serial', new=MockSerial)
  def test_all_set_internal_clock_to_current_date(self):
    logging.debug("test_all_set_internal_clock_to_current_date")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'^AT\+CCLK=\"[0-9]{2}\/[0-9]{2}\/[0-9]{2},[0-9]{2}:[0-9]{2}:[0-9]{2}\"\r\n$', 'mode': 'regex'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.setInternalClockToCurrentDate(), True)

    MockSerial.initializeMock([{'IN': b'^AT\+CCLK=\"[0-9]{2}\/[0-9]{2}\/[0-9]{2},[0-9]{2}:[0-9]{2}:[0-9]{2}\"\r\n$', 'mode': 'regex'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.setInternalClockToCurrentDate(), False)

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_internal_clock_date(self):
    logging.debug("test_all_get_internal_clock_date")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CCLK?\r\n'}, {'OUT': b'+CCLK: 11/12/13,14:15:16\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getDateFromInternalClock(), datetime.datetime.strptime("11/12/13,14:15:16", "%y/%m/%d,%H:%M:%S"))

    MockSerial.initializeMock([{'IN': b'AT+CCLK?\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getDateFromInternalClock(), -1)

    MockSerial.initializeMock([{'IN': b'AT+CCLK?\r\n'}, {'OUT': b'+CCLK: INVALID_DATE\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getDateFromInternalClock(), -1)

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_phonebook_entries(self):
    logging.debug("test_all_get_phonebook_entries")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="SM"\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-250),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=1,250\r\n'},
                               {'OUT': b'+CPBR: 1,"931123456",129,"Quentin Test"\r\n'},
                               {'OUT': b'+CPBR: 2,"9501234567",129,""\r\n'},
                               {'OUT': b'+CPBR: 4,"901234567",129,"Other"\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries("SM"), [{'contact_name': 'Quentin Test', 'index': 1, 'phone_number': '931123456'},
                                                     {'contact_name': '', 'index': 2, 'phone_number': '9501234567'},
                                                     {'contact_name': 'Other', 'index': 4, 'phone_number': '901234567'}])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-100),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=1,100\r\n'},
                               {'OUT': b'INVALID_LINE_BEFORE_RESULT...\r\n'},
                               {'OUT': b'+CPBR: 1,"931123456",129,"Quentin Test"\r\n'},
                               {'OUT': b'+CPBR: 2,"9501234567",129,""\r\n'},
                               {'OUT': b'+CPBR: 4,"901234567",129,"Other"\r\n'},
                               {'OUT': b'+CPBR: 7,"INVALID_NUMBER_OF_PARAM"\r\n'},
                               {'OUT': b'+CPBR: INVALID_INDEX,"901234567",129,"Other"\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [{'contact_name': 'Quentin Test', 'index': 1, 'phone_number': '931123456'},
                                                     {'contact_name': '', 'index': 2, 'phone_number': '9501234567'},
                                                     {'contact_name': 'Other', 'index': 4, 'phone_number': '901234567'}])

    MockSerial.initializeMock([{'IN': b'AT+CPBS="SM"\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(GSMTC35.GSMTC35.ePhonebookType.SIM), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (100-1),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (100)\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (NOT_NUMBER-1),20,14\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-NOT_NUMBER),20,14\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-100),NOT_NUMBER,14\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-100),20,NOT_NUMBER\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-100)\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-100),20\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-100),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=1,100\r\n'},  {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getPhonebookEntries(), [])

  @patch('serial.Serial', new=MockSerial)
  def test_all_add_phonebook_entry(self):
    logging.debug("test_all_add_phonebook_entry")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="ME"\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-250),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=,"+33601020304",145,"Test ADD"\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.addEntryToPhonebook(phone_number="+33601020304", contact_name="Test ADD", phonebook_type=GSMTC35.GSMTC35.ePhonebookType.GSM_MODULE))

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-250),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=,"0601020304",129,"Test ADD"\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.addEntryToPhonebook(phone_number="0601020304", contact_name="Test ADD"))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="ME"\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.addEntryToPhonebook(phone_number="0601020304", contact_name="Test ADD", phonebook_type=GSMTC35.GSMTC35.ePhonebookType.GSM_MODULE))

    MockSerial.initializeMock([])
    self.assertFalse(gsm.addEntryToPhonebook(phone_number="", contact_name="Test ADD"))

    MockSerial.initializeMock([{'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-250),20,14\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertFalse(gsm.addEntryToPhonebook(phone_number="0601020304", contact_name="CONTACT NAME TOOOOOOOOOOOOOO LONG"))

  @patch('serial.Serial', new=MockSerial)
  def test_all_delete_phonebook_entry(self):
    logging.debug("test_all_delete_phonebook_entry")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="LD"\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=65\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.deleteEntryFromPhonebook(index=65, phonebook_type=GSMTC35.GSMTC35.ePhonebookType.LAST_DIALLING))

    MockSerial.initializeMock([{'IN': b'AT+CPBW=65\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.deleteEntryFromPhonebook(index=65))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="LD"\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.deleteEntryFromPhonebook(index=65, phonebook_type=GSMTC35.GSMTC35.ePhonebookType.LAST_DIALLING))

  @patch('serial.Serial', new=MockSerial)
  def test_all_delete_all_phonebook_entries(self):
    logging.debug("test_all_delete_all_phonebook_entries")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="MC"\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-250),20,14\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=1,250\r\n'},
                               {'OUT': b'+CPBR: 1,"931123456",129,"Quentin Test"\r\n'},
                               {'OUT': b'+CPBR: 2,"9501234567",129,""\r\n'},
                               {'OUT': b'+CPBR: 4,"901234567",129,"Other"\r\n'},
                               {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=2\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=4\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.deleteAllEntriesFromPhonebook(phonebook_type=GSMTC35.GSMTC35.ePhonebookType.MISSED_CALLS))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="MC"\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=?\r\n'}, {'OUT': b'+CPBR: (1-250),20,14\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBR=1,250\r\n'},
                               {'OUT': b'+CPBR: 1,"931123456",129,"Quentin Test"\r\n'},
                               {'OUT': b'+CPBR: 2,"9501234567",129,""\r\n'},
                               {'OUT': b'+CPBR: 4,"901234567",129,"Other"\r\n'},
                               {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPBW=2\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'AT+CPBW=4\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertFalse(gsm.deleteAllEntriesFromPhonebook(phonebook_type=GSMTC35.GSMTC35.ePhonebookType.MISSED_CALLS))

    MockSerial.initializeMock([{'IN': b'AT+CPBS="MC"\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.deleteAllEntriesFromPhonebook(phonebook_type=GSMTC35.GSMTC35.ePhonebookType.MISSED_CALLS))

  @patch('serial.Serial', new=MockSerial)
  def test_all_hang_up_call(self):
    logging.debug("test_all_hang_up_call")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.hangUpCall())

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATH\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.hangUpCall())

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATH\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.hangUpCall())

  @patch('serial.Serial', new=MockSerial)
  def test_all_pick_up_call(self):
    logging.debug("test_all_pick_up_call")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'ATA;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.pickUpCall())

    MockSerial.initializeMock([{'IN': b'ATA;\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.pickUpCall())

  @patch('serial.Serial', new=MockSerial)
  def test_all_call(self):
    logging.debug("test_all_call")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'ATD0601020304;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.call(phone_number="0601020304", hide_phone_number=False))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATH\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATD0601020304;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.call(phone_number="0601020304", hide_phone_number=False))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'ATD#31#0601020304;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.call(phone_number="0601020304", hide_phone_number=True))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATH\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATD#31#0601020304;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.call(phone_number="0601020304", hide_phone_number=True))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'ATD0601020304;\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.call(phone_number="0601020304", hide_phone_number=False))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'ATD#31#0601020304;\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.call(phone_number="0601020304", hide_phone_number=True))

  @patch('serial.Serial', new=MockSerial)
  def test_all_recall(self):
    logging.debug("test_all_recall")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'ATDL;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.reCall())

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATH\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'ATDL;\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.reCall())

    MockSerial.initializeMock([{'IN': b'AT+CHUP\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'ATDL;\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.reCall())

  @patch('serial.Serial', new=MockSerial)
  def test_all_is_someone_calling(self):
    logging.debug("test_all_is_someone_calling")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CPAS\r\n'}, {'OUT': b'+CPAS: 3\r\n'}])
    self.assertTrue(gsm.isSomeoneCalling())

    MockSerial.initializeMock([{'IN': b'AT+CPAS\r\n'}, {'OUT': b'+CPAS: 4\r\n'}])
    self.assertFalse(gsm.isSomeoneCalling())

    MockSerial.initializeMock([{'IN': b'AT+CPAS\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.isSomeoneCalling())

  @patch('serial.Serial', new=MockSerial)
  def test_all_is_call_in_progress(self):
    logging.debug("test_all_is_call_in_progress")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CPAS\r\n'}, {'OUT': b'+CPAS: 4\r\n'}])
    self.assertTrue(gsm.isCallInProgress())

    MockSerial.initializeMock([{'IN': b'AT+CPAS\r\n'}, {'OUT': b'+CPAS: 3\r\n'}])
    self.assertFalse(gsm.isCallInProgress())

    MockSerial.initializeMock([{'IN': b'AT+CPAS\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.isCallInProgress())

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_last_call_duration(self):
    logging.debug("test_all_get_last_call_duration")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT^SLCD\r\n'}, {'OUT': b'^SLCD: 12:34:56\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getLastCallDuration(), 12*3600+34*60+56)

    MockSerial.initializeMock([{'IN': b'AT^SLCD\r\n'}, {'OUT': b'^SLCD: INVALID_TIME\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getLastCallDuration(), -1)

    MockSerial.initializeMock([{'IN': b'AT^SLCD\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getLastCallDuration(), -1)

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_current_call_state(self):
    logging.debug("test_all_get_current_call_state")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.NOCALL, ''))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: 1,1,5,0,0,"+33601020304",145\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.WAITING, '+33601020304'))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: 1,1,4,0,0,"+33601020304",145\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.INCOMING, '+33601020304'))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: 1,1,3,0,0,"+33601020304",145\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.ALERTING, '+33601020304'))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: 1,1,2,0,0,"+33601020304",145\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.DIALING, '+33601020304'))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: 1,1,1,0,0,"+33601020304",145\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.HELD, '+33601020304'))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: 1,1,0,0,0,"+33601020304",145\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.ACTIVE, '+33601020304'))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: INVALID_LIST,A,B,C,D\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.NOCALL, ''))

    MockSerial.initializeMock([{'IN': b'AT+CLCC\r\n'}, {'OUT': b'+CLCC: INVALID_LIST\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getCurrentCallState(), (GSMTC35.GSMTC35.eCall.NOCALL, ''))

  @patch('serial.Serial', new=MockSerial)
  def test_all_set_forward_status(self):
    logging.debug("test_all_set_forward_status")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,3,+33601020304,145,1\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.UNCONDITIONAL, GSMTC35.GSMTC35.eForwardClass.VOICE, True, "+33601020304"))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,4,,,1\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.UNCONDITIONAL, GSMTC35.GSMTC35.eForwardClass.VOICE, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=1,4,,,2\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.MOBILE_BUSY, GSMTC35.GSMTC35.eForwardClass.DATA, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=2,4,,,4\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.NO_REPLY, GSMTC35.GSMTC35.eForwardClass.FAX, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=3,4,,,8\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.NOT_REACHABLE, GSMTC35.GSMTC35.eForwardClass.SMS, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=4,4,,,16\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.ALL_CALL_FORWARDING, GSMTC35.GSMTC35.eForwardClass.DATA_CIRCUIT_SYNC, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=5,4,,,32\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.ALL_CONDITIONAL_CALL_FORWARDING, GSMTC35.GSMTC35.eForwardClass.DATA_CIRCUIT_ASYNC, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=5,4,,,64\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.ALL_CONDITIONAL_CALL_FORWARDING, GSMTC35.GSMTC35.eForwardClass.DEDICATED_PACKED_ACCESS, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=5,4,,,128\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.ALL_CONDITIONAL_CALL_FORWARDING, GSMTC35.GSMTC35.eForwardClass.DEDICATED_PAD_ACCESS, False))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,3,+33601020304,145,1\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.UNCONDITIONAL, GSMTC35.GSMTC35.eForwardClass.VOICE, True, "+33601020304"))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,4,,,1\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.setForwardStatus(GSMTC35.GSMTC35.eForwardReason.UNCONDITIONAL, GSMTC35.GSMTC35.eForwardClass.VOICE, False))

  @patch('serial.Serial', new=MockSerial)
  def test_all_get_forward_status(self):
    logging.debug("test_all_get_forward_status")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,2\r\n'},
                               {'OUT': b'+CCFC: 0,2\r\n'}, {'OUT': b'+CCFC: 0,1\r\n'}, {'OUT': b'+CCFC: 0,4\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getForwardStatus(), [{'class': 'DATA', 'enabled': False},
                                              {'class': 'VOICE', 'enabled': False},
                                              {'class': 'FAX', 'enabled': False}
                                             ])

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,2\r\n'},
                               {'OUT': b'+CCFC: 1,2,+33601020304,145\r\n'},
                               {'OUT': b'+CCFC: 1,1,0601020304,129\r\n'},
                               {'OUT': b'+CCFC: 0,4\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getForwardStatus(), [{'class': 'DATA', 'enabled': True, 'is_international': True, 'phone_number': '+33601020304'},
                                              {'class': 'VOICE', 'enabled': True, 'is_international': False, 'phone_number': '0601020304'},
                                              {'class': 'FAX', 'enabled': False}
                                             ])

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,2\r\n'},
                               {'OUT': b'+CCFC: 1,1\r\n'}, {'OUT': b'+CCFC: 0,2\r\n'}, {'OUT': b'+CCFC: 1,4\r\n'},
                               {'OUT': b'+CCFC: 0,8\r\n'}, {'OUT': b'+CCFC: 1,16\r\n'}, {'OUT': b'+CCFC: 0,32\r\n'},
                               {'OUT': b'+CCFC: 1,64\r\n'}, {'OUT': b'+CCFC: 0,128\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getForwardStatus(), [{'class': 'VOICE', 'enabled': True},
                                              {'class': 'DATA', 'enabled': False},
                                              {'class': 'FAX', 'enabled': True},
                                              {'class': 'SMS', 'enabled': False},
                                              {'class': 'DATA_CIRCUIT_SYNC', 'enabled': True},
                                              {'class': 'DATA_CIRCUIT_ASYNC', 'enabled': False},
                                              {'class': 'DEDICATED_PACKED_ACCESS', 'enabled': True},
                                              {'class': 'DEDICATED_PAD_ACCESS', 'enabled': False}])

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,2\r\n'},
                               {'OUT': b'+CCFC: INVALID_LIST\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getForwardStatus(), [])

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,2\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertEqual(gsm.getForwardStatus(), [])

    MockSerial.initializeMock([{'IN': b'AT+CCFC=0,2\r\n'}, {'OUT': b'INVALID_DATA\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.getForwardStatus(), [])

  @patch('serial.Serial', new=MockSerial)
  def test_all_lock_sim_pin(self):
    logging.debug("test_all_lock_sim_pin")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",1,1234\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.lockSimPin("1234"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",1,4321\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.lockSimPin(4321))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",1,4321\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.lockSimPin(4321))

  @patch('serial.Serial', new=MockSerial)
  def test_all_unlock_sim_pin(self):
    logging.debug("test_all_unlock_sim_pin")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",0,1234\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.unlockSimPin("1234"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",0,4321\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.unlockSimPin(4321))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",0,4321\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.unlockSimPin(4321))

  @patch('serial.Serial', new=MockSerial)
  def test_all_change_pin(self):
    logging.debug("test_all_change_pin")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",1,1234\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPWD="SC","1234","4321"\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.changePin(old_pin="1234", new_pin="4321"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",1,1234\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.changePin(old_pin="1234", new_pin="4321"))

    MockSerial.initializeMock([{'IN': b'AT+CLCK="SC",1,1234\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CPWD="SC","1234","4321"\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertFalse(gsm.changePin(old_pin="1234", new_pin="4321"))

  @patch('serial.Serial', new=MockSerial)
  def test_all_is_in_sleep_mode(self):
    logging.debug("test_all_is_in_sleep_mode")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    # In real case scenario in sleep mode, the gsm doesn't answer anything
    MockSerial.initializeMock([{'IN': b'AT+CFUN?\r\n'}])
    self.assertTrue(gsm.isInSleepMode())

    # In real case scenario in not sleep mode, the gsm answers "+CFUN: 1"
    MockSerial.initializeMock([{'IN': b'AT+CFUN?\r\n'}, {'OUT': b'+CFUN: 1\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},])
    self.assertFalse(gsm.isInSleepMode())

    # This case should never happen but who knows (GSM answering it is sleeping)...
    MockSerial.initializeMock([{'IN': b'AT+CFUN?\r\n'}, {'OUT': b'+CFUN: 0\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},])
    self.assertTrue(gsm.isInSleepMode())

    MockSerial.initializeMock([{'IN': b'AT+CFUN?\r\n'}, {'OUT': b'+CFUN: INVALID_RESPONSE\r\n'},
                               {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},])
    self.assertFalse(gsm.isInSleepMode())

    MockSerial.initializeMock([{'IN': b'AT+CFUN?\r\n'}, {'OUT': b'+CFUN: \r\n'}])
    self.assertFalse(gsm.isInSleepMode())

  @patch('serial.Serial', new=MockSerial)
  def test_all_sleep(self):
    logging.debug("test_all_sleep")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    # Not waiting gsm to wake up
    MockSerial.initializeMock([{'IN': b'AT+CLIP=1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CFUN=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_call=True, blocking=False), (True, False, False, False, False))

    # Waiting call received
    MockSerial.initializeMock([{'IN': b'AT+CLIP=1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CFUN=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT\r\n'},
                               {'OUT': b'+CLIP\r\n', 'wait_ms': 3000},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_call=True), (True, False, True, False, False))

    # Waiting gsm alarm received
    MockSerial.initializeMock([{'IN': b'AT+CCLK?\r\n'}, {'OUT': b'+CCLK: 10/10/10,10:10:10\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CALA="10/10/10,10:10:21",0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CFUN=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT\r\n'},
                               {'OUT': b'+CALA\r\n', 'wait_ms': 3000},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_timer_in_sec=10), (True, True, False, False, False))

    # Waiting sms received
    MockSerial.initializeMock([{'IN': b'AT+CNMI=1,1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CFUN=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT\r\n'},
                               {'OUT': b'+CMTI\r\n', 'wait_ms': 3000},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_sms=True), (True, False, False, True, False))

    # Waiting sms received
    MockSerial.initializeMock([{'IN': b'AT^SCTM=1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CFUN=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT\r\n'},
                               {'OUT': b'^SCTM\r\n', 'wait_ms': 3000},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_temperature_warning=True), (True, False, False, False, True))

    # Already alive
    MockSerial.initializeMock([{'IN': b'AT\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.waitEndOfSleepMode(), (True, False, False, False, False))

    # Invalid parameters
    MockSerial.initializeMock([])
    self.assertEqual(gsm.sleep(), (False, False, False, False, False))

    # No wake up specified
    MockSerial.initializeMock([{'IN': b'AT\r\n'}, {'OUT': b'HEY THERE, I\'M UP!\r\n', 'wait_ms': 3000},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertEqual(gsm.sleep(), (False, False, False, False, False))

    # Error while setting up wake up request
    MockSerial.initializeMock([{'IN': b'AT^SCTM=1\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_temperature_warning=True), (False, False, False, False, False))

    MockSerial.initializeMock([{'IN': b'AT+CNMI=1,1\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_sms=True), (False, False, False, False, False))

    MockSerial.initializeMock([{'IN': b'AT+CLIP=1\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_call=True), (False, False, False, False, False))

    MockSerial.initializeMock([{'IN': b'AT+CNMI=1,1\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CFUN=0\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_sms=10), (False, False, False, False, False))

    MockSerial.initializeMock([{'IN': b'AT+CCLK?\r\n'}, {'OUT': b'ERROR\r\n'},
                               {'IN': b'AT+CLIP=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CNMI=0,0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT^SCTM=0\r\n'}, {'OUT': b'OK\r\n'}
                               ])
    self.assertEqual(gsm.sleep(wake_up_with_timer_in_sec=10), (False, False, False, False, False))

    # Error during waking up
    MockSerial.initializeMock([{'IN': b'AT\r\n'}])
    self.assertEqual(gsm.waitEndOfSleepMode(max_additional_waiting_time_in_sec=0), (False, False, False, False, False))

  # TODO: Use "valid" local/international phone number in this test scenario (0601020304 or +33601020304, not 33601020304)
  @patch('serial.Serial', new=MockSerial)
  def test_success_send_sms_7bit(self):
    logging.debug("test_success_send_sms_7bit")
    gsm = GSMTC35.GSMTC35()
    MockSerial.initializeMock(MockSerial.getDefaultConfigForSetup())
    self.assertTrue(gsm.setup(_port="COM_FAKE"))

    # One part 7 bit SMS
    MockSerial.initializeMock([{'IN': b'AT+CMGF=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGS=36\r\n'}, {'IN': b'^0001[0-9A-F]{2}0B913306010203F400001AC2F03C3D06DD40E2341D346D4E41657CB80D6797419B32', 'mode': 'regex'},
                               {'OUT': b'\r\n'}, {'OUT': b'>'}, {'OUT': b'\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'+CMGS: 59\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.sendSMS(phone_number="33601020304", msg="Basic 7 bit SMS example €"))

    MockSerial.initializeMock([{'IN': b'AT+CMGF=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGS=36\r\n'}, {'IN': b'^0001[0-9A-F]{2}0B913306010203F400001AC2F03C3D06DD40E2341D346D4E41657CB80D6797419B32', 'mode': 'regex'},
                               {'OUT': b'\r\n'}, {'OUT': b'>'}, {'OUT': b'\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'+CMGS: 59\r\n'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'ERROR\r\n'}])
    self.assertTrue(gsm.sendSMS(phone_number="33601020304", msg="Basic 7 bit SMS example €"))

    # Multipart 7 bit SMS
    MockSerial.initializeMock([{'IN': b'AT+CMGF=0\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGS=140\r\n'}, {'IN': b'^0041[0-9A-F]{2}0B913306010203F4000091050003[0-9A-F]{2}02019A75363D0D0FCBE9A01B489CA683A6CD29A88C0FB7E1EC32685376B95C2E97CBE572B9402E97CBE572B95C2E17C8E572B95C2E97CBE502B95C2E97CBE572B95C2097CBE572B95C2E970BE472B95C2E97CBE572815C2E97CBE572B95C2E90CBE572B95C2E97CB0572B95C2E97CBE572B9402E97CBE572B95C2E', 'mode': 'regex'},
                               {'OUT': b'\r\n'}, {'OUT': b'>\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGS=33\r\n'}, {'IN': b'^0041[0-9A-F]{2}0B913306010203F4000016050003[0-9A-F]{2}02025C2097CBE572B95C2E97ABE82402', 'mode': 'regex'},
                               {'OUT': b'\r\n'}, {'OUT': b'>'}, {'OUT': b'\r\n'}, {'OUT': b'OK\r\n'},
                               {'IN': b'AT+CMGF=1\r\n'}, {'OUT': b'OK\r\n'}])
    self.assertTrue(gsm.sendSMS(phone_number="33601020304", msg="Multipart 7 bit SMS example €.......... .......... .......... .......... .......... .......... .......... .......... .......... .......... ..........END"))

  # TODO: test_failed_send_sms_7bit
  # TODO: test_success_send_sms_ucs2
  # TODO: test_failed_send_sms_ucs2
  # TODO: test_success_send_sms_text_mode
  # TODO: test_failed_send_sms_text_mode
  # TODO: test_success_get_sms_all_mode
  # TODO: test_failed_get_sms_all_mode
  # TODO: test_all_delete_sms
  # TODO: Enum convertion (eForwardReasonToString, eForwardClassToString, eCallToString)

if __name__ == '__main__':
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  unittest.main()

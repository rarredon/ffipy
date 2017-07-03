##!/bin/python
# ------------------------------------------------------------------------------
# Purpose: To test the FFIEC_Client class in ffipy
# Author: Ryan Arredondo (ryan.c.arredondo@gmail.com)
# Date: 06/10/2017
# ------------------------------------------------------------------------------

import unittest
import os
from configparser import ConfigParser
from uuid import uuid4
from unittest.mock import patch

from zeep import Client
from zeep.wsse.username import UsernameToken
from zeep.exceptions import Fault

from ffipy import FFIEC_Client

# Login parameters
wsdl = \
    'https://cdr.ffiec.gov/Public/PWS/WebServices/RetrievalService.asmx?WSDL'
username = input('Username (if username is invalid all tests will fail): ')
password = input('Password (if password is invalid all tests will fail): ')
wsse = UsernameToken(username, password)

# Default retrieval parameters in FFIEC_Client methods
ds_name = 'Call'
date = '3/31/2017'
ID_type = 'ID_RSSD'
ID = 64150
fmt = 'PDF'

# To test that a conf file is being created
unique_filepath = os.path.join(os.curdir, str(uuid4()))
while os.access(unique_filepath, os.F_OK):
    unique_filepath = os.path.join(os.curdir, str(uuid4()))
os.environ['FFIEC_USER_CONF'] = unique_filepath


class FFIEC_Client_TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.client = FFIEC_Client(wsse=(username, password))
        self.zeep = Client(wsdl=wsdl, wsse=wsse)
        self.maxDiff = 9000

    def test_wsdl(self):
        self.assertEqual(self.client.wsdl.location, wsdl)

    def test_wsse(self):
        self.assertEqual(self.client.wsse.username, username)
        self.assertEqual(self.client.wsse.password, password)

    def test_retrieve_facsimile(self):
        client_result = self.client.retrieve_facsimile()
        zeep_result = self.zeep.service.RetrieveFacsimile(ds_name, date,
                                                          ID_type, ID, fmt)
        self.assertEqual(client_result, zeep_result)

    def test_retrieve_filers_since_date(self):
        client_result = self.client.retrieve_filers_since_date()
        zeep_result = self.zeep.service.RetrieveFilersSinceDate(ds_name,
                                                                date, date)
        self.assertEqual(client_result, zeep_result)

    def test_retrieve_filers_submission_datetime(self):
        client_result = self.client.retrieve_filers_submission_datetime()
        zeep_result = \
            self.zeep.service.RetrieveFilersSubmissionDateTime(ds_name,
                                                               date, date)
        isEqual = all(c['ID_RSSD'] == z['ID_RSSD']
                      and c['DateTime'] == z['DateTime']
                      for c, z in zip(client_result, zeep_result))
        self.assertTrue(isEqual)
    
    def test_retrieve_panel_of_reporters(self):
        client_result = self.client.retrieve_panel_of_reporters()
        zeep_result = self.zeep.service.RetrievePanelOfReporters(ds_name, date)
        client_result.sort(key=lambda x: x['ID_RSSD'])
        zeep_result.sort(key=lambda x: x['ID_RSSD'])
        isEqual = all(c['ID_RSSD'] == z['ID_RSSD']
                      and c['FDICCertNumber'] == z['FDICCertNumber']
                      and c['OCCChartNumber'] == z['OCCChartNumber']
                      and c['OTSDockNumber'] == z['OTSDockNumber']
                      and c['PrimaryABARoutNumber'] == z['PrimaryABARoutNumber']
                      and c['Name'] == z['Name']
                      and c['State'] == z['State']
                      and c['City'] == z['City']
                      and c['Address'] == z['Address']
                      and c['ZIP'] == z['ZIP']
                      and c['FilingType'] == z['FilingType']
                      and c['HasFiledForReportingPeriod'] == \
                          z['HasFiledForReportingPeriod'] 
                      for c, z in zip(client_result, zeep_result))
        self.assertTrue(isEqual)

    def test_retrieve_reporting_periods(self):
        client_result = self.client.retrieve_reporting_periods()
        zeep_result = self.zeep.service.RetrieveReportingPeriods(ds_name)
        self.assertEqual(client_result, zeep_result)

    def test_retrieve_UBPR_reporting_periods(self):
        client_result = self.client.retrieve_UBPR_reporting_periods()
        zeep_result = self.zeep.service.RetrieveUBPRReportingPeriods()
        self.assertEqual(client_result, zeep_result)

    def test_retrieve_UBPR_XBRL_facsimile(self):
        client_result = self.client.retrieve_UBPR_XBRL_facsimile()
        zeep_result = \
            self.zeep.service.RetrieveUBPRXBRLFacsimile(date, ID_type, ID)
        self.assertEqual(client_result, zeep_result)

    @patch('ffipy.FFIEC_Client')
    def test_test_user_access(self, MockClient):
        self.assertTrue(self.client.test_user_access())

        # Check that fake username raises error in zeep.Client
        fake_wsse = UsernameToken('username', 'password')
        self.fake_client = Client(wsdl=wsdl, wsse=fake_wsse)
        with self.assertRaises(Fault):
            self.fake_client.service.TestUserAccess()

        # Check that user input updated to valid user works
        MockClient.__check_login.return_value = 'y'
        MockClient.__get_login.return_value = username, password
        self.fake_client = MockClient(wsse=fake_wsse)

    def test_conf_file(self):
        # Check that conf file was created
        self.assertEqual(self.client.wsse_path, unique_filepath)
        self.assertTrue(os.access(unique_filepath, os.R_OK))
        conf = ConfigParser()
        conf.read(unique_filepath)
        self.assertEqual(conf['wsse']['username'], username)
        self.assertEqual(conf['wsse']['password'], password)
        
        # Check that new instance of FFIEC_Client can be started from conf file
        self.client = FFIEC_Client()
        self.assertEqual(self.client.wsse_path, unique_filepath)
        self.assertEqual(self.client.wsse.username, username)
        self.assertEqual(self.client.wsse.password, password)
        self.assertTrue(self.client.test_user_access())

    @classmethod
    def tearDownClass(self):
        del os.environ['FFIEC_USER_CONF']
        os.remove(unique_filepath)

if __name__ == '__main__':
    unittest.main()
        

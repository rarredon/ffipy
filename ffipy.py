#!/bin/python
# ------------------------------------------------------------------------------
# Purpose: an interface for retrieving reports from the FFIEC site
# Usage: TBD
# Author: Ryan Arredondo (ryan.c.arredondo@gmail.com)
# Date: 06/07/2017
# ------------------------------------------------------------------------------

# PSL
import sys

# 3rd party libs
import zeep
from zeep.wsse.username import UsernameToken

def main():
    wsdl = ('https://cdr.ffiec.gov/Public/PWS/WebServices/'
            'RetrievalService.asmx?WSDL')
    wsse = UsernameToken(sys.argv[1], sys.argv[2])
    client = zeep.Client(wsdl=wsdl, wsse=wsse)
    retrieveFascimile(client, outfile='defaults.pdf', return_result=False)


def retrieveFascimile(client, ds_name='Call', reportingPeriodEndDate='3/31/2017',
                      fiID_type='ID_RSSD', fiID=453446, fascimile_fmt='PDF', 
                      outfile=None, return_result=True):
    """
    Retrieves a facsimile (e.g., a report) from FFIEC site
    
    kwargs:
      client -- zeep SOAP client whose WSDL is \
          https://cdr.ffiec.gov/Public/PWS/WebServices/RetrievalService.asmx?WSDL
      ds_name -- DataSeriesName (default is 'Call')
      reportingPeriodEndDate -- Date for end of the reporting period (default is 
          3/31/17)
      fiID_type -- Type of Financial Inst ID (default is 'ID_RSSD')
      fiID -- Financial Inst ID (default is 453446, for testing)
      fascimile_fmt -- Format of fascimile to retrieve (default is 'PDF')
      outfile -- path of file to write facsimile to; If None, no ouput (default)
      return_result -- If True, return the retrieved facsimile (default)
    returns:
      facsimile -- the revtrieved facsimile (only if return_result==True)
    """
    data_series = client.get_type('ns0:ReportingDataSeriesName')
    ds_name = data_series(ds_name)
    fiID_type_type = client.get_type('ns0:FinancialInstitutionIDType')
    fiID_type = fiID_type_type(fiID_type)
    facsimile_fmt_type = client.get_type('ns0:FacsimileFormat')
    facsimile_fmt = facsimile_fmt_type('PDF')
    facsimile = client.service.RetrieveFacsimile(ds_name, reportingPeriodEndDate,
                                                 fiID_type, fiID, facsimile_fmt)
    if outfile:
        with open(outfile, 'wb') as f:
            f.write(facsimile)
    if return_result:
        return facsimile


if __name__ == '__main__':
    main()

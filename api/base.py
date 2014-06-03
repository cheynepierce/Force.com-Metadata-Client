from suds.client import Client

class BaseClient(object):
    _sfdc = None
    _metadata = None
    
    '''
    Make a connection to the Salesforce SOAP API.
    
    wsdl => Location of WSDL file
    '''
    def __init__(self, partnerWsdl, metadataWsdl):
        self._sfdc = Client(partnerWsdl)
        self._metadata = Client(metadataWsdl)
        
    '''
    Logs user in to Salesforce.
    
    Returns information about current session.
    '''
    def login(self, username, password, token):
        loginRes = self._sfdc.service.login(username, password + token)
        
        self._sfdc.set_options(location = loginRes.serverUrl)
        self._metadata.set_options(location = loginRes.metadataServerUrl)
        
        sessionHeader = self._sfdc.factory.create('SessionHeader')
        sessionHeader.sessionId = loginRes.sessionId
        self._sfdc.set_options(soapheaders = sessionHeader)
        self._metadata.set_options(soapheaders = sessionHeader)
        
        return loginRes
        
    '''
    Logs user out of Salesforce.com. 
    This method logs the user out from every concurrent session.
    '''
    def logout(self):
        self._sfdc.service.logout()
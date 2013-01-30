import os
import webapp2
from google.appengine.ext.webapp import template

from datetime import datetime
from pytz.gae import pytz

BASE_URL='http://yourgoogleappname.appspot.com'
#BASE_URL='' # For testing via localhost
HOME_NUMBER='415-555-1212'
CELL_1='415-555-1313'
NAME_1='Jim'
CELL_2='415-555-1414'
NAME_2='Sally'
NINE_URL=BASE_URL+'/9.wav'
FAMILY_NAME='smith'
PARTY_DAY=6
PASSWORD='1234567'

class BasePage(webapp2.RequestHandler):
    def get(self):
        self.post()

    def _error(self, msg, redirecturl=None):
        templatevalues = {
            'msg': msg,
            'redirecturl': redirecturl
        }
        xml_response(self, 'error.xml', templatevalues)

class AnswerPage(BasePage):
    def post(self):
        try:
            params = {}
            if(pst_weekday() == PARTY_DAY):
                params = { 'timeout' : 4, 'preface' : ('If you are here for the party, press 1 then type in your code or wait to ring the ' + FAMILY_NAME + '.') }
            else:
                params = { 'timeout' : 2, 'preface' : ('Please wait while I connect you.') }
            xml_response( self, 'answer.xml', params )
        except:
            self._error("Error parsing answer page")

class MainPage(BasePage):
    def post(self):
        key = self.request.get('Digits')
        try:
            if (key == '1') or (key == '4'):
                xml_response( self, 'code.xml' )
            else:
                xml_response( self, 'forward.xml', { 'number' : HOME_NUMBER, 'action' : '/app/dialhomeresult' } )
        except:
            self._error("Error parsing main page")

class DialHomeResultPage(BasePage):
    def post(self):
        status = self.request.get('DialCallStatus')
        #sid = self.request.get('DialCallSid')
        #duration = self.request.get('DialCallDuration')
        try:
            if status == 'completed':
                xml_response( self, 'end.xml' )
            else:
                xml_response( self, 'nothomemenu.xml' )
        except:
            self._error("Error parsing dial home result page")
        
class CodePage(BasePage):
    def post(self):
        key = self.request.get('Digits')
        try:
            if key == PASSWORD:
                xml_response( self, 'buzz.xml' )
            else:
                xml_response( self, 'codeerror.xml' )
        except:
            self._error("Error parsing code page")

class NotHomeResultPage(BasePage):
    def post(self):
        key = self.request.get('Digits')
        try:
            if key == '1':
                xml_response( self, 'forward.xml', { 'preface' : ('Dialing '+NAME_1), 'number' : CELL_1 } )
            elif key == '2':
                xml_response( self, 'forward.xml', { 'preface' : ('Dialing '+NAME_2), 'number' : CELL_2 } )
            elif (key == '3') or (key == '4'):
                xml_response( self, 'code.xml' )
            elif key == '*':
                xml_response( self, 'end.xml' )
            else:
                xml_response( self, 'nothomemenu.xml', { 'preface' : 'I did not understand.' } )
        except:
            self._error("Error parsing not home page.")

class SimpleForwardPage(BasePage):
    def post(self):
        try:
            xml_response( self, 'forward.xml', { 'number' : HOME_NUMBER } )
        except:
            self._error("Error parsing forward page")

utc = pytz.timezone('UTC')
pst = pytz.timezone('US/Pacific')

def pst_weekday():
    return datetime.utcnow().replace(tzinfo=utc).astimezone(pst).weekday()

def xml_response(handler, page, templatevalues={}):
    """
    Renders an XML response using a provided template page and values
    """
    templatevalues[ 'baseurl' ] = BASE_URL
    templatevalues[ 'family' ] = FAMILY_NAME
    templatevalues[ 'nine' ] = NINE_URL
    templatevalues[ 'name1' ] = NAME_1
    templatevalues[ 'name2' ] = NAME_2
    path = os.path.join(os.path.dirname(__file__), page)
    handler.response.headers["Content-Type"] = "text/xml"
    handler.response.out.write(template.render(path, templatevalues))
        

app = webapp2.WSGIApplication([('/app/answer', AnswerPage),
                               ('/app/code', CodePage),
                               ('/app/forward', SimpleForwardPage),
                               ('/app/main', MainPage),
                               ('/app/dialhomeresult', DialHomeResultPage),
                               ('/app/nothomeresult', NotHomeResultPage)],
                              debug=True)

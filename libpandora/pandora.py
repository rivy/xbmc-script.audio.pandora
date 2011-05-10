import xmlrpclib
from urllib2 import urlopen
import time

import crypt

PROTOCOL_VERSION=30
BASE_URL = "http://www.pandora.com/radio/xmlrpc/v%d?" %PROTOCOL_VERSION
BASE_URL_RID = BASE_URL + "rid=%sP&method=%s"
BASE_URL_LID = BASE_URL + "rid=%sP&lid=%s&method=%s"

def _inttime():
	return int( time.time() )

class Pandora:
	rid = ""
	lid = ""
	authToken = ""
	curStation = ""
	curFormat = "mp3" #Default to mp3 if not specified

	def __init__( self ):
		self.rid = "%07i" %( time.time() % 10000000 )

	def __init__( self, format ):
		self.rid = "%07i" %( time.time() % 10000000 )
		self.curFormat = format

	def sync( self ):
		reqUrl = BASE_URL_RID %( self.rid, "sync" )

		req = xmlrpclib.dumps( (), "misc.sync" ).replace( "\n", "" )
		enc = crypt.encryptString( req )

		u = urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

	def authListener( self, user, pwd ):
		reqUrl = BASE_URL_RID %( self.rid, "authenticateListener" )

		req = xmlrpclib.dumps( ( _inttime(), user, pwd ), \
								"listener.authenticateListener" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req )

		u = urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		try:
			parsed = xmlrpclib.loads( resp )[0][0]
		except xmlrpclib.Fault, fault:
			print "Error:", fault.faultString
			print "Code:", fault.faultCode
			return False

		self.authToken = parsed["authToken"]
		self.lid = parsed["listenerId"]
		
		return True

	def getStations( self ):
		reqUrl = BASE_URL_LID %( self.rid, self.lid, "getStations" )

		req = xmlrpclib.dumps( ( _inttime(), self.authToken ), \
								"station.getStations" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req )

		u = urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		parsed = xmlrpclib.loads( resp )[0][0]

		return parsed

	def getFragment( self, stationId=None, format=None ):
		if stationId == None:
			stationId = self.curStation
		if format == None:
			format = self.curFormat
		reqUrl = BASE_URL_LID %( self.rid, self.lid, "getFragment" )

		args = ( _inttime(), self.authToken, stationId, "0", "", "", \
					format, "0", "0" )
		req = xmlrpclib.dumps( args, "playlist.getFragment" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req )

		u = urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		parsed = xmlrpclib.loads( resp )[0][0]

		#last 48 chars of URL encrypted, padded w/ 8 * '\x08'
		for i in range( len( parsed ) ):
			url = parsed[i]["audioURL"]
			url = url[:-48] + crypt.decryptString( url[-48:] )[:-8]
			parsed[i]["audioURL"] = url

		self.curStation = stationId
		self.curFormat = format

		return parsed


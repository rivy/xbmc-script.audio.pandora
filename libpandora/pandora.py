import xmlrpclib
import urllib2
import time

import crypt
import keys

PROTOCOL_VERSION=34
BASE_URL = "https://www.pandora.com/radio/xmlrpc/v%d?" %PROTOCOL_VERSION
BASE_URL_RID = BASE_URL + "rid=%sP&method=%s"
BASE_URL_LID = BASE_URL + "rid=%sP&lid=%s&method=%s"

def _inttime():
	return int( time.time() )

class PandoraError(Exception):
	def __init__( self, value ):
		self.value = value
	def __str__( self ):
		return repr( self.value )

class Pandora:
	rid = ""
	lid = ""
	authToken = ""
	curStation = ""
	curFormat = ""
	offset = 0

	def __init__( self, dataDir, fmt = "mp3" ):
		self.dataDir = dataDir
		self.rid = "%07i" %( time.time() % 10000000 )
		self.keys = keys.Keys( self.dataDir, PROTOCOL_VERSION )
		if not self.keys.loadKeys():
			raise PandoraError("Unable to load keys")
		self.curFormat = fmt

	def _timestamp( self ):
		return _inttime() - self.offset

	def setProxy( self, proxy_info ):
		if proxy_info["user"] == "" and proxy_info["pass"] == "":
			proxy_h = urllib2.ProxyHandler( { "http" : \
				"http://%(host)s:%(port)s" %proxy_info } )
		else:
			proxy_h = urllib2.ProxyHandler( { "http" : \
				"http://%(user)s:%(pass)s@%(host)s:%(port)s" %proxy_info } )

		proxy_o = urllib2.build_opener( proxy_h, urllib2.HTTPHandler )

		urllib2.install_opener( proxy_o )

	def sync( self ):
		#reqUrl = BASE_URL_RID %( self.rid, "sync" )
		reqUrl = 'http://ridetheclown.com/s2/synctime.php'

		#req = xmlrpclib.dumps( (), "misc.sync" ).replace( "\n", "" )
		#enc = crypt.encryptString( req, self.keys['out'] )

		#u = urllib2.urlopen( reqUrl, enc )
		u = urllib2.urlopen(reqUrl)
		resp = u.read()
		u.close()

		#parsed = xmlrpclib.loads( resp )[0][0]
		#t = crypt.decryptString( parsed, self.keys['in'] )
		#print 'Debugging pandora: ' + str(_inttime())
		#print 'From Hack: ' + resp
		#self.offset = _inttime() - int(t[4:-2])
		self.offset = _inttime() - int(resp)

	def authListener( self, user, pwd ):
		reqUrl = BASE_URL_RID %( self.rid, "authenticateListener" )

		req = xmlrpclib.dumps( ( self._timestamp(), "00000000000000000000000000000000", user, pwd, "html5tuner", "", "", "HTML5", True ), \
								"listener.authenticateListener" )
		#req = '<?xml version=\"1.0\"?><methodCall><methodName>listener.authenticateListener</methodName><params><param><value><int>%lu</int></value></param><param><value><string>%s</string></value></param><param><value><string>%s</string></value></param><param><value><string>html5tuner</string></value></param><param><value><string/></value></param><param><value><string/></value></param><param><value><string>HTML5</string></value></param><param><value><boolean>1</boolean></value></param></params></methodCall>' % (self._timestamp(), user, pwd)

		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urllib2.urlopen( reqUrl, enc )
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

		req = xmlrpclib.dumps( ( self._timestamp(), self.authToken ), \
								"station.getStations" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urllib2.urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		parsed = xmlrpclib.loads( resp )[0][0]

		return parsed

	def getFragment( self, stationId=None, format=None ):
		if stationId == None:
			stationId = self.curStation
		if format == None:
			format = self.curFormat
		reqUrl = BASE_URL_LID.replace('https', 'http') %( self.rid, self.lid, "getFragment" )

		args = ( self._timestamp(), self.authToken, stationId, "0", "", "", \
					format, "0", "0" )
		req = xmlrpclib.dumps( args, "playlist.getFragment" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urllib2.urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		parsed = xmlrpclib.loads( resp )[0][0]

		#last 48 chars of URL encrypted, padded w/ 8 * '\x08'
		for i in range( len( parsed ) ):
			url = parsed[i]["audioURL"]
			url = url[:-48] + crypt.decryptString( url[-48:],\
											 self.keys['in'] )[:-8]
			parsed[i]["audioURL"] = url

		self.curStation = stationId
		self.curFormat = format

		return parsed

	def addFeedback( self, stationId, musicId, likeFlag ):

		reqUrl = BASE_URL_LID %( self.rid, self.lid, "addFeedback" )

		matchingSeed = ""
		userSeed = ""
		focusTraitId = ""

		args = ( self._timestamp(), self.authToken, stationId, musicId, matchingSeed, userSeed, focusTraitId, "", likeFlag, False )

		req = xmlrpclib.dumps( args, "station.addFeedback" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urllib2.urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

	def addTiredSong( self, musicId ):
		reqUrl = BASE_URL_LID %( self.rid, self.lid, "addTiredSong" )

		req = xmlrpclib.dumps( ( self._timestamp(), self.authToken, musicId ), \
								"listener.addTiredSong" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urllib2.urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

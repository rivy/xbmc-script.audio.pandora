import xmlrpclib
import urllib2
import time

import crypt
import keys

PROTOCOL_VERSION=31
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
	curFormat = ""

	def __init__( self, dataDir, fmt = "mp3" ):
		self.dataDir = dataDir
		self.rid = "%07i" %( time.time() % 10000000 )
		self.keys = keys.Keys( self.dataDir, PROTOCOL_VERSION )
		self.keys.loadKeys()
		self.curFormat = fmt

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
		reqUrl = BASE_URL_RID %( self.rid, "sync" )

		req = xmlrpclib.dumps( (), "misc.sync" ).replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urllib2.urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

	def authListener( self, user, pwd ):
		reqUrl = BASE_URL_RID %( self.rid, "authenticateListener" )

		req = xmlrpclib.dumps( ( _inttime(), user, pwd ), \
								"listener.authenticateListener" )
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

		req = xmlrpclib.dumps( ( _inttime(), self.authToken ), \
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
		reqUrl = BASE_URL_LID %( self.rid, self.lid, "getFragment" )

		args = ( _inttime(), self.authToken, stationId, "0", "", "", \
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

		print "addFeedback - stationId: ", stationId
		print "addFeedback - musicId: ", musicId
		print "addFeedback - likeFlag: ", likeFlag
		reqUrl = BASE_URL_LID %( self.rid, self.lid, "addFeedback" )

		matchingSeed = ""
		userSeed = ""
		focusTraitId = ""

		args = ( _inttime(), self.authToken, stationId, musicId, matchingSeed, userSeed, focusTraitId, "", likeFlag, False )

		req = xmlrpclib.dumps( args, "station.addFeedback" )
		print "addFeedback - req: ", req
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		print "addFeedback resp:", resp

		#parsed = xmlrpclib.loads( resp )[0][0]
		#print "addFeedback return:", parsed

		#return parsed

	def addTiredSong( self, musicId ):
		reqUrl = BASE_URL_LID %( self.rid, self.lid, "addTiredSong" )

		req = xmlrpclib.dumps( ( _inttime(), self.authToken, musicId ), \
								"listener.addTiredSong" )
		req = req.replace( "\n", "" )
		enc = crypt.encryptString( req, self.keys['out'] )

		u = urlopen( reqUrl, enc )
		resp = u.read()
		u.close()

		print "addTiredSong resp:", resp


import urllib2
import pickle
import pianoparser
import os

BASE_KEY_URL = "https://raw.github.com/PromyLOPh/pianobar/master/src/libpiano/"

class Key:
	def __init__( self, proto, key ):
		self._key = {}
		( n, p, s ) = key
		self._proto = proto
		self._key["n"] = n
		self._key["p"] = p
		self._key["s"] = s

	def __getitem__( self, key ):
		return self._key[key]

class Keys:
	_keys = None

	def __init__( self, dataDir, proto ):
		self._proto = proto
		self._dataDir = dataDir
		self._keys = {}

	def __getitem__( self, key ):
		return self._keys[key]

	def loadKeys( self, save=True ):
		fromFile = 0
		key_in = self._loadKeyFromFile( os.path.join( self._dataDir,\
													  "key_in" ) )
		if key_in and key_in._proto == self._proto:
			fromFile += 1
		else:
			key_in = self._loadKeyFromURL( BASE_KEY_URL + \
										  "crypt_key_input.h" )
			if key_in:
				key_in = Key( self._proto, key_in )
			else:
				return False

		key_out = self._loadKeyFromFile( os.path.join( self._dataDir,\
													   "key_out" ) )
		if key_out and key_out._proto == self._proto:
			fromFile += 1
		else:
			key_out = self._loadKeyFromURL( BASE_KEY_URL + \
										  "crypt_key_output.h" )
			if key_out:
				key_out = Key( self._proto, key_out )
			else:
				return False

		self._keys['in'] = key_in
		self._keys['out'] = key_out
		if save and fromFile < 2:
			self.saveKeys()
		return True

	def saveKeys( self ):
		print "PANDORA: Saving keys"
		f = None
		try:
			f = open( os.path.join( self._dataDir, "key_in" ), "w" )
			pickle.dump( self._keys['in'], f )
		finally:
			if f: f.close()

		try:
			f = open( os.path.join( self._dataDir, "key_out" ), "w" )
			pickle.dump( self._keys['out'], f )
		finally:
			if f: f.close()

	def forceReDownload( self ):
		print "PANDORA: Forcing key ReDownload"
		if os.path.exists( os.path.join( self._dataDir, "key_in" ) ):
			os.remove( os.path.join( self._dataDir, "key_in" ) )
		if os.path.exists( os.path.join( self._dataDir, "key_out" ) ):
			os.remove( os.path.join( self._dataDir, "key_out" ) )
		return self.loadKeys( True );

	def _loadKeyFromFile( self, keyFile ):
		print "PANDORA: Loading key from file \"%s\"" %keyFile
		if not os.path.isfile( keyFile ):
			return False

		try:
			try:
				f = open( keyFile, "rb" )
				key = pickle.load( f )
			except:
				return False
		finally:
			f.close()

		return key

	def _loadKeyFromURL( self, keyUrl ):
		print "PANDORA: Downloading key from url \"%s\"" %keyUrl
		try:
			f = urllib2.urlopen( keyUrl )
		except urllib2.URLError, w:
			return False
		key = pianoparser.parse_file( f )
		f.close()
		return key

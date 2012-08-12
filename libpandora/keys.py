import urllib2
import pickle
import pianoparser
import os
import sys

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

	def _toDict( self ):
		return { 'proto' : self._proto,
				 'key' : (self._key['n'],self._key['p'],self._key['s']) }

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
				print "PANDORA: No valid Input key"
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
				print "PANDORA: No valid Output key"
				return False

		self._keys['in'] = key_in
		self._keys['out'] = key_out
		if save and fromFile < 2:
			self.saveKeys()
		return True

	def saveKeys( self ):
		print "PANDORA: Saving keys"
		f = None
		print "PANDORA: dataDir = \"%s\"" %self._dataDir
		print "PANDORA: dataDir.isDir? %s" %os.path.isdir( self._dataDir )
		try:
			f = open( os.path.join( self._dataDir, "key_in" ), "wb" )
			pickle.dump( self._keys['in']._toDict(), f, -1 )
		finally:
			if f: f.close()

		try:
			f = open( os.path.join( self._dataDir, "key_out" ), "wb" )
			pickle.dump( self._keys['out']._toDict(), f, -1 )
		finally:
			if f: f.close()

	def forceReFetch( self ):
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
				tmp = pickle.load( f )
				key = Key( tmp['proto'], tmp['key'] )
			except IOError, e:
				print "PANDORA: IOError %d:%s" %( e.errno, e.stderror )
				return False
			except pickle.UnpicklingError, e:
				print "PANDORA: UnpicklingError: %s" %e
				return False
			except:
				print "PANDORA: Unexpected error:%s:%s" %sys.exc_info()[0:2]
				raise
		finally:
			f.close()

		return key

	def _loadKeyFromURL( self, keyUrl ):
		print "PANDORA: Downloading key from url \"%s\"" %keyUrl
		try:
			f = urllib2.urlopen( keyUrl )
		except urllib2.URLError, e:
			print "PANDORA: URLError: %s" %e.reason
			return False
		key = pianoparser.parse_file( f )
		f.close()
		return key

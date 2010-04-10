import pianoparser

class KeyFile:
	def __init__( self, fname ):
		self._key = {}
		( n, p, s ) = pianoparser.parse_file( fname )
		self._key["n"] = n
		self._key["p"] = p
		self._key["s"] = s

	def __getitem__( self, key ):
		return self._key[key]

key_out = KeyFile( "crypt_key_output.h" )
key_in = KeyFile( "crypt_key_input.h" )
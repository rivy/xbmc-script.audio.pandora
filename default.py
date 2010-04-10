import xbmc, xbmcgui
import os
from libpandora.pandora import Pandora
from pandagui import PandaGUI
from pandaplayer import PandaPlayer

__title__ = "Pandora"

scriptPath = os.getcwd().replace(';','')

class PandaException( Exception ):
	pass

class Panda:

	def __init__( self ):
		self.gui = None
		self.pandora = None
		self.playlist = []
		self.curStation = ""
		self.playing = False
		self.skip = False
		self.die = False
		self.settings = xbmc.Settings( path=scriptPath )
		
		fmt = self.settings.getSetting( "format" )
		self.pandora = Pandora( fmt )
		
		self.pandora.sync()
		
		while not self.auth():
			resp = xbmcgui.Dialog().yesno( "Pandora", \
					"Failed to authenticate listener.", \
					"Check username/password and try again.", \
					"Show Settings?" )
			if resp:
				self.settings.openSettings()
			else:
				self.quit()
				return

		self.player = PandaPlayer( panda = self )
		self.gui = PandaGUI( "script-pandora.xml", scriptPath, \
							 "Default", panda = self )
	
	def auth( self ):
		user = self.settings.getSetting( "username" )
		pwd = self.settings.getSetting( "password" )
		if user == "" or pwd == "":
			return False
		return self.pandora.authListener( user, pwd )

	def playStation( self, stationId ):
		self.curStation = stationId
		self.playlist = []
		self.getMoreSongs()
		self.playing = True
		self.playNextSong()

	def getStations( self ):
		return self.pandora.getStations()
	
	def getMoreSongs( self ):
		if self.curStation == "":
			raise PandaException()
		items = []
		fragment = self.pandora.getFragment( self.curStation )
		for s in fragment:
			item = xbmcgui.ListItem( s["songTitle"] )
			item.setIconImage( s["artRadio"] )
			item.setThumbnailImage( s["artRadio"] )
			item.setProperty( "Cover", s["artRadio"] )
			info = { "title"	:	s["songTitle"], \
					 "artist"	:	s["artistSummary"], \
					 "album"	:	s["albumTitle"], \
					 "genre"	:	"".join(s["genre"]), \
					}
			item.setInfo( "music", info )
			items.append( ( s["audioURL"], item ) )
		self.playlist.extend( items )

	def playNextSong( self ):
		if not self.playing:
			raise PandaException()
		try:
			next = self.playlist.pop( 0 )
			self.player.playSong( next )
			art = next[1].getProperty( "Cover" )
			self.gui.setProperty( "AlbumArt", art )
		except IndexError:
			self.getMoreSongs()
		if len( self.playlist ) == 0:
			#Out of songs, grab some more while playing
			self.getMoreSongs()

	def main( self ):
		if self.die:
			return
		self.gui.doModal()
		if self.playing:
			self.player.stop()
		del self.gui
		del self.player

	def stop( self ):
		self.playing = False

	def quit( self ):
		if self.gui != None:
			self.gui.close()
		self.die = True

if __name__ == '__main__':
	if not ( os.path.exists( os.path.join( scriptPath, "crypt_key_input.h" ) ) \
			and os.path.exists( os.path.join( scriptPath, "crypt_key_output.h" ) ) ):
		xbmcgui.Dialog().ok( "Pandora", "Missing encription key files." )
	else:
		panda = Panda()
		panda.main()

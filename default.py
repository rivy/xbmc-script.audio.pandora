import xbmcgui
dlg = xbmcgui.DialogProgress()
dlg.create( "PANDORA", "Loading Script..." )
dlg.update( 0 )
import xbmc, os
import xbmcaddon

from libpandora.pandora import Pandora

from pandagui import PandaGUI
from pandaplayer import PandaPlayer

__title__ = "Pandora"
__script_id__ = "script.xbmc.pandora"
__settings__ = xbmcaddon.Addon(id=__script_id__)

scriptPath = __settings__.getAddonInfo('path')
dataDir = os.path.join( "special://profile/addon_data/%s/" %__script_id__ )

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
		self.settings = __settings__
		
		fmt = int(self.settings.getSetting( "format" ))
		fmt = ( "aacplus", "mp3", "mp3-hifi" )[fmt]
		self.pandora = Pandora( dataDir, fmt )
		
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
		self.gui = PandaGUI( scriptPath, self )

	def auth( self ):
		user = self.settings.getSetting( "username" )
		pwd = self.settings.getSetting( "password" )
		if user == "" or pwd == "":
			return False
		dlg = xbmcgui.DialogProgress()
		dlg.create( "PANDORA", "Logging In..." )
		dlg.update( 0 )
		ret = self.pandora.authListener( user, pwd )
		dlg.close()
		return ret

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

	def skipSong( self ):
		self.skip = True
		self.player.stop()

	def main( self ):
		if self.die:
			return
		self.gui.doModal()
		self.cleanup()
		xbmc.sleep( 500 ) #Wait to make sure everything finishes

	def stop( self ):
		self.playing = False

	def cleanup( self ):
		self.skip = False
		if self.playing:
			self.playing = False
			self.player.stop()
		del self.gui
		del self.player

	def quit( self ):
		if self.gui != None:
			self.gui.close()
		self.die = True

if __name__ == '__main__':
	panda = Panda()
	dlg.close()
	panda.main()

import xbmcgui
import xbmc
import xbmcaddon
import os, sys

__title__ = "Pandora"
__script_id__ = "script.xbmc.pandora"
__settings__ = xbmcaddon.Addon(id=__script_id__)
__version__ = "2.1.0"

print "PANDORA: Initializing v%s" %__version__
print "PANDORA: sys.platform = %s" %sys.platform

dlg = xbmcgui.DialogProgress()
dlg.create( "PANDORA", "Loading Script..." )
dlg.update( 0 )

from pandora.pandora import Pandora, PandoraError

from pandagui import PandaGUI
from pandaplayer import PandaPlayer


scriptPath = __settings__.getAddonInfo('path')

dataDir = os.path.join( "special://profile/addon_data/%s/" %__script_id__ )

#Workaround: open() doesn't translate path correctly on some versions
dataDir = xbmc.translatePath( dataDir )


if __settings__.getSetting( "firstrun" ) == "true":
	print  "PANDORA: First run, showing settings dialog"
	__settings__.openSettings()
	__settings__.setSetting( "firstrun", "false" )

BTN_THUMB_DN = 330
BTN_THUMB_UP = 331
BTN_THUMBED_DN = 337
BTN_THUMBED_UP = 338

class PandaException( Exception ):
	pass

class Panda:

	def __init__( self ):
		self.gui = None
		self.pandora = None
		self.playlist = []
		self.curStation = ""
		self.curSong = None
		self.playing = False
		self.skip = False
		self.die = False
		self.settings = __settings__
		self.player = None
		self.skinName = "Default"
		
		fmt = int(self.settings.getSetting( "format" ))
		fmt = ( "lowQuality", "mediumQuality", "highQuality" )[fmt]
		try:
			self.pandora = Pandora()
			self.pandora.set_audio_format(fmt)
		except PandoraError, e:
			xbmcgui.Dialog().ok( "Pandora", "Error: %s" %e )
			self.die = True
			return

		#Proxy settings
		if self.settings.getSetting( "proxy_enable" ) == "true":
			print "PANDORA: Proxy Enabled"
			proxy_info = {
				"host" : self.settings.getSetting( "proxy_server" ),
				"port" : self.settings.getSetting( "proxy_port" ),
				"user" : self.settings.getSetting( "proxy_user" ),
				"pass" : self.settings.getSetting( "proxy_pass" )
			}
			self.pandora.set_proxy( "http://%(user)s:%(pass)s@%(host)s:%(port)s" % proxy_info )
		
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

		# Get skin from settings.
		# Check if a value is set in the settings. If not then use Default.
		if self.settings.getSetting ( "skin" ) != "":
			self.skinName = self.settings.getSetting( "skin" )
		
		self.player = PandaPlayer( panda = self )

		self.gui = PandaGUI( "script-pandora.xml", scriptPath, self.skinName)
		
		self.gui.setPanda( self )

	def auth( self ):
		user = self.settings.getSetting( "username" )
		pwd = self.settings.getSetting( "password" )
		if user == "" or pwd == "":
			return False
		dlg = xbmcgui.DialogProgress()
		dlg.create( "PANDORA", "Logging In..." )
		dlg.update( 0 )
		try:
			self.pandora.connect(user, pwd)
		except PandoraError, e:
			return 0;
		dlg.close()
		return 1

	def playStation( self, stationId ):
		self.curStation = stationId
		self.curSong = None
		self.playlist = []
		self.getMoreSongs()
		self.playing = True
		self.playNextSong()

	def getStations( self ):
		self.pandora.get_stations()
		return self.pandora.stations
	
	def getMoreSongs( self ):
		print "PANDORA: getting more songs"
		if self.curStation == "":
			raise PandaException()
		items = []
		station = self.pandora.get_station_by_id(self.curStation);
		songs = station.get_playlist()
		for song in songs:
			print "PANDORA: Adding song %s" % song.title
			thumbnailArtwork = self.settings.getSetting( "thumbnailArtwork" )
			thumbnail = song.artRadio
	
			item = xbmcgui.ListItem( song.title )
			item.setIconImage( thumbnail )
			item.setThumbnailImage( thumbnail )
			item.setProperty( "Cover", thumbnail )
			if song.rating_str != None:
				item.setProperty( "Rating", song.rating_str )
			else:
				item.setProperty( "Rating", "" )
			info = { "title"	:	song.title, \
				 "artist"	:	song.artist, \
				 "album"	:	song.album, \
				}
			print "PANDORA: item info = %s" % info
			item.setInfo( "music", info )
			items.append( ( song.audioUrl, item, song ) )

		self.playlist.extend( items )

	def playNextSong( self ):
		if not self.playing:
			raise PandaException()
		try:
			next = self.playlist.pop( 0 )
			self.player.playSong( next )
			art = next[1].getProperty( "Cover" )
			self.gui.setProperty( "AlbumArt", art )
			self.curSong = next
			# FIXIT - This should move elsewhere:
			rating = next[1].getProperty( "Rating" )
			if rating == "":			# No rating
				self.gui.getControl(BTN_THUMB_DN).setVisible(True)
				self.gui.getControl(BTN_THUMBED_DN).setVisible(False)
				self.gui.getControl(BTN_THUMB_UP).setVisible(True)
				self.gui.getControl(BTN_THUMBED_UP).setVisible(False)
			elif rating == 'ban':		# Hate
				self.gui.getControl(BTN_THUMB_DN).setVisible(False)
				self.gui.getControl(BTN_THUMBED_DN).setVisible(True)
				self.gui.getControl(BTN_THUMB_UP).setVisible(True)
				self.gui.getControl(BTN_THUMBED_UP).setVisible(False)
			elif rating == 'love':			# Love
				self.gui.getControl(BTN_THUMB_DN).setVisible(True)
				self.gui.getControl(BTN_THUMBED_DN).setVisible(False)
				self.gui.getControl(BTN_THUMB_UP).setVisible(False)
				self.gui.getControl(BTN_THUMBED_UP).setVisible(True)
			else:
				print "PANDORA: !!!! Unrecognised rating"
		except IndexError:
			self.curSong = None
			self.getMoreSongs()

		if len( self.playlist ) == 0:
			#Out of songs, grab some more while playing
			self.getMoreSongs()

	def skipSong( self ):
		self.skip = True
		self.player.stop()

	def addFeedback( self, likeFlag ):
		if not self.playing:
			raise PandaException()
		self.curSong[2].rate(likeFlag);

	def addTiredSong( self ):
		if not self.playing:
			raise PandaException()
		musicId = self.curSong[2].set_tired();

	def main( self ):
		if self.die:
			return
		self.gui.doModal()
		self.cleanup()
		xbmc.sleep( 500 ) #Wait to make sure everything finishes

	def stop( self ):
		self.playing = False
		if self.player and self.player.timer\
				and self.player.timer.isAlive():
			self.player.timer.stop()

	def cleanup( self ):
		self.skip = False
		if self.playing:
			self.playing = False
			self.player.stop()
		del self.gui
		del self.player

	def quit( self ):
		if self.player and self.player.timer\
				and self.player.timer.isAlive():
			self.player.timer.stop()
		if self.gui != None:
			self.gui.close()
		self.die = True

if __name__ == '__main__':
	if __settings__.getSetting( "username" ) == "" or \
		__settings__.getSetting( "password" ) == "":
		xbmcgui.Dialog().ok( "Pandora", \
			"Username and/or password not specified" )
		__settings__.setSetting( "firstrun", "true" )
	else:
		panda = Panda()
		dlg.close()
		panda.main()

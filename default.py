import xbmcgui
import xbmc
import xbmcaddon
import os, sys

__settings__  = xbmcaddon.Addon()
__script_id__ = __settings__.getAddonInfo('id')
__title__     = __settings__.getAddonInfo('name')
__version__   = __settings__.getAddonInfo('version')

TITLE = __title__.upper()

print TITLE+": Initializing v%s" % __version__
print TITLE+": sys.platform = %s" % sys.platform

dlg = xbmcgui.DialogProgress()
dlg.create( TITLE, "Loading Script..." )
dlg.update( 0 )

from pithos.pandora.pandora import Pandora, PandoraError
import pithos.pandora.data

from pandagui import PandaGUI
from pandaplayer import PandaPlayer

scriptPath = __settings__.getAddonInfo('path')

dataDir = os.path.join( "special://profile/addon_data/%s/" %__script_id__ )

#Workaround: open() doesn't translate path correctly on some versions
dataDir = xbmc.translatePath( dataDir )

if __settings__.getSetting( "firstrun" ) == "true":
	print  TITLE+": First run, showing settings dialog"
	__settings__.openSettings()
	__settings__.setSetting( "firstrun", "false" )

BTN_THUMB_DN = 330
BTN_THUMB_UP = 331
BTN_THUMBED_DN = 337
BTN_THUMBED_UP = 338

import urllib2

class My_Pandora( Pandora ):
	def __init__( self ):
		Pandora.__init__( self )
		self.set_proxy(None)

	def set_proxy(self, proxy):
		if proxy:
			proxy_handler = urllib2.ProxyHandler({'http': proxy})
			self.opener = urllib2.build_opener(proxy_handler)
		else:
			self.opener = urllib2.build_opener()


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
			self.pandora = My_Pandora()
			self.pandora.set_audio_quality(fmt)
		except PandoraError, e:
			xbmcgui.Dialog().ok( __title__, "Error: %s" %e )
			self.die = True
			return

		#Proxy settings
		if self.settings.getSetting( "proxy_enable" ) == "true":
			print TITLE+": Proxy Enabled"
			proxy_info = {
				"host" : self.settings.getSetting( "proxy_server" ),
				"port" : self.settings.getSetting( "proxy_port" ),
				"user" : self.settings.getSetting( "proxy_user" ),
				"pass" : self.settings.getSetting( "proxy_pass" )
			}
			self.pandora.set_proxy( "http://%(user)s:%(pass)s@%(host)s:%(port)s" % proxy_info )

		while not self.auth():
			resp = xbmcgui.Dialog().yesno( __title__, \
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
		client_id = pithos.pandora.data.default_client_id
		pandoraone = self.settings.getSetting( "pandoraone" )
		if pandoraone == "true":
			client_id = pithos.pandora.data.default_one_client_id
		dlg = xbmcgui.DialogProgress()
		dlg.create( TITLE, "Logging In..." )
		dlg.update( 0 )
		try:
			self.pandora.connect(pithos.pandora.data.client_keys[client_id], user, pwd)
		except PandoraError, e:
			return 0;
		dlg.close()
		return 1

	def playStation( self, stationId ):
		self.curStation = stationId
		station = self.pandora.get_station_by_id(self.curStation);
		dlg = xbmcgui.DialogProgress()
		dlg.create( TITLE, "Opening Pandora station: " + station.name )
		dlg.update( 0 )
		self.settings.setSetting( 'last_station_id', stationId )
		self.curSong = None
		self.playlist = []
		self.getMoreSongs()
		self.playing = True
		self.playNextSong()
		dlg.close()

	def getStations( self ):
		self.pandora.get_stations()
		return self.pandora.stations

	def getMoreSongs( self ):
		print TITLE+": getting more songs"
		if self.curStation == "":
			raise PandaException()
		items = []
		station = self.pandora.get_station_by_id(self.curStation);
		songs = station.get_playlist()
		for song in songs:
			print TITLE+": Adding song %s" % song.title
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
			## HACK: set fictional duration to enable scrobbling
			if self.settings.getSetting( "scrobble_hack" ) == "true":
				duration = 60 * ( int(self.settings.getSetting( "scrobble_hack_time" )) + 1 )
				info["duration"] = duration
			print TITLE+": item info = %s" % info
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
				print TITLE+": !!!! Unrecognised rating"
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
		xbmcgui.Dialog().ok( __title__, \
			"Username and/or password not specified" )
		__settings__.setSetting( "firstrun", "true" )
	else:
		panda = Panda()
		dlg.close()
		panda.main()

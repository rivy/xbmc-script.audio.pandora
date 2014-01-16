import xbmc
from threading import Timer

import xbmcaddon

_settings   = xbmcaddon.Addon()
_name       = _settings.getAddonInfo('name')

_NAME = _name.upper()

class PandaPlayer( xbmc.Player ):

	def __init__( self, core=None, panda=None ):
		xbmc.Player.__init__( self, xbmc.PLAYER_CORE_MPLAYER )
		self.panda = panda
		self.timer = None
		self.playNextSong_delay = 0.5

	def playSong( self, item ):
		print _NAME+": Item 0 %s" % item[0]
		print _NAME+": Item 1 %s" % item[1]
		self.play( item[0], item[1] )

	def play( self, url, item ):
		xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play( url, item )

	def onPlayBackStarted( self ):
		print _NAME+": onPlayBackStarted: %s" %self.getPlayingFile()
		if self.panda.playing:
			# ToDO: ? remove checks for pandora.com / p-cdn.com (are they needed? could be a maintainence headache if the cdn changes...)
			if not "pandora.com" in self.getPlayingFile():
				if not "p-cdn.com" in self.getPlayingFile():
					self.panda.playing = False
					self.panda.quit()
			else:
				# show visualization (disappears after each song...)
				xbmc.executebuiltin( "ActivateWindow( 12006 )" )

	def onPlayBackEnded( self ):
		print _NAME+": onPlayBackEnded"
		self.stop()
		print _NAME+": playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.skip:
			self.panda.skip = False
		if self.panda.playing:
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()

	def onPlayBackStopped( self ):
		print _NAME+": onPlayBackStopped"
		self.stop()
		print _NAME+": playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.playing and self.panda.skip:
			self.panda.skip = False
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()
		else:
			if xbmc.getCondVisibility('Skin.HasSetting(PandoraVis)'):
				# turn off visualization
				xbmc.executebuiltin('Skin.Reset(PandoraVis)')
			self.panda.stop()

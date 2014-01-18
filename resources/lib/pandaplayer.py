import xbmc
from threading import Timer

import xbmcaddon

_settings   = xbmcaddon.Addon()
_name       = _settings.getAddonInfo('name')

_NAME = _name.upper()

class PandaPlayer( xbmc.Player ):

	def __init__( self, core=None, panda=None ):
		xbmc.Player.__init__( self )
		self.panda = panda
		self.timer = None
		self.playNextSong_delay = 0.5

	def playSong( self, item ):
		print _name+": playSong: item[url] %s" % item[0]
		print _name+": playSong: item[item] %s" % item[1]
		self.play( item[0], item[1] )

	def play( self, url, item ):
		# override play() to force use of PLAYER_CORE_MPLAYER
		xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play( url, item )

		# NOTE: using PLAYER_CORE_MPLAYER is necessary to play .mp4 streams (low & medium quality from Pandora)
		#   ... unfortunately, using "xbmc.Player([core]) is deprecated [ see URLref: http://forum.xbmc.org/showthread.php?tid=173887&pid=1516662#pid1516662 ]
		#   ... and it may be removed from Gotham [ see URLref: https://github.com/xbmc/xbmc/pull/1427 ]
		# ToDO: discuss with the XBMC Team what the solution to this problem would be

	def onPlayBackStarted( self ):
		print _name+": onPlayBackStarted: %s" %self.getPlayingFile()
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
		print _name+": onPlayBackEnded"
		self.stop()
		print _name+": playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.skip:
			self.panda.skip = False
		if self.panda.playing:
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()

	def onPlayBackStopped( self ):
		print _name+": onPlayBackStopped"
		self.stop()
		print _name+": playing = %s" %self.panda.playing
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

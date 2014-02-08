# (emacs/sublime) -*- mode: python; tab-width: 4; -st-draw_white_space: 'all'; -*-
from threading import Timer
import xbmc
import xbmcaddon
import os, sys

from utils import *

class PandaPlayer( xbmc.Player ):

	def __init__( self, core=None, panda=None ):
		log.debug( "PandaPlayer.__init__( CORE, PANDA )" )
		xbmc.Player.__init__( self )
		self.panda = panda
		self.timer = None
		self.playNextSong_delay = 0.5
		log.debug( "PandaPlayer.__init__ :: end" )

	def playSong( self, item ):
		log.debug( "PandaPlayer.playSong()" )
		log.debug( "PandaPlayer.playSong: item[url] %s" % item[0] )
		log.debug( "PandaPlayer.playSong: item[item] %s" % item[1] )
		self.play( item[0], item[1] )
		log.debug( "PandaPlayer.playSong() :: end" )

	def play( self, url, item ):
		log.debug( "PandaPlayer.play( '%s', '%s' )" % ( url, item ) )
		# override play() to force use of PLAYER_CORE_MPLAYER
		xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play( url, item )

		# NOTE: using PLAYER_CORE_MPLAYER is necessary to play .mp4 streams (low & medium quality from Pandora)
		#   ... unfortunately, using "xbmc.Player([core]) is deprecated [ see URLref: http://forum.xbmc.org/showthread.php?tid=173887&pid=1516662#pid1516662 ]
		#   ... and it may be removed from Gotham [ see URLref: https://github.com/xbmc/xbmc/pull/1427 ]
		# ToDO: discuss with the XBMC Team what the solution to this problem would be
		log.debug( "PandaPlayer.play() :: end" )

	def onPlayBackStarted( self ):
		log.debug( "PandaPlayer.onPlayBackStarted: %s" %self.getPlayingFile() )
		if self.panda.playing:
			### ToDO: ? remove checks for pandora.com / p-cdn.com (are they needed? could be a maintainence headache if the cdn changes...)
			##if not "pandora.com" in self.getPlayingFile():
			##	if not "p-cdn.com" in self.getPlayingFile():
			##		self.panda.playing = False
			##		self.panda.quit()
			##else:
				# show visualization (o/w disappears when song is started...)
				xbmc.executebuiltin( "ActivateWindow( 12006 )" )
		log.debug( "PandaPlayer.onPlayBackStarted :: end" )

	def onPlayBackEnded( self ):
		log.debug( "PandaPlayer.onPlayBackEnded()" )
		self.stop()
		log.debug( "playing = %s" %self.panda.playing )
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.skip:
			self.panda.skip = False
		if self.panda.playing:
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()
		log.debug( "PandaPlayer.onPlayBackEnded() :: end" )

	def onPlayBackStopped( self ):
		log.debug( "PandaPlayer.onPlayBackStopped()" )
		self.stop()
		log.debug( "playing = %s" %self.panda.playing )
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.playing and self.panda.skip:
			self.panda.skip = False
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()
		else:
			if xbmc.getCondVisibility('Skin.HasSetting(PandoraVis)'):
				# show UI
				xbmc.executebuiltin('Skin.Reset(PandoraVis)')
			self.panda.stop()
		log.debug( "PandaPlayer.onPlayBackStopped() :: end" )

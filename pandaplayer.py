import xbmc
from threading import Timer

class PandaPlayer( xbmc.Player ):

	def __init__( self, core=None, panda=None ):
		xbmc.Player.__init__( self )
		self.panda = panda
		self.timer = None
		self.playNextSong_delay = 0.5

	def playSong( self, item ):
		print "PANDORA: Item 0 %s" % item[0]
		print "PANDORA: Item 1 %s" % item[1]
		self.play( item[0], item[1] )

	def play( self, url, item ):
		xbmc.Player().play( url, item )

	def onPlayBackStarted( self ):
		print "PANDORA: onPlayBackStarted: %s" %self.getPlayingFile()
		if self.panda.playing:
			if not "pandora.com" in self.getPlayingFile():
				if not "p-cdn.com" in self.getPlayingFile():
					self.panda.playing = False
					self.panda.quit()
			else:
				# show visualization (disappears after each song...)
				xbmc.executebuiltin( "ActivateWindow( 12006 )" )

	def onPlayBackEnded( self ):
		print "PANDORA: onPlayBackEnded"
		self.stop()
		print "PANDORA: playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.skip:
			self.panda.skip = False
		if self.panda.playing:
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()

	def onPlayBackStopped( self ):
		print "PANDORA: onPlayBackStopped"
		self.stop()
		print "PANDORA: playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.playing:
			if self.panda.skip:
				self.panda.skip = False
			self.timer = Timer( self.playNextSong_delay, self.panda.playNextSong )
			self.timer.start()

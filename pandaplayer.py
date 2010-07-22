import xbmc
from threading import Timer

class PandaPlayer( xbmc.Player ):

	def __init__( self, core=None, panda=None ):
		xbmc.Player.__init__( self, xbmc.PLAYER_CORE_MPLAYER )
		self.panda = panda
		self.timer = None

	def playSong( self, item ):
		self.play( item[0], item[1] )
		print "Self Play"

	def play( self, url, item ):
		xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play( url, item )
		print "XBMC Player Started"

	def onPlayBackStarted( self ):
		print "PANDORA: onPlayBackStarted: %s" %self.getPlayingFile()
		if self.panda.playing:
			print "RSP PANDA PLAYING"
			if not "pandora.com" in self.getPlayingFile():
				print "RSP ERROR PLAYING!"
				self.panda.playing = False
				self.panda.quit()
			else:
				print "RSP STARTING VISUALIZATION"
				#Show Visualization (disappears after each song...)
				xbmc.executebuiltin( "ActivateWindow( 12006 )" )
		else:
			print "RSP PANDA NOT PLAYING"

	def onPlayBackEnded( self ):
		print "PANDORA: onPlayBackEnded"
		print "MAKING SURE PREVIOUS PLAYER IS STOPPED!"
		self.stop()
		print "PANDORA: playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.skip:
			self.panda.skip = False
		if self.panda.playing:
			self.timer = Timer( 0.5, self.panda.playNextSong )
			self.timer.start()
		#self.panda.playNextSong()

	def onPlayBackStopped( self ):
		print "PANDORA: onPlayBackStopped"
		print "MAKING SURE PREVIOUS PLAYER IS STOPPED!"
		self.stop()
		print "PANDORA: playing = %s" %self.panda.playing
		if self.timer and self.timer.isAlive():
			self.timer.cancel()
		if self.panda.playing:
			if self.panda.skip:
				self.panda.skip = False
			self.timer = Timer( 0.5, self.panda.playNextSong )
			self.timer.start()
		#self.panda.playNextSong()

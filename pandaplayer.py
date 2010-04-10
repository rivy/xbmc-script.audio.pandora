import xbmc
from threading import Timer

class PandaPlayer( xbmc.Player ):

	def __init__( self, core=None, panda=None ):
		xbmc.Player.__init__( self, xbmc.PLAYER_CORE_MPLAYER )
		self.panda = panda

	def playSong( self, item ):
		self.play( item[0], item[1] )

	def play( self, url, item ):
		xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play( url, item )

	def onPlayBackStarted( self ):
		print "PANDORA: onPlayBackStarted: %s" %self.getPlayingFile()
		if self.panda.playing:
			if not "pandora.com" in self.getPlayingFile():
				self.panda.playing = False
				self.panda.quit()

	def onPlayBackEnded( self ):
		print "PANDORA: onPlayBackEnded"
		print "PANDORA: playing = %s" %self.panda.playing
		if self.panda.playing:
			xbmc.sleep(1000) #sleep a bit to make sure player ends
			print "PANDORA: playNextSong"
			self.panda.playNextSong()

	def onPlayBackStopped( self ):
		print "PANDORA: onPlayBackStopped"
		print "PANDORA: playing = %s" %self.panda.playing
		if self.panda.playing:
			print "PANDORA: playNextSong"
			self.panda.playNextSong()
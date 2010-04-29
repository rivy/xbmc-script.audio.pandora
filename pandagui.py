import xbmc, xbmcgui
from libpandora.pandora import Pandora

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

ACTION_PREVIOUS_MENU = 10
ACTION_NEXT_ITEM = 14

BTN_THUMB_DN = 330
BTN_THUMB_UP = 331
BTN_PLAY_PAUSE = 332
BTN_SKIP = 333
BTN_INFO = 334

class PandaGUI(xbmcgui.WindowXMLDialog):
	def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,panda=None):
		xbmcgui.WindowXMLDialog.__init__( self, strXMLname, strFallbackPath, strDefaultName, bforeFallback )
		self.panda = panda

	def onInit(self):
		print "PANDORA: Window Initalized"
		self.list = self.getControl(200)
		dlg = xbmcgui.DialogProgress()
		dlg.create( "PANDORA", "Fetching Stations" )
		dlg.update( 0 )
		for s in self.panda.getStations():
			tmp = xbmcgui.ListItem(s["stationName"])
			tmp.setProperty( "stationId", s["stationId"] )
			self.list.addItem(tmp)
		dlg.close()

	def onAction(self, action):
		buttonCode =  action.getButtonCode()
		actionID   =  action.getId()
		if (actionID == ACTION_PREVIOUS_MENU ):
			self.panda.quit()
		elif (actionID == ACTION_NEXT_ITEM ):
			self.panda.skipSong()

	def onClick(self, controlID):
		if (controlID == 200): #List Item
			selItem = self.list.getSelectedItem()
			self.panda.playStation( selItem.getProperty("stationId") )
		elif self.panda.playing:
			if controlID == BTN_THUMB_DN:
				pass #TODO
			elif controlID == BTN_THUMB_UP:
				pass #TODO
			elif controlID == BTN_PLAY_PAUSE:
				pass #Handled by skin currently, further functionality TBD
			elif controlID == BTN_SKIP:
				self.panda.playNextSong()
			elif controlID == BTN_INFO:
				pass #TODO

	def onFocus(self, controlID):
		pass

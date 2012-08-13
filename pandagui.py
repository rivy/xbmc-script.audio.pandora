import xbmc, xbmcgui

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NEXT_ITEM = 14
ACTION_NAV_BACK = 92

BTN_THUMB_DN = 330
BTN_THUMB_UP = 331
BTN_PLAY_PAUSE = 332
BTN_SKIP = 333
BTN_INFO = 334
BTN_HIDE = 335

BTN_TIRED = 336
BTN_THUMBED_DN = 337
BTN_THUMBED_UP = 338

class PandaGUI(xbmcgui.WindowXMLDialog):

	def setPanda( self, panda ):
		self.panda = panda

	def onInit(self):
		print "PANDORA: Window Initalized!!!"
		self.list = self.getControl(200)
		dlg = xbmcgui.DialogProgress()
		dlg.create( "PANDORA", "Fetching Stations" )
		dlg.update( 0 )
		for s in self.panda.getStations():
			tmp = xbmcgui.ListItem(s.name)
			tmp.setProperty( "stationId", s.id )
			self.list.addItem(tmp)
		dlg.close()
		self.getControl(BTN_THUMBED_DN).setVisible(False)
		self.getControl(BTN_THUMBED_UP).setVisible(False)

		logo = self.getControl(100)
		if self.panda.settings.getSetting( "logo" ) == "false":
			logo.setPosition(-100, -100)

	def onAction(self, action):
		buttonCode =  action.getButtonCode()
		actionID   =  action.getId()
		if ( actionID in ( ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, \
                           ACTION_PARENT_DIR ) ):
			if xbmc.getCondVisibility( 'Skin.HasSetting(PandoraVis)' ):
				xbmc.executebuiltin( 'Skin.Reset(PandoraVis)' )
				#xbmc.executebuiltin( "SetProperty(HidePlayer,False)" )
			else:
				self.panda.quit()


		elif (actionID == ACTION_NEXT_ITEM ):
			self.panda.skipSong()

	def onClick(self, controlID):
		if (controlID == 200): #List Item
			selItem = self.list.getSelectedItem()
			self.panda.playStation( selItem.getProperty("stationId") )
		elif self.panda.playing:
			if controlID == BTN_THUMB_DN:
				self.getControl(BTN_THUMB_DN).setVisible(False)
				self.getControl(BTN_THUMBED_DN).setVisible(True)
				self.getControl(BTN_THUMB_UP).setVisible(True)
				self.getControl(BTN_THUMBED_UP).setVisible(False)
				self.panda.addFeedback( 'ban' )
				self.panda.playNextSong()
			elif controlID == BTN_THUMB_UP:
				self.getControl(BTN_THUMB_DN).setVisible(True)
				self.getControl(BTN_THUMBED_DN).setVisible(False)
				self.getControl(BTN_THUMB_UP).setVisible(False)
				self.getControl(BTN_THUMBED_UP).setVisible(True)
				self.panda.addFeedback( 'love' )
			elif controlID == BTN_PLAY_PAUSE:
				pass #Handled by skin currently, further functionality TBD
			elif controlID == BTN_SKIP:
				self.panda.playNextSong()
			elif controlID == BTN_INFO:
				pass #TODO
			elif controlID == BTN_TIRED:
				#obj = self.getControl(BTN_TIRED)
				#for attr in dir(obj):
				#	print ">>> obj.%s = %s" % (attr, getattr(obj, attr))
				self.panda.addTiredSong()
				self.panda.playNextSong()
			elif controlID == BTN_HIDE:
				pass #Handled by skin

	def onFocus(self, controlID):
		pass

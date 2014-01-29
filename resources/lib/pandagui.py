from threading import Timer
import xbmc
import xbmcaddon
import xbmcgui
import os, sys

_settings   = xbmcaddon.Addon()
_name       = _settings.getAddonInfo('name')

from utils import *

_NAME = _name.upper()

# ToDO: DRY these IDs into constants.py
##
# URLref: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

# URLref: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NEXT_ITEM = 14
ACTION_NAV_BACK = 92

# skin control IDs
BTN_THUMB_DN = 330
BTN_THUMB_UP = 331
BTN_PLAY_PAUSE = 332
BTN_SKIP = 333
BTN_INFO = 334
BTN_HIDE = 335

BTN_TIRED = 336
BTN_THUMBED_DN = 337
BTN_THUMBED_UP = 338

PANDORA_LOGO_ID = 100
STATION_LISTBOX_ID = 200
##

class PandaGUI(xbmcgui.WindowXMLDialog):

	# bind_onAction ( actionID, f( self, action ) )
	# bind_onClick ( controlID, f( self ) )
	# mapControlClick ( controlID ): try return self.onControlClick_fmap[ controlID ] except return None
	# mapAction ( actionID ): try return self.onAction_fmap[ controlID ] except return None

	def setPanda( self, panda ):
		self.panda = panda

	def onInit(self):
		log.debug( "PandaGUI.onInit()" )
		play_station_n = -1
		last_station_id = self.panda.settings.getSetting('last_station_id')
		auto_start = self.panda.settings.getSetting('auto_start')

		self.onControlClick_fmap = {};		# controlID => f( self )
		self.onControlFocus_fmap = {};		# controlID => f( self )
		self.onAction_fmap = {}; 			# actionID => f( self, action )

		self.station_listbox = self.getControl( STATION_LISTBOX_ID )
		dlg = xbmcgui.DialogProgress()
		dlg.create( _NAME, "Fetching Stations" )
		dlg.update( 0 )
		stations = {}
		station_names = []
		for s in self.panda.getStations():
			s.name = s.name.encode('utf-8')
			s.id = s.id.encode('utf-8')
			log.debug( "station[%s]( id, isQuickMix ) = ( %s, %s )" % ( s.name, s.id, s.isQuickMix ) )
			if s.isQuickMix:
				s.name = "* [ "+s.name+" ]"
			tmp = xbmcgui.ListItem(s.name)
			tmp.setProperty( "stationId", s.id )
			stations[s.name] = tmp
			station_names.append( s.name )
		if self.panda.settings.getSetting( "sort_stations" ) == "true":
			station_names = sorted( station_names )
		station_list = []
		for name in station_names:
			station_list.append( stations[name] )
			if stations[name].getProperty('stationId') == last_station_id:
				play_station_n = len(station_list) - 1
			log.debug( "station_list[%s]{name, id} = {%s, %s}" % ( len(station_list)-1, station_list[len(station_list)-1].getLabel(), station_list[len(station_list)-1].getProperty('stationId')) )
		self.station_listbox.addItems( station_list )
		dlg.close()
		self.getControl(BTN_THUMBED_DN).setVisible(False)
		self.getControl(BTN_THUMBED_UP).setVisible(False)

		logo = self.getControl( PANDORA_LOGO_ID )
		if self.panda.settings.getSetting( "logo" ) == "false":
			logo.setPosition(-100, -100)

		if ( auto_start == "true" ) & ( play_station_n >= 0 ):
			dlg.create( _NAME, "Now starting station: "+station_list[play_station_n].getLabel() )
			dlg.update( 0 )
			self.station_listbox.selectItem( play_station_n )
			self.setFocusId( STATION_LISTBOX_ID )
			log( "Initiating station stream (station_id = %s)" % last_station_id )
			##log.debug( "station_list[%s]{name, id} = {%s, %s}" % ( play_station_n, station_list[play_station_n].getLabel().encode('utf-8'), station_list[play_station_n].getProperty('stationId')) )
			##log.debug( "station_list[%s]{name, id} = {%s, %s}" % ( play_station_n, self.station_listbox.getSelectedItem().getLabel().encode('utf-8'), self.station_list.getSelectedItem().getProperty('stationId')) )
			self.panda.playStation( last_station_id )
			dlg.close
		log( "UI: Window initalized" )
		log.debug( "PandaGUI.onInit() :: end" )

	def onAction(self, action):
		log.debug( "PandaGUI.onAction( %s )" % action.getId() )
		##buttonCode =  action.getButtonCode()
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
		log.debug( "PandaGUI.onAction() :: end" )

	def onClick(self, controlID):
		log.debug( "PandaGUI.onClick( %s )" % controlID )
		if (controlID == STATION_LISTBOX_ID): # station list control
			selItem = self.station_list.getSelectedItem()
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
				#	log.debug( ">>> obj.%s = %s" % (attr, getattr(obj, attr)) )
				self.panda.addTiredSong()
				self.panda.playNextSong()
			elif controlID == BTN_HIDE:
				pass #Handled by skin
				self.hideUI()
		log.debug( "PandaGUI.onClick() :: end" )

	def onFocus(self, controlID):
		pass

	def showUI ( self ):
		xbmc.executebuiltin( 'Skin.Reset(PandoraVis)' )

	def hideUI ( self ):
		log( "PandaGUI.hideUI()" )
		xbmc.executebuiltin( "Skin.SetBool(PandoraVis)" )
		bg_visuals = ( 'none', 'visualizer', 'screensaver')[ int(self.panda.settings.getSetting( "bg_visuals" )) ]
		if ( bg_visuals == 'visualizer' ):
			log( "PandaGUI.hideUI(): activate 'Audio Visualizer'" )
			#xbmc.executebuiltin( "ActivateWindow( visualiser )" )
			##xbmc.executebuiltin( "ActivateWindow( 12006 )" )
		if ( bg_visuals == 'screensaver' ):
			log( "PandaGUI.hideUI(): activate 'Screensaver'" )
			xbmc.executebuiltin( "ActivateScreensaver" )

	def isVisibleUI ( self ):
		return xbmc.getCondVisibility( 'Skin.HasSetting(PandoraVis)' )

	def do_Quit ( self ):
		self.panda.quit()

	def do_NavigateBack ( self ):
		if not self.isVisibleUI:
			self.showUI()
		else:
			self.do_Quit()

	def do_NextSong ( self ):
		self.panda.skipSong()

	def do_station_list_PageNext ( self ):
		do_station_list_Next ( self, step=10 )

	def do_station_list_PagePrev ( self ):
		do_station_list_Prev ( self, step=10 )

	def do_station_list_Next ( self, step=1 ):
		l = self.station_list.size()
		if ( l > 0 ):
			n = self.station_list.getSelectedPosition() + step
			if ( n >= l ):
				n = l - 1
			self.station_list.selectItem( n )

	def do_station_list_Prev ( self, step=1 ):
		l = self.station_list.size()
		if ( l > 0 ):
			n = self.station_list.getSelectedPosition() - step
			if ( n < 0 ):
				n = 0
			self.station_list.selectItem( n )

	def do_station_list_Select ( self ):
		selItem = self.station_list.getSelectedItem()
		self.panda.playStation( selItem.getProperty("stationId") )

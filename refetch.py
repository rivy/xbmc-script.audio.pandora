import xbmc
import xbmcgui
import libpandora.keys
import libpandora.pandora

if __name__ == '__main__':
	dlg = xbmcgui.DialogProgress()
	dlg.create( "PANDORA", "ReFetching Keys..." )
	dlg.update( 0 )
	dataDir = "special://profile/addon_data/script.xbmc.pandora"
	dataDir = xbmc.translatePath( dataDir )
	proto = libpandora.pandora.PROTOCOL_VERSION
	keys = libpandora.keys.Keys( dataDir, proto )
	keys.forceReFetch()
	dlg.close()

# (emacs/sublime) -*- mode: python; tab-width: 4; -st-draw_white_space: 'all'; -*-
import xbmc
import xbmcaddon
import os, sys

_settings   = xbmcaddon.Addon()
_name       = _settings.getAddonInfo('name')

class Log:
	prefix = _name

	# URLref: http://mirrors.xbmc.org/docs/python-docs [see xbmc]

	def __call__ ( self, msg, log_level=xbmc.LOGNOTICE ):
		# default to xbmc.LOGNOTICE level (minimum level to print to xbmc log under usual settings)
		xbmc.log( msg=self.__format(msg), level=log_level )

	def debug ( self, msg ):
		xbmc.log( msg=self.__format(msg), level=xbmc.LOGDEBUG )

	def info ( self, msg ):
		xbmc.log( msg=self.__format(msg), level=xbmc.LOGINFO )

	def notice ( self, msg ):
		xbmc.log( msg=self.__format(msg), level=xbmc.LOGNOTICE )

	def warning ( self, msg ):
		xbmc.log( msg=self.__format(msg), level=xbmc.LOGWARNING )

	def error ( self, msg ):
		xbmc.log( msg=self.__format(msg), level=xbmc.LOGERROR )

	def fatal ( self, msg ):
		xbmc.log( msg=self.__format(msg), level=xbmc.LOGFATAL )

	def __format ( self, msg ):
		if isinstance( msg, basestring ):
			if not isinstance( msg, unicode ):
				# [str -> unicode]
				msg = unicode( msg, 'utf-8' ) 	# .or. msg.decode('utf-8')
		message = u'%s: %s' % (self.prefix, msg)
		# XBMC log needs output to be 'ascii' compatible
		return message.encode('utf-8') 	# [unicode -> str]

log = Log()

####

import logging

class XBMCLogHandler( logging.Handler ):
    # log level transform ( logging.X => xbmc.LOGY )
    log_level_transform = {
        'debug' : xbmc.LOGDEBUG,
        'info' : xbmc.LOGINFO,
        'notice' : xbmc.LOGNOTICE,
        'warning' : xbmc.LOGWARNING,
        'error' : xbmc.LOGERROR,
        'critical' : xbmc.LOGFATAL,
        }

    def __init__( self ):
        logging.Handler.__init__( self )
        self.setLevel( logging.DEBUG )
        self.setFormatter( logging.Formatter( '** %(message)s' ) )

    def emit( self, record ):
        # record.message is the log message
        log( self.format(record), self.log_level_transform[ record.levelname.lower() ] )

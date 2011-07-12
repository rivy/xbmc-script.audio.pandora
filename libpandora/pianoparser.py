import re

def parse_file( f ):
	
	lines = f.readlines()
	f.close()
	lines = cleanup( lines )
	code = "".join( lines ).split( ";" )
	
	n = 0
	p = []
	s = []
	
	for i in code:
		m = re.search( "_key_(\w)", i )
		if m:
			if m.group(1) == 'n':
				n = int( re.search( "_key_n = (\d*)", i ).group(1) )
			elif m.group(1) == 'p':
				a = re.search( "\{(.*)\}", i ).group(1)
				p = a.split( "," )
				if p[-1] == "": p = p[:-1]
				p = [ long( x, 0 ) for x in p ]
			elif m.group(1) == 's':
				a = re.search( "\{\{(.*)\}\}", i ).group(1)
				b = re.split( r"},\s*{", a )
				for c in b:
					d = c.split( "," )
					if d[-1] == "": d = d[:-1]
					d = [ long( x, 0 ) for x in d ]
					s.append( d )
	return ( n, p, s )
	
#Takes in a collection of lines.
#removes all surrounding whitespace, comments and empty lines.
def cleanup( lines ):
	clean = []
	comment = False
	for line in lines:
		( line, comment ) = clean_line( line, comment )
		if line == "": continue
		if line[0] == '#': continue
		clean.append( line )
	return clean

def clean_line( line, comment ):
        line = line.strip()
        if comment:
                if "*/" in line:
                        line = line.split( "*/", 1 )[1]
                        ( line, comment ) = clean_line( line, False )
                else:
                        line = ""
        elif "//" in line:
                line = line.split( "//" )[0]
                ( line, comment ) = clean_line( line, False )
        elif "/*" in line:
                if "*/" in line:
                        line = line.split( "/*" )[0] + line.split( "*/", 1 )[1]
                        ( line, comment ) = clean_line( line, False )
                else:
                        line = line.split( "/*" )[0]
                        comment = True
        return ( line, comment )
                        

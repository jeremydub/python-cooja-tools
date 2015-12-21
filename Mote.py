

class Mote:
	def __init__(self, id, x, y, mote_type):
		self.id=id
		
		self.x=x
		self.y=y
		self.z=0

		self.nbr_count=0

		self.mote_type=mote_type

	def __str__(self):
		return '[#'+str(self.id)+']('+str(self.x)+', '+str(self.y)+')'

	def __repr__(self):
		return self.__str__()

	def __lt__(self, other):
		return self.nbr_count < other.nbr_count

	def __eq__(self, other):
		if type(self)==type(other):
			return self.x==other.x and self.y==other.y and self.z==other.z and self.id==other.id
		else:
			return False

class MoteType:
	def __init__(self, identifier, java_class, firmware, interfaces=[], description=None):
		self.identifier=identifier
		
		self.java_class=java_class
		self.firmware=firmware

		common_interfaces=['org.contikios.cooja.interfaces.Position',\
			'org.contikios.cooja.interfaces.RimeAddress',\
			'org.contikios.cooja.interfaces.IPAddress',\
			'org.contikios.cooja.interfaces.Mote2MoteRelations',\
			'org.contikios.cooja.interfaces.MoteAttributes']

		self.interfaces=common_interfaces+interfaces

		if description == None:
			self.description="Mote #"+identifier
		else:
			self.description=description

	def __str__(self):
		return '['+self.identifier+': '+self.firmware+''

	def __repr__(self):
		return self.__str__()

	def to_xml(self, xb):
		xb.write('<motetype>')
		xb.indent()
		xb.write(self.java_class)
		xb.write('<identifier>'+self.identifier+'</identifier>')
		xb.write('<description>'+self.description+'</description>')
		xb.write('<firmware EXPORT="copy">[CONFIG_DIR]/'+self.firmware+'</firmware>')
		for interface in self.interfaces:
			xb.write('<moteinterface>'+interface+'</moteinterface>')
		xb.unindent()
		xb.write('</motetype>')

class SkyMoteType(MoteType):
	def __init__(self, identifier, firmware, description=None):
		interfaces=['org.contikios.cooja.mspmote.interfaces.MspClock',
		'org.contikios.cooja.mspmote.interfaces.MspMoteID',
		'org.contikios.cooja.mspmote.interfaces.SkyButton',
		'org.contikios.cooja.mspmote.interfaces.SkyFlash',
		'org.contikios.cooja.mspmote.interfaces.SkyCoffeeFilesystem',
		'org.contikios.cooja.mspmote.interfaces.Msp802154Radio',
		'org.contikios.cooja.mspmote.interfaces.MspSerial',
		'org.contikios.cooja.mspmote.interfaces.SkyLED',
		'org.contikios.cooja.mspmote.interfaces.MspDebugOutput',
		'org.contikios.cooja.mspmote.interfaces.SkyTemperature']
		MoteType.__init__(self, identifier, 'org.contikios.cooja.mspmote.SkyMoteType', firmware, interfaces, description)

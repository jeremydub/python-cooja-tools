import random
import shelve
import datetime
import os
import os.path
from Log import Log

CONTIKI_PATH = "/home/user/contiki"

class CoojaSimulation:
	def __init__(self, topology, seed=None, success_ratio_tx=1.0, success_ratio_rx=1.0, title="Simulation",\
				 timeout=60,debug_info={}):
		
		if seed == None:
			self.seed=random.randint(0,1000000)
		else:
			self.seed=seed

		self.topology=topology

		self.success_ratio_rx=success_ratio_rx
		self.success_ratio_tx=success_ratio_tx

		self.title=title
		self.timeout=timeout

		now=datetime.datetime.today()
		self.id=str(now.year)+""+str(now.month).zfill(2)+""+str(now.day).zfill(2)+"_"+str(now.hour).zfill(2)\
				+""+str(now.minute).zfill(2)+""+str(now.second).zfill(2)

		mote_types=[]

		for mote in topology:
			if mote.mote_type not in mote_types:
				mote_types.append(mote.mote_type)

		self.mote_types=mote_types

		# User-defined dictionary used for debugging or for later analysis
		self.debug_info=debug_info

		self.return_value=-1

	def run(self, destination_file="COOJA.log"):
		self.export_as_csc(str(self.id)+".csc")
		try:
			self.log_file=destination_file

			absolute_path=os.path.abspath(str(self.id)+".csc")

			command="cd "+CONTIKI_PATH+"/tools/cooja/dist && java -mx512m -jar cooja.jar -nogui="+absolute_path
			code=os.system(command)
			self.return_value=code

			if self.has_suceed():
				os.rename(CONTIKI_PATH+"/tools/cooja/dist/COOJA.testlog",destination_file)
		finally:
			os.remove(str(self.id)+".csc")
			return code

	def has_suceed(self):
		return self.return_value==256

	def get_log(self):
		if self.has_suceed:
			return Log(self.log_file)
		else:
			return None

	def export_as_csc(self, filename):
		xb = XmlBuilder()

		xb.write("<simconf>")
		xb.indent()
		xb.write('<project EXPORT="discard">[APPS_DIR]/mrm</project>')
		xb.write('<project EXPORT="discard">[APPS_DIR]/mspsim</project>')
		xb.write('<project EXPORT="discard">[APPS_DIR]/avrora</project>')
		xb.write('<project EXPORT="discard">[APPS_DIR]/serial_socket</project>')
		
		xb.write("<simulation>")
		xb.indent()

		# General settings
		xb.write('<title>'+self.title+'</title>')
		xb.write('<randomseed>'+str(self.seed)+'</randomseed>')
		xb.write('<motedelay_us>'+str(1000000)+'</motedelay_us>')

		# Radio settings
		xb.write('<radiomedium>')
		xb.indent()
		xb.write('se.sics.cooja.radiomediums.UDGM')
		xb.write('<transmitting_range>'+str(self.topology.transmitting_range)+'</transmitting_range>')
		xb.write('<interference_range>'+str(self.topology.interference_range)+'</interference_range>')
		xb.write('<success_ratio_tx>'+str(self.success_ratio_tx)+'</success_ratio_tx>')
		xb.write('<success_ratio_rx>'+str(self.success_ratio_rx)+'</success_ratio_rx>')
		xb.unindent()
		xb.write('</radiomedium>')

		xb.write('<events>')
		xb.indent()
		xb.write('<logoutput>40000</logoutput>')
		xb.unindent()
		xb.write('</events>')

		# Mote Types
		for mote_type in self.mote_types:
			mote_type.to_xml(xb)

		# Motes
		for mote in self.topology:
			xb.write('<mote>')
			xb.indent()
			xb.write('<breakpoints />')
			xb.write('<interface_config>')
			xb.indent()
			xb.write('se.sics.cooja.interfaces.Position')
			xb.write('<x>'+str(mote.x)+'</x>')
			xb.write('<y>'+str(mote.y)+'</y>')
			xb.write('<z>'+str(mote.z)+'</z>')
			xb.unindent()
			xb.write('</interface_config>')
			xb.write('<interface_config>')
			xb.indent()
			xb.write('se.sics.cooja.mspmote.interfaces.MspMoteID')
			xb.write('<id>'+str(mote.id)+'</id>')
			xb.unindent()
			xb.write('</interface_config>')
			xb.write('<motetype_identifier>'+mote.mote_type.identifier+'</motetype_identifier>')
			xb.unindent()
			xb.write('</mote>')

		xb.unindent()
		xb.write("</simulation>")

		xb.write("<plugin>")
		xb.indent()
		xb.write("se.sics.cooja.plugins.ScriptRunner")
		xb.write("<plugin_config>")
		xb.indent()
		xb.write("<script>&#xD;")
		xb.indent()
		xb.write("TIMEOUT("+str(1000*self.timeout)+");&#xD;")
		xb.write("while (true) {&#xD;")
		xb.write("log.log(time + \":\" + id + \":\" + msg + \"\\n\");&#xD;")
		xb.write("YIELD();&#xD;")
		xb.write("}</script>")
		xb.unindent()
		xb.write("<active>true</active>")
		xb.unindent()
		xb.write("</plugin_config>")
		xb.write("<width>600</width>")
		xb.write("<z>0</z>")
		xb.write("<height>700</height>")
		xb.write("<location_x>1120</location_x>")
		xb.write("<location_y>180</location_y>")
		xb.unindent()
		xb.write("</plugin>")

		xb.unindent()
		xb.write("</simconf>")
		xb.write("")

		xb.save(filename)

class SimulationsDatabase:
	def __init__(self, filename="simulations.db"):

		self.filename=filename

		db = shelve.open(self.filename)
		if 'simulations' not in db:
			db['simulations'] = []

		self.simulations=db['simulations']
		db.close()

	def add_simulation(self, sim):
		self.simulations.append(sim)

	def merge_db(self, db):
		merged_sim = self.simulations + db.simulations
		self.simulations=merged_sim

	def get_simulation_with_id(self, sim_id):
		return self.simulations[sim_id]

	def get_simulations(self):
		return self.simulations

	def commit_changes(self):
		db = shelve.open(self.filename)
		db['simulations']=self.simulations
		db.close()

	def select(self,id=None, n=None, title=None,topology=None,debug_info=None,success_ratio_rx=None,\
				success_ratio_tx=None,timeout=None,transmitting_range=None):
		
		if topology != None:
			n=None

		result=[]

		def dictionary_is_included(dic1,dic2):
			for key in dic1:
				if not(dic2.has_key(key)) or (dic2.has_key(key) and dic2[key]!=dic1[key]):
					return False
			return True

		for s in self.simulations:
			if (n == None or (n != None and n==len(s.topology)))\
				and (id == None or (nid != None and id==s.id))\
				and (title == None or (title != None and s.title.find(title)!=-1))\
				and (success_ratio_rx == None or (success_ratio_rx != None and success_ratio_rx==s.success_ratio_rx))\
				and (success_ratio_tx == None or (success_ratio_tx != None and success_ratio_tx==s.success_ratio_tx))\
				and (timeout == None or (timeout != None and timeout==s.timeout))\
				and (transmitting_range == None or (transmitting_range != None and transmitting_range==s.transmitting_range))\
				and (debug_info == None or (debug_info != None and dictionary_is_included(debug_info, s.debug_info)))\
				and (topology == None or (topology != None and topology==s.topology)) :
				result.append(s)
		return result

	def __len__(self):
		return len(self.simulations)



class XmlBuilder:
	indent_count=0
	indent_symbol="  "

	def __init__(self):
		self.content=[]

	def indent(self):
		self.indent_count += 1

	def unindent(self):
		self.indent_count -= 1

	def write(self, line):
		self.content.append((self.indent_symbol*self.indent_count)+line+'\n')

	def save(self, filename):
		f=open(filename,"w")
		for line in self.content:
			f.write(line)
		f.close()

	def __str__(self):
		return self.content
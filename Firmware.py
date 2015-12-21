import os
import os.path


class FirmwareCompiler:
	def __init__(self, source_folder, contiki_app, objective_function="rpl_mrhof",clean=True):
		
		if not(os.path.exists(source_folder)):
			raise IOError("Application Folder does not exist.")

		self.source_folder=source_folder
		self.contiki_app=contiki_app
		self.of=objective_function
		self.clean=clean

	def compile(self,destination_file=None, override=False):
		out=self.contiki_app
		if destination_file != None:
			out=destination_file

		if not(os.path.exists(out)) or override==True:
			os.system("cd "+self.source_folder+" && rm *.sky")
			os.rename(self.source_folder+"/project-conf.h",self.source_folder+"/project-conf.h.back")
			f = open(self.source_folder+"/project-conf.h.back",'r')
			
			content = []

			for line in f:
				line=line.strip()
				if line.startswith("#define RPL_CONF_OF"):
					content.append("#define RPL_CONF_OF "+self.of)
				else:
					content.append(line.strip())
			f.close()
			f2 = open(self.source_folder+'/project-conf.h','w')

			for line in content:
				f2.write(line+'\n')
			f2.close()

			command="cd "+self.source_folder+""
			if self.clean:
				command+=" && make clean"
			command+=" && make "+self.contiki_app+" -j"
			os.system(command)
			os.remove(self.source_folder+"/project-conf.h")
			os.rename(self.source_folder+"/project-conf.h.back",self.source_folder+"/project-conf.h")
			os.rename(self.source_folder+"/"+self.contiki_app,out)
		
		else:
			print "firmware already exists !"

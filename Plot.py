import math
import matplotlib.pyplot as plt
import os.path

class DataGraph:

	@staticmethod
	def cdf(simulations, packet_attribute_selector=lambda packet:packet.delay,\
			simulation_var_selector=lambda simulation:simulation.success_ratio_rx,\
			simulation_var_label="Rx", separate_subplot=False, label_x="Delay"):
		plots=[]
		simulations_by_of={}

		for s in simulations:
			of=s.debug_info['of']
			simulation_variable=simulation_var_selector(s)

			if not(simulations_by_of.has_key(of)):
				simulations_by_of[of]={}
			simulations_by_of[of][simulation_variable]=s

		# If the given simulations use the same OF,
		# The plot does not need to be grouped by OFs
		if len(simulations_by_of) == 1:
			simulations_grouped_by_var=simulations_by_of[of]

			# If the user want 1 plot for each value of the variable (i.e, RX)
			if separate_subplot:
				for var_key in simulations_grouped_by_var:
					simulation=simulations_grouped_by_var[var_key]

					# Identifies/describes the plot by a string ID (used for filename) 
					identifier=("cdf__"+label_x+"__"+simulation_var_label+"_"+str(var_key).replace('.','')+"__"+of).lower()
					p=Plot("CDF ("+of+")",label_x=label_x, label_y="Packets (%)", identifier=identifier)
					(data_x,data_y)=DataGraph._cdf(simulation, packet_attribute_selector)
					p.add_subplot(data_x, data_y,simulation_var_label+"="+str(var_key)+"%")
					plots.append(p)

			# Otherwise, 1 plot with subplots for each value of the variable (i.e, RX)
			else:
				# Identifies/describes the plot by a string ID (used for filename) 
				identifier=("cdf__"+label_x+"__"+simulation_var_label+"__"+of).lower()
				p=Plot("CDF ("+of+")",label_x=label_x, label_y="Packets (%)", identifier=identifier)

				keys=simulations_grouped_by_var.keys()

				# Just for output purpose, allowing to display legend items in the right order
				keys.sort()

				for var_key in keys:
					simulation=simulations_grouped_by_var[var_key]
					(data_x,data_y)=DataGraph._cdf(simulation, packet_attribute_selector)
					p.add_subplot(data_x, data_y,simulation_var_label+"="+str(var_key)+"%")
				plots.append(p)
		else:
			simulations_grouped_by_var={}
			for s in simulations:
				of=s.debug_info['of']
				simulation_variable=simulation_var_selector(s)

				if not(simulations_grouped_by_var.has_key(simulation_variable)):
					simulations_grouped_by_var[simulation_variable]={}
				simulations_grouped_by_var[simulation_variable][of]=s

			# For each value of the simulation var, there is 1 simulation for each OF
			for var_key in simulations_grouped_by_var:
				simulations_by_of=simulations_grouped_by_var[var_key]

				# Identifies/describes the plot by a string ID (used for filename) 
				identifier=("cdf__"+label_x+"__"+simulation_var_label+"_"+str(var_key).replace('.','')).lower()
				p=Plot("CDF ("+simulation_var_label+"="+str(var_key)+")",label_x=label_x, label_y="Packets (%)", identifier=identifier)
				for of_key in simulations_by_of:
					simulation=simulations_by_of[of_key]
					(data_x,data_y)=DataGraph._cdf(simulation, packet_attribute_selector)
					p.add_subplot(data_x, data_y,""+of_key)
				plots.append(p)

		return plots

	@staticmethod
	def _cdf(simulation, x_axis_selector=lambda x:x.delay):
		log=simulation.get_log()
		if log == None:
			return None

		packets=log.received_packets
		sorted_packets=sorted(packets.values(), key=x_axis_selector)
		
		data_x=[]
		data_y=[]

		old_x=x_axis_selector(sorted_packets[0])
		counter=0
		n_packets=float(len(packets))
		for packet in sorted_packets:
			x=x_axis_selector(packet)
			if x != old_x:
				data_x.append(old_x)
				data_y.append(counter/n_packets)
			old_x=x
			counter += 1

		return data_x,data_y

	@staticmethod
	def two_dimensional(simulations, x_simulation_attribute_selector, y_simulation_attribute_selector, label_x, label_y):
		plots=[]
		simulations_by_of={}

		for s in simulations:
			of=s.debug_info['of']

			if not(simulations_by_of.has_key(of)):
				simulations_by_of[of]=[]
			simulations_by_of[of].append(s)

		# Identifies/describes the plot by a string ID (used for filename) 
		identifier=(label_x+"__"+label_y).lower()
		p=Plot("",label_x=label_x, label_y=label_y, identifier=identifier)
		for of_key in simulations_by_of:
			simulations=simulations_by_of[of_key]

			data_x, data_y = [], []

			simulations.sort(key=x_simulation_attribute_selector)

			old_x=None
			y = 0
			count=0

			for s in simulations:
				x=x_simulation_attribute_selector(s)
				if x != old_x and old_x != None:
					data_x.append(old_x)
					data_y.append(float(y)/count)
					y=0
					count=0

				old_x=x
				y += y_simulation_attribute_selector(s)
				count += 1

			data_x.append(old_x)
			data_y.append(float(y)/count)

			p.add_subplot(data_x, data_y,""+of_key)
			plots.append(p)

		return plots

	@staticmethod
	def test(simulations, x_packet_attribute_selector, y_packet_attribute_selector, label_x, label_y):
		plots=[]
		simulations_by_of={}

		for s in simulations:
			of=s.debug_info['of']

			if not(simulations_by_of.has_key(of)):
				simulations_by_of[of]=[]
			simulations_by_of[of].append(s)

		# Identifies/describes the plot by a string ID (used for filename) 
		identifier=(label_x+"__"+label_y).lower()
		p=Plot("",label_x=label_x, label_y=label_y, identifier=identifier)
		for of_key in simulations_by_of:
			simulation=simulations_by_of[of_key][0]
			log=simulation.get_log()

			data_x = map(x_packet_attribute_selector, log.received_packets.values())

			def remove_duplicate(seq):
				seen = set()
				seen_add = seen.add
				return [ x for x in seq if not (x in seen or seen_add(x))]

			data_x = remove_duplicate(data_x)
			data_x.sort()

			data_y = []

			for x in data_x:
				packets = filter(lambda packet: x_packet_attribute_selector(packet) == x, log.received_packets.values())
				y = float(sum(map(y_packet_attribute_selector,packets)))/len(packets)
				data_y.append(y)

			p.add_subplot(data_x, data_y,""+of_key)
			plots.append(p)

		return plots


class Plot:
	def __init__(self, title="Graph", grid=True, label_x="X", label_y="Y", identifier=None):
		self.subplots=[]
		self.title=title
		self.grid=grid
		self.label_x=label_x
		self.label_y=label_y
		self.identifier=identifier

	def add_subplot(self, data_x, data_y, label):
		subplot=(data_x, data_y, label)
		self.subplots.append(subplot)


class GraphPlotter:
	base_path="plots"
	@staticmethod
	def plot(plot, folder="."):
		if type(plot) == list:
			for p in plot:
				GraphPlotter.plot(p,folder)
		else:
			colors=['r','g','b','y']

			fig = plt.figure()
			ax = fig.add_subplot(111)
			ax.set_title(plot.title)
			i=0

			#ax.set_xlim(0, 6)

			ax.set_xlabel(plot.label_x)
			ax.set_ylabel(plot.label_y)

			for subplot in plot.subplots:
				color=colors[i%len(colors)]
				data_x,data_y,label=subplot
				ax.plot(data_x, data_y, '-'+color, label=label)
				i+=1

			leg = plt.legend(fancybox=False, loc='lower right')
			leg.get_frame().set_alpha(0.5)		

			ax.grid(plot.grid)
			
			if not(os.path.exists(GraphPlotter.base_path)):
				os.mkdir(GraphPlotter.base_path)

			if not(os.path.exists(GraphPlotter.base_path+"/"+folder)):
				os.mkdir(GraphPlotter.base_path+"/"+folder)

			fig.savefig(GraphPlotter.base_path+"/"+folder+"/"+plot.identifier+".png")
			plt.close()

'''
colors = ["yellow", "blue", "green", "red"]
symbols = ["*b","+b","ob","xb"]
symbols_ligne = ["b-","b-","b-","b-"]

def generate_histogram(machine):
	"""genere l'histogramme global des donnees pour une machine"""
	points = probleme.get_machine_points(machine)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	
	ax.set_xlabel("Vitesse(MHz)")
	ax.set_ylabel(r"$Probabilit\'{e}$")
	
	nb_intervalle = math.sqrt(len(points[1]))
	
	ax.hist(points[1], nb_intervalle, normed=1, 
			facecolor=colors[machine-1], alpha=0.75);
	ax.set_title("Machine "+str(machine))
	
	ax.grid(True)
	
	fig.savefig("images/histogram"+str(machine)+".png")
'''

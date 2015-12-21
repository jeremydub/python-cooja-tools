import os.path
import math
import re

class Log:
	def __init__(self, log_file):
		if os.path.exists(log_file):
			self.log_file=log_file
			self.debug=False
			self.parse_file(log_file)
		else:
			raise IOError("Log file does not exists !")

	def update_nodes_packets(self, packet):
		source_id=packet.source
		destination_id=packet.destination

		packets_by_node = self.packets_by_node

		if source_id != None and not(packets_by_node.has_key(source_id)):
			packets_by_node[source_id] = {"received":[], "sent":[]}

		if destination_id != None and not(packets_by_node.has_key(destination_id)):
			packets_by_node[destination_id] = {"received":[], "sent":[]}

		# If it is the first time we handle that packet, otherwise the packet would be
		# added 2 times in the source's sent packets list.
		if not(packet.has_been_received()):
			packets_by_node[source_id]["sent"].append(packet)
		else:
			packets_by_node[destination_id]["received"].append(packet)

	def parse_file(self, file):
		pending = {}
		self.received_packets = {}

		self.packets_by_node = {}

		for line in open(file, 'r').readlines():
			parts = line.split(":")
			if len(parts) > 2:
				time=int(parts[0])
				node_id=parts[1]

				print line

				if parts[2] == 'app':
					message = parts[3].strip()
					packet_id=Packet.extract_packet_id(node_id, message)

					if pending.has_key(packet_id):
						packet=pending[packet_id]
					else:
						packet=Packet(packet_id)
					"""
					print pending
					print "current pid : ", packet_id
					print line
					print "has key : ", pending.has_key(packet_id)
					print ""
					"""
					if not(self.received_packets.has_key(packet_id)):
						packet.populate(time, node_id, message)

						if packet.has_been_received():
							self.received_packets[packet_id]=packet
							pending.pop(packet_id)
						else:
							pending[packet_id]=packet

						self.update_nodes_packets(packet)
					else:
						if self.debug:
							print "Duplicate detected : packet #",packet_id

		self.lost_packets=pending

		#self.compute_nodes_pdr()

	def compute_nodes_pdr(self):
		packets_by_node=self.packets_by_node
		nodes_pdr={}
		for node_id in packets_by_node.keys():
			received=0
			for packet in packets_by_node[node_id]['sent']:
				if self.received_packets.has_key(packet.packet_id) : received+=1
			if node_id != '1':
				nodes_pdr[node_id]= 1.0*received/len(packets_by_node[node_id]["sent"])
		return nodes_pdr

	def get_mean_pdr(self):
		nodes_pdr=self.compute_nodes_pdr().values()
		return float(sum(nodes_pdr))/len(nodes_pdr)

	def get_mean_hop_count(self):
		f=lambda packet : packet.hop_count

		hop_counts = map(f, self.received_packets.values())
		return float(sum(hop_counts))/len(hop_counts)

	def get_mean_delay(self):
		f=lambda packet : packet.delay

		delays = map(f, self.received_packets.values())
		return float(sum(delays))/len(delays)

	def __str__(self):
		string=""
		string+="Log file :"+self.log_file+"\n"
		string+=" - mean PDR :"+str(self.get_mean_pdr())+"\n"
		string+=" - mean Hop Count :"+str(self.get_mean_hop_count())+"\n"
		string+=" - mean Delay :"+str(self.get_mean_delay())

		return string

class Packet:
	def __init__(self, packet_id):
		self.packet_id=packet_id
		self.sent_time=None
		self.delay=None
		self.hop_count=None
		self.of_metric=None
		self.source=None
		self.destination=None

	def populate(self, time, node_id, message):
		elements=message.split(" ")

		if elements[0]=='send':
			self.source=node_id
			self.sent_time=time
			self.rtmetric=elements[2]
			self.nbr_count=elements[3]
		elif elements[0]=='received':
			self.destination=node_id
			self.delay=(time-self.sent_time)/1000.
			self.hop_count=int(elements[3])
			#self.rank=int(elements[15])
			#self.nbr_count=int(elements[16])
			#self.parent_etx=int(elements[14])
		if(time == None):
			print "Error"
			exit()
	def has_been_received(self):
		return self.delay != None

	def __str__(self):
		return '[#'+str(self.packet_id)+']'

	def __repr__(self):
		return self.__str__()

	@staticmethod
	def extract_packet_id(node_id, message):
		elements=message.split(" ")
		if elements[0]=='send':
			return node_id+'_'+elements[1]
		elif elements[0]=='received':
			return elements[2]+'_'+elements[1]

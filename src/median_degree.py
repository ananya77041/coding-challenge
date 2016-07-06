import networkx as nx
import sys
import numpy as np
import json
from datetime import datetime

def convert_to_dt(dt_string):
	return datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%SZ')

def calc_median(G):
	return np.median(nx.degree(G).values())

class MedianGraph(object):
	def __init__(self):
		self.G = nx.Graph()
		self.newest = None
		self.degrees = []

	def _within_window(self, created_time):
		if not self.newest:
			self.newest = convert_to_dt(created_time)
			return True
		if (self.newest - convert_to_dt(created_time)).total_seconds() < 60 or convert_to_dt(created_time) > self.newest:
			return True
		return False

	def _remove_old_edges(self):
		created_times = nx.get_edge_attributes(self.G, "created_time")
		for edge, created_time in created_times.iteritems():
			if abs((self.newest - convert_to_dt(created_time)).seconds) > 60:
				self.G.remove_edge(*edge)

	def _add_valid_nodes(self, record):
		if self._within_window(record['created_time']):
			if record['target']:
				self.G.add_edge(record['actor'], record['target'], created_time = record['created_time'])
			self.newest = convert_to_dt(record['created_time'])
			self._remove_old_edges()

	def build_graph(self, filename):
		with open(filename) as f:
			for line in f:
				record = json.loads(line)
				self._add_valid_nodes(record)
				median = calc_median(self.G)

				print("Time: %s, %d Edges, Median: %f" % (self.newest, self.G.size(), median))
				print(np.mean(nx.degree(self.G).values()))
				

if __name__ == "__main__":
	graph = MedianGraph()
	graph.build_graph(sys.argv[1])




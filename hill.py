import sys
import random
import numpy as np
'''
Author: Lucas Batista Fialho - 2018
Hill Climber Algorithm to TSP
'''
class Graph:
	graph: dict
	adj: list
	vertices: list
	nvertices: int
	def __init__(self, vertices = []):
		self.graph = {}
		self.vertices = vertices
		self.nvertices = 0
	
	def euclidianDist2D(self, p1, p2):
		return ((p2[0]-p1[0])**2.+(p2[1]-p1[1])**2.)**0.5
		
	def euclidianDist3D(self, p1, p2):
		return ((p2[0]-p1[0])**2.+(p2[1]-p1[1])**2.+(p2[2]-p1[2])**2.)**0.5
	
	def read_tsp_format(self,header, body):
		tam = int(header['DIMENSION'])
		coords = {}
		self.nvertices = tam
		self.adj = [[0.0 for j in range(self.nvertices)] for i in range(self.nvertices)]
		if header['EDGE_WEIGHT_TYPE'] in ['EUC_2D','EUC_3D']:
			for i in range(tam):
				l = list(filter(lambda x: x.strip() != '',body[i].strip().split(' ')))
				
				coords[i] = (float(l[1]),float(l[2])) if header['EDGE_WEIGHT_TYPE'] == 'EUC_2D' else (float(l[1]),float(l[2]),float(l[3]))

			for i in range(tam):
				for j in range(i,tam):
					if i == j: continue
					self.adj[i][j] = self.adj[j][i] = self.euclidianDist2D(coords[i],coords[j]) if header['EDGE_WEIGHT_TYPE'] == 'EUC_2D' else self.euclidianDist3D(coords[i],coords[j])
			print(coords)
		elif header['EDGE_WEIGHT_TYPE'] == 'EXPLICIT':
			if header['EDGE_WEIGHT_FORMAT'] == 'FULL_MATRIX':
				for i in range(self.nvertices):
					l = list(filter(lambda x: x.strip() != '',body[i].strip().split(' ')))
					for j in range(self.nvertices):
						self.adj[i][j] = float(l[j])
			elif header['EDGE_WEIGHT_FORMAT'] == 'UPPER_ROW':
				for i in range(0,self.nvertices-1):
					l = list(filter(lambda x: x.strip() != '',body[i].strip().split(' ')))
					for j in range(i,self.nvertices-1):
						self.adj[i][j+1] = self.adj[j+1][i] = float(l[j-i-1])
			elif header['EDGE_WEIGHT_FORMAT'] == 'LOWER_DIAG_ROW':
				body = list(filter(lambda x: x.strip() != '',' '.join(body).split(' ')[::-1]))
				print(body)
				for i in range(self.nvertices):
					l = []
					for k in range(i+1):
						l.append(body.pop())
					for j in range(i+1):
						self.adj[i][j] = self.adj[j][i] = float(l[j])
						
				
			
		return coords
				
		
	def tsp_parser(self,filename):
		header = {}
		line = None
		body = ''
		edge_type = ''
		nvertices = 0
		with open(filename, "r") as fp:
			while True:
				line = fp.readline().strip()
				while line == '':
					line = fp.readline().strip()
				l = list(map(lambda x: x.upper().strip(),line.split(':')))
				
				if len(l) != 2:
					break
				else:
					header[l[0]] = l[1]
			if header['TYPE'] != 'TSP':
				return
			nvertices = int(header['DIMENSION'])
			edge_type = header['EDGE_WEIGHT_TYPE']
			body = list(filter(lambda x: x != '' and x != 'EOF',map(lambda x: x.strip(),fp.readlines())))
		return self.read_tsp_format(header, body)
		
					
			
		
	def load(self, filename):
		with open(filename, "r") as fp:
			self.nvertices = int(fp.readline().strip())
			self.adj = [[0.0 for j in range(self.nvertices)] for i in range(self.nvertices)]
			for i in range(self.nvertices):
				line = list(map(lambda x: float(x),filter(lambda x: x != '',fp.readline().strip().split(" "))))
				for j in range(self.nvertices):
					self.adj[i][j] = line[j]
			
			
	def adjacencia(self,v):
		return list(map(lambda i: [i[0], i[1]],filter(lambda i: i[1] != 0,enumerate(self.adj[v]))))
	
	def avaliacao(self,sol):
		ini = sol[0]
		curr = ini
		soma = 0.0
		for i in range(1, len(sol)):
			s = sol[i]
			soma += self.adj[curr][s]
			curr = s
		soma += self.adj[curr][ini]
		return soma
		
	#gulosa - o melhor primeiro	
	def construct_solution(self, trivial = False, oddFirst = False):
		sol = [0]
		curr = 0
		if trivial:
			return [i for i in range(self.nvertices)]
		if oddFirst:
			odd = [i for i in range(2,self.nvertices,2)]
			even = [i for i in range(1,self.nvertices,2)]
			sol.extend(odd)
			sol.extend(even)
			return sol
		while len(sol) < self.nvertices:
			adj = self.adjacencia(curr)
			adjOrd = filter(lambda x: x[0] not in sol,sorted(adj, key = lambda y: y[1]))
			first = next(adjOrd)[0]
			sol.append(first)
		return sol
		
	def baguncar(self, sol, av):
		best = sol, av
		melhorou = False
		while not(melhorou):
			random.seed()
			smp = random.sample(range(1,len(sol)),4)
			nsol = best[0]
			if random.uniform(0,1) > 0.5:
				for s in range(0,4,2):
					nsol[smp[s]], nsol[smp[s+1]] = nsol[smp[s+1]], nsol[smp[s]]
			else:
				solaux = nsol[1:]
				random.shuffle(solaux)
				solaux.insert(0,0)
				nsol = solaux
			nav = self.avaliacao(nsol)
			nsol, nav =self.local_search(nsol, nav, True)
			print(nav)
			if nav < best[1]:
				best = nsol, nav
				melhorou = True
		return best
		
	def local_search(self,sol, av, bestFirst = False):
		best = sol,av
		for i,_ in enumerate(sol):
			if i == 0: continue
			for j,_ in enumerate(sol):
				if j == 0: continue
				if i != j:
					nsol = best[0]
					nsol[i],nsol[j] = nsol[j],nsol[i]
					nav = self.avaliacao(nsol)
					if nav < best[1]:
						best = nsol, nav
						if bestFirst:
							return best
		return best
		
			
def main(args):
	g = Graph()
	#g.load("tsp28.csv")
	g.tsp_parser("fri26.tsp")
	solution = g.construct_solution(True,oddFirst = True)
	avaliacao = g.avaliacao(solution)
	print(avaliacao)
	changed = True
	times = 0
	while changed:
		res = g.local_search(solution, avaliacao, bestFirst = True)
		if avaliacao == res[1]:
			changed = False
		else:
			solution, avaliacao = res[0], res[1]
		
		print(res)


	
main(sys.argv)
	
	

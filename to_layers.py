#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from time import *
from struct import *
from math import *
import re

FEED_NC = 100


class Path() :
	def __init__(self, feed=None) :
		self.items = []
		self.feed = feed
		self.feed_type = None
	def line_to(self, x, y=None) :
		self.items.append([x,y] if type(x)!=list else x)

	def from_list(self, a) :
		self.items = []
		self.feed = a["feed"]
		for p in a["data"] :
			self.items.append(p)
	
	def to_svg(self) :
		if len(self.items)>1 :
			s = """								<path class="path path-%s feed feed-%s"  d=" """%(int(self.feed), int(self.feed))
			s += "M %0.4f, %0.4f "%(tuple(self.items[0]))
			i = 0
			for p in self.items :	
				i +=1
				if i%20 == 0 :
					s+="\n										"
				s += "L %0.4f, %0.4f "%(tuple(p))
			s += """ "/> """
			return s		
		else :
			return ""
	
	def to_str(self) :
		s = """		{"type":"path", "feed":%s, "feed-type":"%s", "data":[ """%(self.feed,self.feed_type)
		i = 0	
		for p in self.items :
			i += 1
			if i%20 == 0 : 
				s += "\n			"
			s += "[%0.4f, %0.4f],"%(p[0],p[1])
		s += "]}"				
		return s

	def clean(self) :
		return
	
	def move(x,y) :
		for p in self.items : 	
			 p[0] += x
			 p[1] += y
			 
	
			
class Layer() :
	def __init__(self, z=None) :
		self.paths = []
		self.last_path = None
		self.feed = None
		self.z = z
		
	def move_to(self,x,y=None) :
		if self.last_path == None or len(self.last_path.items) > 0 :
			self.paths.append(Path())
			self.last_path = self.paths[-1]
			self.last_path.feed = self.feed
		self.last_path.line_to(x,y)	
		self.cp = [x,y]
		
	def line_to(self, x,y=None) :
		if self.last_path == None :
			self.move_to(self.cp[0],self.cp[1])
		self.last_path.line_to(x,y)	
		self.cp = [x,y]
	
	def get_feed(self) :
		return self.last_path.feed
	
	def from_list(self, a) :
		self.paths = []
		for path in a["data"] :
			p_ = Path()
			p_.from_list(path)
			self.paths.append(p_)
	
	def to_svg_g(self) :
		s = ""
		for path in self.paths :
			s += path.to_svg()
			s += "\n"
		return s

	def to_svg(self) :
		s = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
				<svg class='preview' version = "1.1" baseProfile="full" xmlns = "http://www.w3.org/2000/svg" xmlns:xlink = "http://www.w3.org/1999/xlink" xmlns:ev = "http://www.w3.org/2001/xml-events" 
					viewBox="-50 -50 100 100"
					height = "100%"  width = "100%">
					<defs>			
						<link href="web.css" type="text/css" rel="stylesheet" xmlns="http://www.w3.org/1999/xhtml"/>
					</defs>
					"""
		style = "fill:none;stroke:#7b009f;stroke-width:0.05;"
		s += "	<g class='layer layer-%s' style='%s' >\n"%(i,style)
		s += self.to_svg_g()
		s += "	</g>\n\n"
		s += "</svg>"
		return s
		
		
	def to_str(self) :
		s = """	{ "type":"layer", "z":%s, "data":[\n """%self.z
		for path in self.paths :
			s += path.to_str()
			s += ",\n\n"
		s += "	]}"
		return s 

	def clean(self) :
		res = []
		for path in self.paths :
			path.clean()
			if len(path.items) > 1 :
				res.append(path)
		self.paths = res
	
	def move(self, x,y) :
		for path in self.paths :
			path.move(x,y)
			
	def combine(self, other) :
		self.paths += other.paths		
		
class Object() :
	def __init__(self) :
		self.layers = []
		self.feed = None
		self.cp = [None,None]
		
	def get_feed(self) :
		return self.last_layer.feed
		
	def set_feed(self, feed) : 
		self.last_layer.last_path.feed = feed
		FEED = {
			"perimeter": 		60 *60,
			"perimeter-out": 	80 *60,
			"perimeter-small": 	100*60,
			"infill":		 	120*60,
			"infill-solid":	 	140*60,
			"infill-top-solid":	160*60,
			"infill-gaps":	 	180*60,
			"bridges":	 		200*60,
			"support":	 		220*60,
			"support interface":240*60,
		}
		fn = "none"
		for i in FEED :
			if FEED[i] == feed :
				fn = i
				break
		self.last_layer.last_path.feed_type = fn
		self.feed = feed
		
	def add_layer(self, z=None) :
		if len(self.layers)==0 or len(self.last_layer.paths)>0 :
			self.layers.append(Layer(z))
			self.last_layer = self.layers[-1]
			self.last_layer.feed = self.feed
		
	def move_to(self,x,y=None) :
		self.last_layer.move_to(x,y)
		self.cp = [x,y]		

	def line_to(self, x,y=None) :
		self.last_layer.cp = self.cp
		self.last_layer.line_to(x,y)
		self.cp = [x,y]

		
	def to_svg(self) :
		s = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
				<svg class='preview' version = "1.1" baseProfile="full" xmlns = "http://www.w3.org/2000/svg" xmlns:xlink = "http://www.w3.org/1999/xlink" xmlns:ev = "http://www.w3.org/2001/xml-events" 
					viewBox="-50 -50 100 100"
					height = "100%"  width = "100%">
					<defs>			
						<link href="web.css" type="text/css" rel="stylesheet" xmlns="http://www.w3.org/1999/xhtml"/>
					</defs>
					"""
		i = 0
		for l in self.layers :
			s += "	<g class='layer layer-%s'>\n"%i
			s += l.to_svg()
			s += "	</g>\n\n"
			i += 1
		s += "</svg>"
		return s
		
			
	def from_gcode(self,s) :
		for layer in s.split("(layer start)")[1:] :
			layer = layer.split("\n")
			for l in layer : # find if there's same layer already
				if l[:4]=="G1 Z" : # zmove
					z = float(re.search("Z([-0-9.]+)", l).group(1))
					if z not in [l1.z for l1 in self.layers] :
						self.add_layer(z=z)
					break
			feed = None
			for l in layer :
				if l[:4]=="G1 Z" : # zmove
					continue

				r = re.search("G1\s*(X.*)?\s*F([-0-9.]+)", l)
				if r :  # feed
					feed = float(r.group(2))	

					
				if l[:4] in ["G1 X", "G1 Y"] :
					p = re.search("X([-0-9.]+) Y([-0-9.]+)", l).groups()
					p = [float(p[0]),float(p[1])]
					if feed > 7000*60: # rappid_move
						self.move_to(p)
					else :
						#print "line"
						self.line_to(p)
						if feed != None :
							self.set_feed(feed)

	def from_slice(self,s) :
		s = s.split("\n")
		#self.cp = [0.,0.]
		for l in s:
			if l=="" :
				continue
			self.add_layer()
			a = eval(l)
			for sp in a:
				if len(sp)<2 :
					continue
				self.move_to(sp[0])	
				for p in sp[1:] :
					self.line_to(p)			
				self.set_feed(FEED_NC)				
		
				
	def from_nc(self, s) :
		def to_p(x,y) :
			scale = 0.01
			return [float(x)*scale, float(y)*scale]
		num = 0	
		s = s.split("\n")
		#self.cp = [0.,0.]
		for l in s:
			num += 1
			if num%1000 == 0 :
				print "%s of %s"%(num,len(s))
			if "G02" in l :
				c,x,y,z = l.split()
				self.add_layer(z=z)
				self.move_to(to_p(x,y))	
			if "G03" in l :	
				c,x,y = l.split()
				self.move_to(to_p(x,y))			
			if "G01" in l :	
				c,x,y = l.split()
				self.line_to(to_p(x,y))			
				self.set_feed(FEED_NC)				
			
	def from_list(self, a) :
		self.layers = []
		for l in a["data"] :
			L = Layer()
			L.from_list(l)
			self.layers.append(L)
		self.clean
			
	def to_str(self) :
		s = """{ "type":"object", "data":[\n """
		for l in self.layers :
			s += l.to_str()
			s += ",\n"
		s += "]}"
		return s
			
	def clean(self)	: 
		res = []
		for l in self.layers :
			l.clean()
			if len(l.paths) > 0 :
				res.append(l) 
		self.layers = res

	def move(self,x,y) :
		for layer in self.layers :
			layer.move(x,y)

	def combine(self, other) :
		for i in range(len(other.layers)) : 
			if i >= len(self.layers) : 
				self.layers.append(other.layer[i])
			else :
				self.layer[i].combine(other.layer[i])
			
class Scene() :
	def __init__(self) :
		self.obj = [] 
		
	def add_obj(self,f,x=None,y=None) :
		f = "layers/"+os.path.splitext(os.path.basename(f))[0]+".l"
		obj = Object()
		obj.from_list(eval(open(f).read()))
		obj.move(x,y)
		self.obj.append(obj)
		
	def combine(self) :
		res = self.objects[0]
		for obj in self.objects[1:] :
			res.combine(obj)
		return res				
		
if __name__ == "__main__":					
	l = Object() 
	
	fin = sys.argv[1]
	if "-l" in sys.argv :
		l.from_list(eval(open(fin).read()))
	elif "-n" in sys.argv :
		l.from_nc(open(fin).read())
	elif ".slice" in fin :
		l.from_slice(open(fin).read())
	else :	
		l.from_gcode(open(fin).read())
	
	l.clean()

	fout = os.path.splitext(os.path.basename(fin))[0]
	dirname = 'objects/%s'%fout
	import shutil
	try : 
		shutil.rmtree(dirname)	
	except :
		pass
		
	os.mkdir(dirname)
	os.mkdir(dirname+"/layers")
	os.mkdir(dirname+"/svg")
	i = 0
	for layer in l.layers :
		
		open(dirname+"/layers/%05d.l"%i,"w").write(layer.to_str())
		open(dirname+"/svg/%05d.svg"%i,"w").write(layer.to_svg())
		i += 1
	
	
	
	

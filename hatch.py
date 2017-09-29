import re
import math
import pyclipper
from inc.points import P
import time 
import sys 

class Path() :
	def __init__(self, items=None):
			self.items = []
			if items != None :
				self.items = items
			self.res = []
			
			
	def clone(self) :
		res = Path()
		res.items = [[p[:] for p in sp] for sp in self.items]
		return res
			
	def bounds(self) :
		b = [1e100,1e100,-1e100,-1e100]
		for sp in self.items :
			for p in sp :
				b[0] = min(b[0],p[0])
				b[1] = min(b[1],p[1])
				b[2] = max(b[2],p[0])
				b[3] = max(b[3],p[1])
		return b
	
	def clean(self) :
		self.items = [sp for sp in self.items if len(sp)>1]
		
		
	def hatches(self, l=10, st=0.1, num=0):
		self.clean()
		b0 = self.bounds()
		b = [b0[0]-l, b0[1]-l, b0[2]+l, b0[3]+l]

		h = []
		ls = l/math.sqrt(2)
		sts = st/math.sqrt(2)
		i = 0
	   
		if num%2 == 0 :
			x0 = b[0]		
			while x0<b[2]+b[3]-b[1] :
				x = x0
				y = b[1]
				while x>b[0] and y<b[3] :
					x -= sts
					y += sts
					if i%2 == 0 :
						h.append([  [x,y],[x-ls,y-ls]] )
					else :
						h.append([  [x-ls,y-ls],[x,y]] )
					i += 1 				
				x0 += l*math.sqrt(2)
		else :
			x0 = b[0] - (b[3]-b[1])
			while x0<b[2] :
				x = x0
				y = b[1]
				while y<b[3] and x<b[2] :
					x += sts
					y += sts
					if i%2 == 0 :
						h.append([  [x,y],[x+ls,y-ls]] )
					else :
						h.append([  [x+ls,y-ls],[x,y]] )
					i += 1 				
				x0 += l*math.sqrt(2)
		def check_sp(sp,b):
			return b[0]<sp[0][0]<b[2] and  b[1]<sp[0][1]<b[3] or b[0]<sp[1][0]<b[2] and  b[1]<sp[1][1]<b[3]
			
		h = [sp for sp in h if check_sp(sp,b)]

		pc = pyclipper.Pyclipper()
		pc.AddPaths(pyclipper.scale_to_clipper(self.items), pyclipper.PT_CLIP, True)
		pc.AddPaths(pyclipper.scale_to_clipper(h), pyclipper.PT_SUBJECT, False)
		solution = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
		
		h = pyclipper.scale_from_clipper(pyclipper.PolyTreeToPaths(solution)	)
		return Path(h)

	def line_to(self, x,y) :
		self.items[-1].append([x,y])

	def move_to(self,x=None,y=None) :
		self.items.append([])
		if x!=None:
			self.line_to(x,y)

	def offset(self, r) :
		r = pyclipper.scale_to_clipper(r)
		t = time.time()
		pco = pyclipper.PyclipperOffset()
		pco.AddPaths(pyclipper.scale_to_clipper(self.items), pyclipper.JT_SQUARE, pyclipper.ET_CLOSEDPOLYGON)
		res = pyclipper.scale_from_clipper(pco.Execute(r))
		return res 

	def append(self, other) :
		self.items += other.items[:]

	def contours(self, num = 0	, offset=.9) :
		res = Path() 
		for i in range(num,1,-1) :
			c = self.clone()
			c.offset(offset*i)
			res.append(c)
		res.append(self.clone())
		return res
		
	def export(self, num, contours=2) :
		print "Export (len %s = %s)"%([len(sp) for sp in self.items],sum([len(sp) for sp in path.items])) 
		t = time.time()
		res = self.hatches(num=num)
		print "Hatches",(time.time()-t)
		t = time.time()
		res.append(self.contours(contours))
		print "Contours %s Offset "%contours,(time.time()-t)
		return res

	def to_inkscape(self) :
		res = ""
		for sp in self.items:
			res +="M "
			for p in sp : 
				res += "%f,%f"%(p[0],p[1])
		return res


s = open(sys.argv[1]).read()
num = 0
path = None
start_time = time.time()


out = open(sys.argv[1]+".slice","w")

for l in s.split("\n"):
		if l!="" and l[0]=="Z" :

				if path!=None :
					p = path.export(num)
					out.write("%s\n"%p.items)
				path = Path()
				num += 1
				print "Layer %s"%num
				path.move_to()
		elif l == "C" :
			path.move_to()
		else :
			r = re.match("([-0-9.]+) ([-0-9.]+)",l)
			if r :
				x,y = float(r.group(1))*25.4,float(r.group(2))*25.4
				path.line_to(x,y)
			else :
				print l
print "Done in %s"%(time.time()-start_time)				

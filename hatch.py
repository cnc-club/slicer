import re
import math
from inc.points import P

class Path() :
	def __init__(self):
			self.items = []
			self.res = []
	def bounds(self) :
		b = [1e100,1e100,-1e100,-1e100]
		for sp in self.items :
			for p in sp :
				b[0] = min(b[0],p[0])
				b[1] = min(b[1],p[1])
				b[2] = max(b[2],p[0])
				b[3] = max(b[3],p[1])
		return b
		
	def hatches(self, l=10, st=0.1, layer=0):
		b0 = self.bounds()
		b = [b0[0]-l, b0[1]-l, b0[2]+l, b0[3]+l]

		h = []
		ls = l/math.sqrt(2)
		sts = st/math.sqrt(2)
		i = 0
	   
		if layer%2 == 0 :
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
			x0 = b[2]
			while x0>b[0]  b[2]-b[1] :
				y = y0
				x = b[0]
				while y>b[1] and x<b[2] :
					x += sts
					y -= sts


		def check_sp(sp,b):
			return b[0]<sp[0][0]<b[2] and  b[1]<sp[0][1]<b[3] or b[0]<sp[1][0]<b[2] and  b[1]<sp[1][1]<b[3]
			
		h = [sp for sp in h if check_sp(sp,b)]
		for sp in h: 
			print "M",sp[0][0],sp[0][1],sp[1][0],sp[1][1],
		print 
		print 

	def line_to(self, x,y) :
		self.items[-1].append([x,y])

	def move_to(self,x=None,y=None) :
		self.items.append([])
		if x!=None:
			self.line_to(x,y)

	def offset(self, r) :
		pass

	def contours(self, num = 3, offset=.9) :
			contours = []
			for i in range(num,1,-1) :
				print offset*i
				contours.append(self.offset(offset*i).items)
			contours.append(self.items)

	def export(self) :
		self.hatches()
		#self.contours()



s = open("test1.ssl").read()
num = 0
path = None
for l in s.split("\n"):
		if l!="" and l[0]=="Z" :
				if path!=None :
						path.export()
				path = Path()
				num += 1
				print "Layer %s"%num
				path.move_to()
		elif l == "C" :
			path.move_to()
		else :
			r = re.match("([-0-9.]+) ([-0-9.]+)",l)
			if r :
				x,y = float(r.group(1)),float(r.group(2))
				path.line_to(x,y)
			else :
				print l

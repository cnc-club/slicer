import re
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

    def hatches(self, l=10, st=0.1, ang = 45):
        b = self.bounds()
        b = [b[0]-1, b[1]-1, b[2]+1, b[3]+2]
        x,y = b[0],b[1]
        h = []
        while x<b[2] and y<b[3] :
            d = 0

            while d<b[3]-b[1]:
                h.append([
                    [x+d,   ]

                ])
                y0+=st

            h.append(
                    [
                        [x,b[1]],
                        [x+st,b[1]],
                        [b[0],y+st],
                        [b[0],y]
                    ]
                )
            x += l
            y += l



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
        self.contours()



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

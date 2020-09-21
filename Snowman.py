import struct
import math
from collections import namedtuple

V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

def color(r, g, b):
    return bytes([b, g, r])

#Funciones vistas con Dennis

def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def length(v0):
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def mul(v0, k):
  return V3(v0.x * k, v0.y * k, v0.z *k)

def cross(v1, v2):
  return V3(
    v1.y * v2.z - v1.z * v2.y,
    v1.z * v2.x - v1.x * v2.z,
    v1.x * v2.y - v1.y * v2.x,
  )

def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def sum(v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def bbox(*vertices):
  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]
  
  xs.sort()
  ys.sort()

  xMin = xs[0]
  xMax = xs[-1]
  yMin = ys[0]
  yMax = ys[-1]

  return xMin, xMax, yMin, yMax

def baryCentric(A, B, C, P):
  cx, cy, cz = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x), 
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(cz) < 1:
    return -1, -1, -1   

  u = cx/cz
  v = cy/cz
  w = 1 - (u + v)

  return w, v, u

def norm(v0):
  v0length = length(v0)

  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

class Material(object):
  def __init__(self, diffuse):
    self.diffuse = diffuse

class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, direction):
        L = sub(self.center, orig)
        tca = dot(L, direction)
        l = length(L)
        d2 = l ** 2 - tca ** 2

        if d2 > self.radius ** 2:
          return False

        thc = (self.radius ** 2 - d2) ** 1 / 2
        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
          t0 = t1

        if t0 < 0:
          return False

        return True


class RayTracer(object):

    def glInit(self, width, height):
        self.width = 0
        self.height = 0
        self.color = color(255, 255, 255)
        self.framebuffer = []
        self.filename = filename
        self.glclear
        
    def glClear(self):
        self.framebuffer = [
            [color(0, 0, 0) for x in range(self.width)]
            for y in range(self.height)
        ]
        
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height        
      
    def point(self, x, y):
        self.framebuffer[x][y] = color(255, 0, 0)

    def glColor(self, r, g, b):
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        self.color = bytes([b, g, r])

    def glViewPort(self, x, y, width, height):
        self.xVP = x
        self.yVP = y
        self.wVP = width
        self.hVP = height
        
    def glClearColor(self, r, g, b):
        self.framebuffer = [
        [color(r, b, g) for x in range(self.width)]
        for y in range(self.height)
            ]

    def glVertex(self, x, y):
        x_Ver = int(round(self.wVP/2)*(x+1))
        y_Ver = int(round(self.yVP/2)*(x+1))
        x_pnt = self.xVP + x_Ver
        y_pnt = self.yVP + y_Ver
        self.point((x_pnt),(y_pnt))

    def glLine(self, x0, x1, y0, y1):
        x0 = int(round(self.wVP/2)*(x0+1))
        x1 = int(round(self.wVP/2)*(x1+1))
        y0 = int(round(self.wVP/2)*(y0+1))
        y1 = int(round(self.wVP/2)*(y1+1))

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        
        offset = 0
        threshold = dx
        y = y0
        
        for x in range(x0, x1):
            if steep:
                self.point(y, x)
            else:
                self.point(x, y)
                
            offset += dy * 2
            
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += 2 * dx

    def glBM(self, filename):
        f = open(filename, 'bw')

        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width + self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])
        f.close()
    def glFinish(self):
      self.render()
      self.glBM('Snowman.bmp')
      
    def scene_intersect(self, origin, direction):
      for obj in self.scene:
        if obj.ray_intersect(origin, direction):
          return obj.material
      return None

    def cast_ray(self, orig, direction):
        impacted_material = self.scene_intersect(orig, direction)
        if impacted_material:
            return impacted_material.diffuse
        else:
            return color(0, 0, 0)

    def render(self):
      snm = int(math.pi/2)
      for y in range(self.height):
        for x in range(self.width):
          i = (2 * (x + 0.5)/self.width - 1) * self.width/self.height * math.tan(snm/2)
          j = (1 - 2 * (y + 0.5)/self.height) * math.tan(snm/2)

          direction = norm(V3(i, j, -1))
          self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)

#Colores       
noir = Material(diffuse=color(0, 0, 0))
blanc = Material(diffuse=color(255, 255, 255))
orange = Material(diffuse=color(255, 128, 0))

bitmap = RayTracer()
bitmap.glCreateWindow(1000,1000)
bitmap.glClear()
bitmap.scene = [
    #nariz
    Sphere(V3(0, -3, -10), 0.2, orange),

    #ojos
    Sphere(V3(0.5, -3.5, -10), 0.1, noir),
    Sphere(V3(-0.5, -3.5, -10), 0.1, noir),
    
    #sonrisa
    Sphere(V3(-0.5, -2.5, -10), 0.1, noir),
    Sphere(V3(-0.2, -2.4, -10), 0.1, noir),
    Sphere(V3(0.2, -2.4, -10), 0.1, noir),
    Sphere(V3(0.5, -2.5, -10), 0.1, noir),

    #botones
    Sphere(V3(0, 0, -10), 0.3, noir),
    Sphere(V3(0, 1.5, -10), 0.3, noir),
    Sphere(V3(0, 3, -10), 0.3, noir),

    #cuerpo
    Sphere(V3(0, 3, -10), 2.5, blanc),
    Sphere(V3(0, 0, -10), 2, blanc),
    Sphere(V3(0, -3, -10), 1.5, blanc)

]
bitmap.glFinish()

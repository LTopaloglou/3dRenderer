import tkinter
import time
import math

xrotation = math.pi/4
yrotation = math.pi/4
zrotation = 0
cubeOrOctahedron = 1

#Key handling
def key_pressed(event):
    #print(event.char)
    global yrotation, xrotation, zrotation
    if (event.char == 'a'):
        yrotation = yrotation + math.pi/32
    if (event.char == 'd'):
        yrotation = yrotation - math.pi/32
    if (event.char == 'w'):
        xrotation = xrotation + math.pi/32
    if (event.char == 's'):
        xrotation = xrotation - math.pi/32
    if (event.char == 'r'):
        zrotation = zrotation + math.pi/32
    if (event.char == 'f'):
        zrotation = zrotation - math.pi/32
    if (event.char == 'z'):
        global cubeOrOctahedron
        cubeOrOctahedron *= -1
    
    
    

#setup of the window and page
page = tkinter.Tk()
canvas = tkinter.Canvas(page, bg="black", height=600,width=600)
page.bind("<Key>", key_pressed)
page.title("3D Test")
page.resizable(width=False, height=False)
canvas.pack()

#Global vertex, index and color list
Vertices = []
Indices = []
Colors = []

class Matrix3x3:
    def __init__(self, values):
        self.values = values
    
    #these rotation matrices use radians
    def zRot(self, theta):
        self.values = [math.cos(theta), math.sin(theta), 0.0,
                       math.sin(theta) * -1.0, math.cos(theta), 0.0,
                       0.0, 0.0, 1.0]
    def xRot(self, theta):
        self.values = [1.0, 0.0, 0.0, 
                       0.0, math.cos(theta), math.sin(theta),
                       0.0, math.sin(theta) * -1.0, math.cos(theta)]
    def yRot(self, theta):
        self.values = [math.cos(theta), 0.0, math.sin(theta) * -1.0,
                       0.0, 1.0, 0.0,
                       math.sin(theta), 0.0, math.cos(theta)]
    
    def applyTo3x1Matrix(self, matrix3x1):
        result = [matrix3x1[0]*self.values[0] + matrix3x1[1]*self.values[3] + matrix3x1[2]*self.values[6], matrix3x1[0]*self.values[1] + matrix3x1[1]*self.values[4] + matrix3x1[2]*self.values[7], matrix3x1[0]*self.values[2] + matrix3x1[1]*self.values[5] + matrix3x1[2]*self.values[8]]
        return result

class Vector2D:
    def __init__(self, p1x, p1y, p1z, p2x, p2y, p2z):
        self.x = p2x - p1x
        self.y = p2y - p1y
        self.z = p2z - p1z

    def printVec(self):
        print("x: " + str(self.x) + " y: " + str(self.y) + "z: " + str(self.z))

    def dotProduct(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def crossProduct(self, other):
        result = Vector2D(0, 0, 0, self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)
        return result


class Object:
    def __init__(self, vertices, indices, colors):
        #vertices contains a set of ordered triplets (x, y, z) 
        self.vertices = vertices
        #indices contains a set of four (v1, v2 , v3, color)
        #the v's are which set of ordered pairs to use to draw the triangle, and the color is what color to fill it with
        self.indices = indices
        #colors contains a a set of colors
        self.colors = colors
        self.rotateVertices = [None] * len(self.vertices)
        self.projectVertices = [None] * len(self.vertices)
    def rotate(self, x, y, z):
        #x, y and z are in radians
        X = Matrix3x3([])
        X.xRot(x)
        Y = Matrix3x3([])
        Y.yRot(y)
        Z = Matrix3x3([])
        Z.zRot(z)
        for x in range(0, len(self.vertices), 3):
            newValues = [self.vertices[x], self.vertices[x + 1], self.vertices[x + 2]]
            newValues = X.applyTo3x1Matrix(newValues)
            newValues = Y.applyTo3x1Matrix(newValues)
            newValues = Z.applyTo3x1Matrix(newValues)
            self.rotateVertices[x] = newValues[0]
            self.rotateVertices[x + 1] = newValues[1]
            self.rotateVertices[x + 2] = newValues[2]
    def project(self, n):
        #for the sake of projection, z value must be translated into the screen n units so it's behind the viewing plane. The camera is at 0, 0 ,0 and the n value is the distance from the camera to viewing plane.
        for x in range(0, len(self.rotateVertices), 3):
            self.projectVertices[x] = self.rotateVertices[x] * n / (self.rotateVertices[x+2] + (n * 2))
            self.projectVertices[x+1] = self.rotateVertices[x+1] * n / (self.rotateVertices[x+2] + (n * 2))
            self.projectVertices[x+2] = self.rotateVertices[x+2]

    def toRender(self):
        for x in self.projectVertices:
            Vertices.append(x)
        for x in self.indices:
            Indices.append(x)
        for x in self.colors:
            Colors.append(x)

def render():
    canvas.create_rectangle(0, 0, 600, 600, fill="black")
    #for every triangle (and color)
    for x in range(0, len(Indices), 4):
        #BACKFACE CULLING
        #first generate the normal vector of the triangle.
        #use vectors x - x+1 and x - x+2
        #THIS IS THE SOURCE OF ERROR CURRENTLY
        vec1 = Vector2D(Vertices[Indices[x] * 3], Vertices[Indices[x] * 3 + 1], Vertices[Indices[x] * 3 + 2], Vertices[Indices[x + 1] * 3],  Vertices[Indices[x + 1] * 3 + 1],  Vertices[Indices[x + 1] * 3 + 2])
        vec2 = Vector2D(Vertices[Indices[x] * 3], Vertices[Indices[x] * 3 + 1], Vertices[Indices[x] * 3 + 2], Vertices[Indices[x + 2] * 3],  Vertices[Indices[x + 2] * 3 + 1],  Vertices[Indices[x + 2] * 3 + 2])
        normal = vec1.crossProduct(vec2)
        #Then find the dot product between the normal vector and the vector of the camera 
        #if the dot is negative, draw. If not, don't.
        #Since the camera is at 0,0,0 and goes in the +z diretion, the camera vector can be (0,0,1)
        vec3 = Vector2D(0, 0, 0, 0, 0, 1)
        result = normal.dotProduct(vec3)
        if (result < 0):
            canvas.create_polygon(Vertices[Indices[x] * 3] + 300, Vertices[Indices[x] * 3 + 1]+ 300,Vertices[Indices[x+1] * 3]+ 300, Vertices[Indices[x+1] * 3 + 1]+ 300,Vertices[Indices[x+2] * 3]+ 300, Vertices[Indices[x+2] * 3 + 1]+ 300, fill=Colors[Indices[x+3]])
        
    


cubeVertices = [-150, -150, 150,
       150, -150, 150,
       -150, 150, 150,
       150, 150, 150,
       -150, -150, -150,
       150, -150, -150,
       -150, 150, -150, 
       150, 150, -150]
cubeIndices = [0, 1, 3, 0,
               0, 3, 2, 0,
               4, 5, 1, 1,
               4, 1, 0, 1,
               2, 3, 7, 2, 
               2, 7, 6, 2, 
               4, 0, 2, 3,
               4, 2, 6, 3,
               1, 5, 7, 4,
               1, 7, 3, 4,
               5, 4, 6, 5,
               5, 6, 7, 5]
cubeColors = ["red",
              "blue",
              "green",
              "orange",
              "yellow",
              "purple"]

Cube = Object(cubeVertices, cubeIndices, cubeColors)

octahedronVertices = [
    -150, 0, 0,
    0, 0, -150,
    150, 0, 0,
    0, 0, 150,
    0, -150, 0,
    0, 150, 0
]
octahedronIndices = [
    4, 1, 0, 0,
    4, 2, 1, 1,
    4, 3, 2, 2,
    4, 0, 3, 3,
    0, 1, 5, 4,
    1, 2, 5, 5,
    2, 3, 5, 6,
    3, 0, 5, 7
]
octahedronColors = [
    "red",
    "blue",
    "green",
    "yellow",
    "purple", 
    "pink",
    "orange",
    "darkblue"
    
]

Octahedron = Object(octahedronVertices, octahedronIndices, octahedronColors)

def clear():
    global Vertices
    global Indices
    global Colors
    Vertices = []
    Indices = []
    Colors = []

while True:
    clear()
    
    if (cubeOrOctahedron > 0):
        Cube.rotate(xrotation, yrotation, zrotation)
        Cube.project(600)
        Cube.toRender()
    else:
        Octahedron.rotate(xrotation, yrotation, zrotation)
        Octahedron.project(600)
        Octahedron.toRender()
    #render
    render()
    page.update_idletasks()
    page.update()

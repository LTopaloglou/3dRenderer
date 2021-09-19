# 3dRenderer
A program that renders any convex 3D object and allows the user to rotate it by using the w/s, a/d and r/f keys. Created in Python using only TKinter's polygon function to draw triangles.

The entire program is in the test.py file. 

It initially renders a cube, but can toggle between the cube and an octahedron by pressing the z key.

The program rotates the object's vertices and then projects them onto the view plane. After that, each triangle in the object is processed by the renderer
1 by 1. The renderer will check if that triangle is facing towards or away from the camera and decide whether or not to draw it accordingly.
Then, that triangle is drawn using TKinger's polygon function.

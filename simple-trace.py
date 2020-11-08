import numpy as np 
from intersection import intersect
import relativity as rel 
from plane import Plane 

v = np.array([0.15,0,0])
boost = rel.lorentz(v)

#todo: plane class: 
theta,phi = 0.,0.0
z = 500 
plane1 = Plane(boost,np.array([-z*v[0],-z*v[1],z]),np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)]),np.array([30,0.0,0.0]),np.array([0,20.0,0.0]) )
plane2 = Plane(boost,np.array([-z*v[0],-z*v[1],z+100]),np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)]),np.array([30,0.0,0.0]),np.array([0,20.0,0.0]) , np.array([0,255,0]))

planeList = [plane1,plane2]
Nplanes = len(planeList)

#initialization 
Nx, Ny = 3*192,3*108
imagingX = 160
imagingY = 90
imagingPlane = 200
pixelX,pixelY = np.meshgrid(np.linspace(-imagingX,imagingX,Nx),np.linspace(-imagingY,imagingY,Ny),indexing = 'ij')
Nrays = Nx*Ny #can be more later if we want anti-aliasing
rays = np.zeros([Nx,Ny,4])
rays[:,:,0] = 1.0
rays[:,:,1] = pixelX
rays[:,:,2] = pixelY
rays[:,:,3] = imagingPlane
#forbidden loop -- if you have a nicer way to write this, let me know.
for i in range(Nx):
    for j in range(Ny):
        ray = rays[i,j,:]
        rays[i,j,1:] /= np.sqrt(np.dot(ray,ray))
#shaping the rays 
rays = np.reshape(rays,[Nx*Ny,4])
#to obtain the original configuration, use: rays = np.reshape(rays,[Nx,Ny,4])



#compute which plane is first intersected by each ray: 
rayInds = np.arange(Nrays)
intersectingPlaneIndex = -1*np.ones(Nrays,dtype=np.int32)
leastT = 1e99 * np.ones(Nrays)
for ind,pl in enumerate(planeList):
    tIntersects = intersect(pl,rays) 
    rInter =  rays*tIntersects[:,np.newaxis]
    # vel_4 * tInter[:,np.newaxis]
    intersectingRayIndices = rayInds[np.logical_and(np.logical_and(leastT > tIntersects, tIntersects>0), pl.inPlane(pl.toPrimedFrame(rInter)))]
    #np.arange(Nrays)[np.logical_and(leastT > tIntersects, tIntersects>np.zeros(Nrays))]
    intersectingPlaneIndex[intersectingRayIndices] = ind 
    leastT[intersectingRayIndices] = tIntersects[intersectingRayIndices]

#compute the location of first intersection: 
r1_4 = rays*tIntersects[:,np.newaxis] #np.multiply(np.tile(leastT,4).reshape((Nrays,4)),rays)
#now, compute the color contributed by each plane at the point of intersection:
numPlaneHits = np.array([np.sum((intersectingPlaneIndex == i)) for i in range(Nplanes)])
raysIntersectingPlanes = [ rayInds[(intersectingPlaneIndex == i)] for i in range(Nplanes)]
raysIntersectingSky = (rayInds[intersectingPlaneIndex == -1])
rayRGB = np.zeros([Nrays,3],dtype = np.int32)
for ind,pl in enumerate(planeList):
    intersectingRayInds = raysIntersectingPlanes[ind]
    rayRGB[intersectingRayInds] = pl.boostedColor(rays[intersectingRayInds],r1_4[intersectingRayInds], np.array([500,0,-500,0]),100.0)
    # rayRGB[intersectingRayIndices,:] = color[intersectingRayIndices]
# print(intersectingPlaneIndex)
rayRGB[raysIntersectingSky] = np.array([0,25,50],dtype=np.int32)
print('misses: ',np.size(raysIntersectingSky), 'of ', Nrays)



#TODO: output the ray RGBs into an image
screenRGB = np.reshape(rayRGB,[Nx,Ny,3])

import matplotlib.pyplot as plt 
plt.imshow(np.transpose(screenRGB,axes = (1,0,2)),origin = 'lower')
plt.show()


def shapeBack(arr):
    return np.reshape(arr,pixelX.shape)


r1p_4 = plane1.toPrimedFrame(r1_4)
# print(plane1.inPlane(r1p_4))

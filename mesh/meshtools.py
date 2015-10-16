### ========================================    
### Some mesh helper functions ... initialise etc  
### ========================================

import math
import numpy as np
    
def lloyd_mesh_improvment(x, y, bmask, iterations):
    """
    Applies Lloyd's algorithm of iterated voronoi construction 
    to improve the mesh point locations (assumes no current triangulation)

    (e.g. see http://en.wikipedia.org/wiki/Lloyd's_algorithm )

    We do not move boundary points, but some issues can arise near
    boundaries if the initial mesh is poorly constructed with non-boundary points
    very close to the boundary such that the centroid of the cell falls outside the boundary.

    Caveat emptor !
    """

    from scipy.spatial import Voronoi  as __Voronoi
    import numpy as np


    points = np.column_stack((x,y))

    for i in range(0,iterations):
        vor = __Voronoi(points)
        new_coords = vor.points.copy()

        for centre_point, coords in enumerate(vor.points):
            region = vor.regions[vor.point_region[centre_point]]
            if not -1 in region and bmask[centre_point]:
                polygon = vor.vertices[region]      
                new_coords[centre_point] = [polygon[:,0].sum() / len(region), polygon[:,1].sum() / len(region)]
              
        points = new_coords

    x = np.array(new_coords[:,0])
    y = np.array(new_coords[:,1])  
     
    return x,y


def square_mesh(minX, maxX, minY, maxY, spacingX, spacingY, samples, boundary_samples ):
    
    import numpy as np


    lin_samples = int(math.sqrt(samples))

    tiX = np.linspace(minX + 0.75 * spacingX, maxX - 0.75 * spacingX, lin_samples) 
    tiY = np.linspace(minY + 0.75 * spacingY, maxY - 0.75 * spacingY, lin_samples) 

    x,y = np.meshgrid(tiX, tiY)

    x = np.reshape(x,len(x)*len(x[0]))
    y = np.reshape(y,len(y)*len(y[0]))

    xscale = (x.max()-x.min()) / (2.0 * math.sqrt(samples))
    yscale = (y.max()-y.min()) / (2.0 * math.sqrt(samples))

    x += xscale * (0.5 - np.random.rand(len(x)))
    y += yscale * (0.5 - np.random.rand(len(y)))


    bmask = np.ones_like(x, dtype="Bool") # It's all true !

    # add boundary points too 

    x = np.append(x, np.linspace(minX, maxX, boundary_samples) )
    y = np.append(y, np.ones(boundary_samples)*minY )
    bmask = np.append(bmask, np.zeros(boundary_samples, dtype="Bool"))

    x = np.append(x, np.linspace(minX, maxX, boundary_samples) )
    y = np.append(y, np.ones(boundary_samples)*maxY )
    bmask = np.append(bmask, np.zeros(boundary_samples, dtype="Bool"))

    x = np.append(x, np.ones(boundary_samples)[1:-1] * minX )
    y = np.append(y, np.linspace(minY, maxY, boundary_samples)[1:-1] )
    bmask = np.append(bmask, np.zeros(boundary_samples-2, dtype="Bool"))

    x = np.append(x, np.ones(boundary_samples)[1:-1] * maxX )
    y = np.append(y, np.linspace(minY, maxY, boundary_samples)[1:-1] )
    bmask = np.append(bmask, np.zeros(boundary_samples-2, dtype="Bool"))

# mask: need to keep the boundary conditions from being changed but equally have them available

    inverse_bmask = np.invert(bmask)

    return x, y, bmask, inverse_bmask


def elliptical_mesh(minX, maxX, minY, maxY, spacingX, spacingY, samples, boundary_samples ): 

    import numpy as np


    originX = 0.5 * (maxX + minX)
    originY = 0.5 * (maxY + minY)
    radiusX = 0.5 * (maxX - minX)
    aspect = 0.5 * (maxY - minY) / radiusX
    
    print "Origin = ", originX, originY, "Radius = ", radiusX, "Aspect = ", aspect
    
    lin_samples = int(math.sqrt(samples))

    tiX = np.linspace(minX + 0.75 * spacingX, maxX - 0.75 * spacingX, lin_samples) 
    tiY = np.linspace(minY + 0.75 * spacingY, maxY - 0.75 * spacingY, lin_samples) 

    x,y = np.meshgrid(tiX, tiY)

    x = np.reshape(x,len(x)*len(x[0]))
    y = np.reshape(y,len(y)*len(y[0]))

    xscale = (x.max()-x.min()) / (2.0 * math.sqrt(samples))
    yscale = (y.max()-y.min()) / (2.0 * math.sqrt(samples))

    x += xscale * (0.5 - np.random.rand(len(x)))
    y += yscale * (0.5 - np.random.rand(len(y)))

    mask = np.where( (x**2 + y**2 / aspect**2) < (radiusX-0.5*spacingX)**2 )

    X = x[mask]
    Y = y[mask]
    bmask = np.ones_like(X, dtype=bool)

    # Now add boundary points
    
    theta = np.array( [ 2.0 * math.pi * i / (3 * boundary_samples) for i in range(0, 3 * boundary_samples) ])
        
    X = np.append(X, 1.001 * radiusX * np.sin(theta))    
    Y = np.append(Y, 1.001 * radiusX * aspect * np.cos(theta))    
    bmask = np.append(bmask, np.zeros_like(theta, dtype=bool))
    inverse_bmask = np.invert(bmask)

    return X, Y, bmask, inverse_bmask




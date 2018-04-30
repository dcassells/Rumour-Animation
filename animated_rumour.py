"""
==================
Animated histogram
==================

Use a path patch to draw a bunch of rectangles for an animated histogram.

from terminal write:
	python animated_rumour.py #number_of_nodes #number_of_initial_infective
"""

import sys

#import argparse
#parser = argparse.ArgumentParser(
#	description = 'Simulation of rumour model in Maki and Thompson (1973) to show proportion of population never hearing a rumour\n\n'+
#		'usage is: python animated_rumour.py #number_of_nodes #number_of_initial_infective',
#	epilog = 'Should converge to 0.203 - A. Sudbury (1985)')

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.animation as animation

# Fixing random state for reproducibility
#np.random.seed(19680801)

# initialise number of nodes and number of initial infective
if len(sys.argv) < 2:
	# number of nodes
	num = 100
	# number of initial infective
	i_0 = 10
elif len(sys.argv) < 3:
	# number of nodes
	num = int(sys.argv[1])
	# number of initial infective
	i_0 = 10
else:
	# number of nodes
	num = int(sys.argv[1])
	# number of initial infective
	i_0 = int(sys.argv[2])


# define spread function
def spread():
	# count of infective
	I = i_0
	# count of susceptible
	S = num - i_0
	# initial state of nodes
	nodes = ['s']*num
	for i in range(i_0):
	    nodes[i] = 'i'

	# run until no infective
	while I != 0 and S != 0:
	    # caller
	    u = np.random.randint(num)
	    # receiver
	    v = np.random.randint(num)
	    
	    # is u infective
	    if nodes[u] == 'i':
	        # is v suscpetible
	        if nodes[v] == 's':
	            # change v from susceptible to infected
	            nodes[v] = 'i'
	            # one more infective
	            I += 1
	            # one less susceptible
	            S -= 1
	        # else v is infective or removed
	        else:
	            # change u from infective to removed
	            nodes[u] = 'r'
	            # one less infective
	            I -= 1
	return S/num

# histogram our data with numpy
initial = [1]*100
n, bins = np.histogram(initial, 100, density=True, range=(0,1))
data = [spread()]

# get the corners of the rectangles for the histogram
left = np.array(bins[:-1])
right = np.array(bins[1:])
bottom = np.zeros(len(left))
top = bottom + n
nrects = len(left)

###############################################################################
# Here comes the tricky part -- we have to set up the vertex and path codes
# arrays using ``plt.Path.MOVETO``, ``plt.Path.LINETO`` and
# ``plt.Path.CLOSEPOLY`` for each rect.
#
# * We need 1 ``MOVETO`` per rectangle, which sets the initial point.
# * We need 3 ``LINETO``'s, which tell Matplotlib to draw lines from
#   vertex 1 to vertex 2, v2 to v3, and v3 to v4.
# * We then need one ``CLOSEPOLY`` which tells Matplotlib to draw a line from
#   the v4 to our initial vertex (the ``MOVETO`` vertex), in order to close the
#   polygon.
#
# .. note::
#
#   The vertex for ``CLOSEPOLY`` is ignored, but we still need a placeholder
#   in the ``verts`` array to keep the codes aligned with the vertices.
nverts = nrects * (1 + 3 + 1)
verts = np.zeros((nverts, 2))
codes = np.ones(nverts, int) * path.Path.LINETO
codes[0::5] = path.Path.MOVETO
codes[4::5] = path.Path.CLOSEPOLY
verts[0::5, 0] = left
verts[0::5, 1] = bottom
verts[1::5, 0] = left
verts[1::5, 1] = top
verts[2::5, 0] = right
verts[2::5, 1] = top
verts[3::5, 0] = right
verts[3::5, 1] = bottom

###############################################################################
# To animate the histogram, we need an ``animate`` function, which runs the
# spread() function and updates the locations of the vertices for the
# histogram (in this case, only the heights of each rectangle). ``patch`` will
# eventually be a ``Patch`` object.
patch = None


def animate(i):
    # simulate new data coming in
    data.append(spread())
    n, bins = np.histogram(data, 100, density=True, range=(0,1))
    top = bottom + n
    verts[1::5, 1] = top
    verts[2::5, 1] = top
    print(str(i)+': ',np.mean(data))
    return [patch, ]

###############################################################################
# And now we build the `Path` and `Patch` instances for the histogram using
# our vertices and codes. We add the patch to the `Axes` instance, and setup
# the `FuncAnimation` with our animate function.
fig, ax = plt.subplots()
barpath = path.Path(verts, codes)
patch = patches.PathPatch(
    barpath, facecolor='green', edgecolor='yellow', alpha=0.5)
ax.add_patch(patch)

ax.set_xlim(0, 0.5)
ax.set_ylim(bottom.min(), top.max())
ax.set_xlabel('$S/n$')
ax.set_ylabel('Density')
ax.set_title('Distribution of the proportion never hearing the rumour\n for '+str(num)+' nodes and $i_0$ = '+str(i_0))

ani = animation.FuncAnimation(fig, animate, 200, repeat=False, blit=True)
# use .save() to save
#ani.save('rumour.mp4',dpi=250)
# use plt.show() to display
plt.show()

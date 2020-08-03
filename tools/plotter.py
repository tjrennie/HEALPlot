#===============================================================================
# tools/plotter.py
#===============================================================================
'''
python HEALPix map plotting object and scripts
'''

from astropy.visualization.wcsaxes import SphericalCircle
from astropy import units as u
from astropy.io import fits
import astropy.wcs as wcs
import healpy as hp
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reproject import reproject_from_healpix
from tqdm import tqdm
from tools.parser import parse_file


class HPlot:

    def __init__(self,
                param_file_name):
        self.params = parse_file(param_file_name)

        self.map_wcs = wcs.WCS(naxis=2)
        self.map_wcs.wcs.crpix = self.params['wcs']['crpix']
        self.map_wcs.wcs.cdelt = self.params['wcs']['cdelt']
        self.map_wcs.wcs.crval = self.params['wcs']['crval']
        self.map_wcs.wcs.ctype = self.params['wcs']['ctype']

        self.map_shape = [self.params['wcs']['crpix'][1]*2,
                          self.params['wcs']['crpix'][0]*2]

        self.map_xlims = [self.params['wcs']['crval'][0] - self.params['wcs']['crpix'][0] * self.params['wcs']['cdelt'][0],
                          self.params['wcs']['crval'][0] + self.params['wcs']['crpix'][0] * self.params['wcs']['cdelt'][0]]
        self.map_ylims = [self.params['wcs']['crval'][1] - self.params['wcs']['crpix'][1] * self.params['wcs']['cdelt'][1],
                          self.params['wcs']['crval'][1] + self.params['wcs']['crpix'][1] * self.params['wcs']['cdelt'][1]]

        self.fig = plt.figure(figsize=self.params['gen']['fsize'])
        self.ax  = plt.subplot(111,projection=self.map_wcs)
        self.ax.set_xlim(-0.5, self.map_shape[1] - 0.5)
        self.ax.set_ylim(-0.5, self.map_shape[0] - 0.5)
        self.ax.set_title(self.params['gen']['title'])

    def plot_map(self,map_file_name):
        try:
            map_array = hp.read_map(map_file_name)
            map_array[map_array==0] = np.nan
        except:
            print('error: file not found!')

        map_label = map_file_name.split('/')[-1].split('.')[0]

        wcs_array, footprint = reproject_from_healpix((map_array,'galactic'),
                                                      self.map_wcs,
                                                      shape_out=self.map_shape,
                                                      nested=False)
        im  = self.ax.imshow(wcs_array,**self.params['img'],label=map_label)
        return im

    def plot_cbar(self,image,axis=None):
        if axis==None:
            axis = self.ax
        cax = self.fig.add_axes([axis.get_position().x1+0.01,axis.get_position().y0,0.02,axis.get_position().height])
        cbar = plt.colorbar(image, cax=cax) # Similar to fig.colorbar(im, cax = cax)
        cbar.set_label('T [Kelvin]', rotation=90)

    def overplot(self):
        if self.params['overlay']['galgrid']!=False:
            self.ax.grid(color=self.params['overlay']['galgrid'],ls='-')
        if self.map_ylims[0]<= 0 and self.map_ylims[1]>= 0 and self.params['overlay']['galplane']!=False:
            self.ax.plot(self.map_xlims,[0,0],color=self.params['overlay']['galplane'],transform=self.ax.get_transform('world'),alpha=0.5,label='Galactic Plane')

    def plot_catalogue(self):
        for i in range(len(self.params['cat'].keys())):
            tag = list(self.params['cat'].keys())[i]
            cat_params = self.params['cat'][tag]
            cat_ext = cat_params['fname'].split('.')[-1]
            #read catalogue
            if cat_ext == 'csv':
                cat_data = pd.read_csv(cat_params['fname'])
                cat_data = np.asarray(cat_data)
            elif cat_ext == 'fit' or cat_ext == 'fits':
                cat_data = fits.open(cat_params['fname'])[1].data
            else:
                print('error: file type not recognised')
            #find correct entries
            x, y, r = [],[],[]
            for entry in tqdm(cat_data, miniters = int(len(cat_data)/20)):
                if entry[cat_params['glat']] >= self.map_ylims[0] and entry[cat_params['glat']] <= self.map_ylims[1]:
                    if entry[cat_params['glon']] >= self.map_xlims[0] and entry[cat_params['glat']] <= self.map_xlims[1]:
                        # accepted entry, proceed to produce list of items
                        x.append(entry[cat_params['glon']])
                        y.append(entry[cat_params['glat']])
                        if cat_params['rad'] != 'none':
                            r.append(entry[cat_params['rad']] * cat_params['rad_unit'])

            #plot
            if cat_params['ptype'] == 'circle':
                for i in range(len(x)):
                    if i == 0:
                        c = Circle((x[i],y[i]),
                                    r[i],
                                    edgecolor=cat_params['c'],
                                    facecolor='none',
                                    transform=self.ax.get_transform('world'),
                                    alpha=0.25,
                                    label=cat_params['name'])
                    else:
                        c = Circle((x[i],y[i]),
                                   r[i],
                                   edgecolor=cat_params['c'],
                                   facecolor='none',
                                   transform=self.ax.get_transform('world'),
                                   alpha=0.25)
                    self.ax.add_patch(c)
                patch = mpatches.Patch(color='grey', label='Manual Label')
            elif cat_params['ptype'] == 'scatter':
                self.ax.scatter(x,y,
                                c=cat_params['c'],
                                marker='+',
                                transform=self.ax.get_transform('world'),
                                alpha=0.25,
                                label=cat_params['name'])
            else:
                print('{} ptype not recognised'.format(tag))

            print('{} {} targets plotted'.format(len(x),cat_params['name']))

    def show(self):
        self.ax.legend(bbox_to_anchor=(-.18,1), loc="upper left", borderaxespad=0)
        plt.show()

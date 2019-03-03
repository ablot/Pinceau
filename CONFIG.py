# File to contain constant, mostly used for creating absolute paths
import os, sys
import Pinceau

_j = os.path.join
HOME = os.path.expanduser('~')
LOCAL = os.path.split(os.path.abspath(Pinceau.__file__))[0]
PARENT = '/'.join(LOCAL.split('/')[:-1])
DATA = _j(LOCAL, 'data/')
SAVE_PATH = _j(LOCAL, 'output_figures/')

if not os.path.isdir(SAVE_PATH):
    os.mkdir(SAVE_PATH)

if PARENT not in sys.path:
    sys.path.append(PARENT)

import matplotlib

FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
fonts = ['Liberation Sans'] + matplotlib.rcParams['font.sans-serif']
D = {'xtick.major.size': 10,
     'font.sans-serif': fonts,
     'font.family': 'sans-serif',
     'font.size': 14,
     'text.usetex': False,
     'text.latex.unicode': False,
     'figure.dpi': 72,  # 300,
     'figure.facecolor': 'w'}
matplotlib.rcParams.update(D)

from matplotlib.pyplot import figure

# all in mm:
natureGuideLines = {'single': 89,
                    'double': 183,
                    'full': 247}

mm2inches = lambda x: x * 0.0393700787
figSize = dict([(k, mm2inches(v)) for k, v in natureGuideLines.items()])
dot2inch = lambda x: x / matplotlib.rcParams['figure.dpi']
inch2dot = lambda x: x * matplotlib.rcParams['figure.dpi']
BLUE = '#5599ff'
YELLOW = '#d4aa00'
GREEN = '#8dd35f'


def myFigure(ratio, size='double', **kwargs):
    w = figSize[size]
    h = w * ratio
    fig = figure(figsize=(w, h), dpi=72, **kwargs)  # frameon = False, **kwargs)
    return fig


METHOD = "field"

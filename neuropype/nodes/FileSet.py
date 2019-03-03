import os
from neuropype import node
from neuropype.datafile import *
import neuropype.datatypes.Sweep as Sweepmodule
import neuropype.datatypes.SweepData as SweepDatamodule
import neuropype.ressources.progressbar as pgb
from neuropype.tag import UniverseError
from copy import copy, deepcopy
from neuropype.parameter import path2file
import bisect
from numpy import cumsum

class FileError(Exception):
    pass

class FileSet(node.Node):
    '''Extract sweep from files in filelist
    
    TODO: implement a change gain, unit, title function that one can apply one 
    the file, the sweep or the chan
          think about when to load the file data (put them in self._data)
          add a save option to save self._data
          
    '''
    def __init__(self, name, parent):
        self.out_sweep = node.Output('Sweep')
        self.out_sweepData = node.Output('SweepData')
        self.out_numSweeps = node.Output('int')
        self.out_chanNames = node.Output('list')
        self.out_origin = node.Output('list')
        self.out_tag = node.Output('list')
        self.out_sweepInfo = node.Output('SweepInfo')
        self._dataFile = {}
        
        super(FileSet, self).__init__(name, parent)
        #link output function to node:
        Outs = ['sweep', 'sweepData', 'numSweeps', 'chanNames', 'origin', 'tag', 'sweepInfo']
        for i in Outs:
            out = getattr(self, 'out_'+i)
            setattr(out, 'output', getattr(self, i))
        
        self._outputGroups['sweep'] = {'sweep': 'out_sweep', 'numSweeps': 
        'out_numSweeps', 'chanNames': 'out_chanNames', 'origin': 'out_origin',
        'tag': 'out_tag', 'sweepInfo': 'out_sweepInfo'}
        self._outputGroups['sweepData'] = {'sweep': 'out_sweepData', 'numSweeps': 
        'out_numSweeps', 'chanNames': 'out_chanNames', 'origin': 'out_origin',
        'tag': 'out_tag', 'sweepInfo': 'out_sweepInfo'}
        
        filelist = path2file('filelist', self,
                        ext = ['Supported files (*.abf *.wcp *.dat)', 
                               'WCP files (*.wcp)', 
                               'PClamp files (*.abf *.dat)',
                               'All  (*)'],
                        mpl = True)
        self._params = {'filelist': filelist, 
                        'policy': {'cache':'all'}, 
                        'graphviz': {'style': 'filled', 'fillcolor': 'coral'}}
                   
    def set_param(self,  *args, **kwargs):
        '''Reimplemented to add files'''
        
        if len(args) == 2:
            kwargs[args[0]] = args[1]
        
        for param_name, value in kwargs.iteritems():
            if param_name == 'filelist':
                self.dirty('all')
                # security dirty, usefull only if you change just filelist
                value = self._params['filelist'].checkType(value)
                knownfiles = self._dataFile.keys()
                #find the names of files in the memory    
                for name in value:
                    File = self._add_file(name, verbose = 0)
                    if File.name in knownfiles:
                        knownfiles.remove(File.name)
                for old_file in knownfiles:
                    self._removeFile(old_file)
                    #self._dataFile.pop(old_file)
            elif param_name is 'policy':
                for datafile in self._dataFile.values():
                    datafile.set_policy(value)
        
        super(FileSet, self).set_param(**kwargs)
    
    ###########################################################################
    ### Lines used to create and modify self._data, the inner dict          ###
    ###########################################################################
    def load(self):
        pbar = pgb.ProgressBar(maxval = self.numSweeps(), term_width = 79 \
                ).start()
        for index_sweep in range(self.numSweeps()):
            sweep = self.findOriginFromIndex(index_sweep)
            pbar.update(index_sweep)
        pbar.finish()
    
    def _removeFile(self, filename):
        self._dataFile.pop(filename)
        delattr(self, filename)
        #TODO: del also filename sons
    
    def _add_file(self, Filename, verbose = 1):
        '''Add a file in the FileSet'''
        Filename = unicode(Filename)
        
        if Filename[0]!= '/':
            Filename = os.path.join(self.parent.home,Filename)
        local_name = Filename.split('/')[-1::-1]
        local_name = [i.strip().replace(' ','').replace('.','') for i in local_name if i]
        local_name = '_'.join(local_name)
        
        name = 'File_'+local_name
        path = os.path.split(Filename)[0]
        extension = os.path.splitext(Filename)[1]
        if name in self._dataFile.keys():
            if getattr(self, name).path == path:
                if verbose: print 'File %s named already in this fileSet. Skip'%name
                return getattr(self, name)
        self._dataFile[name] = DataFile(Filename)
        
        
        File = FileClass(name, path)
        setattr(self, name, File)
        self.to_default(File)
        
        #ipshell()
        return File
    
    def to_default(self, node, prop = None):
        '''Reset the node properties to default values (read in file)
        
        if prop, reset only property named "prop"'''
        
        
        if isinstance(node, FileClass):
            if prop is None:
                #get rid of useless data:
                for i in ['gains', 'numSweeps', 'samplingInterval', 'channelInfo']:
                    setattr(node, i, getattr(self._dataFile[node.name], i))
                return
            setattr(node, prop, getattr(self._dataFile[name], prop))
            return
        if isinstance(node, SweepClass):
            fileName = node.parent.name
            index_sweep = node.index_sweep
            _sweepInfo = self._dataFile[fileName].sweepInfo(index_sweep)
            
            if prop is None:
                node.__dict__.update(_sweepInfo)
                return
            setattr(node, prop,  _sweepInfo[prop])
            return
        
        if isinstance(node, ChanClass):
            #it's a chan
            index_chan =  node.index_chan
            parent = node.parent
            if isinstance(parent, SweepClass):
                index_sweep = parent.index_sweep
                fileName = parent.parent.name
                _sweepInfo = self._dataFile[fileName].sweepInfo(index_sweep)
                _chanInfo = _sweepInfo['channelInfo'][index_chan]
                
                if prop is None:
                    node.__dict__.update(_chanInfo.__dict__)
                    return
                setattr(node, prop, getattr(_chanInfo, prop))
                return
            else:
                if not isinstance(parent, FileClass):
                    raise TypeError('%s should be FileClass of SweepClass instance'%parent)
                fileName = parent.name
                _sweepInfo = self._dataFile[fileName].sweepInfo(0)
                _chanInfo = _sweepInfo['channelInfo'][index_chan]
                
                if prop is None:
                    node.__dict__.update(_chanInfo.__dict__)
                    return
                setattr(node, prop, getattr(_chanInfo, prop))
                return
        print 'node %s not found'% node
    
    ###########################################################################
    ### Lines used to acces and return sweep using self._data               ###
    ###########################################################################
    def numSweeps(self):
        listFile = [getattr(self, File) for File in self._dataFile.keys()]
        return sum([File.numSweeps for File in listFile])
    
    def list_files(self):
        lst = self._dataFile.keys()
        lst.sort()
        return lst
    
    def sweepInfo(self, index):
        File, Sweep = self.findOriginFromIndex(index)
        out = copy(Sweep)
        delattr(out, 'parent')
        [delattr(out, c) for c in self.chanNames(index)]
        out.parent = File.name
        out.channelInfo = deepcopy(out.channelInfo)
        return out

    def sweep(self, index, chan = None):
        """Return a Sweep object containing channel infos and data"""
        data, out_info = self._sweep(index, chan)
        out = Sweepmodule.Sweep('Sweep_'+str(index), data, out_info)
        out.tag = self.tag(index)
        return out

    def sweepData(self, index, chan = None, dtype = None):
        if dtype is None:
            dtype = 'int16'
        data, out_info = self._sweep(index, chan, dtype)
        out = SweepDatamodule.SweepData('Sweep_'+str(index), data[1:], out_info)
        out.tag = self.tag(index)
        return out
        
    def _sweep(self, index, chan = None, dtype = None):
        """Return a data and out_info
        
        dtype can be used to set the type of the data array. If one integer type
        is set, datas will not be converted in true unit but read as stored in 
        the file. The time line will be kept to keep the indices constant but is
        likely to be corrupted (if the resolution of dtype is inferior to 2 
        times the number of points)"""
        #print 'Extracting sweep %s'%index
        File, Sweep = self.findOriginFromIndex(index)
        #saved_sw = self._memory.get(index)
        #if saved_sw is not None:
            #if chan is None:
                #return saved_sw
            #return saved_sw._keepOnlyChan(chan)
        if chan is None:
            chan = [i.name for i in Sweep.channelInfo]
        if not isinstance(chan, list):
            chan = [str(chan)]
        
        chan_index = []
        out_info = []
        for cname in chan:
            c = getattr(Sweep, cname)
            chan_index.append(c.index_chan)
            out_info.append(ChannelType(c.name, c.title, c.units, c.isinput,  \
            c.maxval, c.factor))        
        name = File.name
        data = self._dataFile[name].sweep(Sweep.index_sweep, chans = chan_index,
                                          dtype = dtype)
        return data, out_info
        
#         out = Sweepmodule.Sweep('Sweep_'+str(index), data, out_info)
#         #if self.get_param('numSweepCached') is not None:
#             #if self.get_param('numSweepCached') == 'NoLimit':
#                 #pass
#             #else:
#                 #maxvalue = int(self.get_param('numSweepCached'))
#                 #while len(self._memory)>= maxvalue:
#                     #self._memory.popitem()
#                     ##TODO: change to pop the last element (not one by chance)
#             ##self._memory[index] = out
#         #print 'Extracted !\n'
#         out.tag = self.tag(index)
        
    
    def tag(self, index):
        tags = []
        tagMg = self.parent.tagManager
        typeName = 'SweepIndex_in_'+self.name
        tagName = 'Sw_'+str(index)
        try:
            tags.append(tagMg.tagInstance(typeName, tagName, value = index, 
                            universe = int))
        except UniverseError:
            print '''list_files has probably changed since tagType creation, 
            some tags might be corrupted if you don\'t update them (dirty 
            fileSet should work)'''
            tagMg.list_tag[typeName].universe = range(self.numSweeps())
            tags.append(tagMg.tagInstance(typeName, tagName, value = index, 
                            universe = range(self.numSweeps())))
        
        fileName, Sw = self.origin(index)
        typeName = 'File_in_'+self.name
        try:
            tags.append(tagMg.tagInstance(typeName, fileName, value = fileName, 
                          universe = self.list_files()))
        except UniverseError:
            print '''list_files has changed since tagType creation, some tags
            might be corrupted if you don\'t update them (dirty fileSet should
            work)'''
            tagType = getattr(tagMg, typeName)
            tagType.universe = self.list_files()
            #ipshell()
            tags.append(tagMg.tagInstance(typeName, fileName, value = fileName, 
                          universe = self.list_files()))
        
        userTags = self._user_defined_tags(index)
        if userTags is not None:
            tags = tags + userTags
        return tags
    
    def _user_defined_tags(self, index):
        return None
        '''TODO deal with manually defined tags, store them somewhere, not in
        cache or make sure dirty will not erase them and return a list of tag 
        instance when this method is called (make sure it's a list even if there
        is only one tag to apply'''
    
    def chanNames(self, index=0):
        files = list_instance(self, FileClass)
        File, Sweep = self.findOriginFromIndex(index)
        out = list_instance(Sweep, ChanClass)
        return out
    
    def fileBorder(self):
        """return the index of the first sweep of each file"""
        return cumsum([0]+[getattr(self, n).numSweeps for n in self.list_files()])

    def findSweepFromFile(self, fileName):
        """return the index of the first sweep of file fileName"""
        lst_files = self.list_files()
        try:
            ind = lst_files.index(fileName)
        except ValueError:
            print 'file %s not in %s'%(fileName, self.name)
            return
        n = 0
        ind = 0
        while n<ind:
            ind += getattr(self,lst_files[n]).numSweeps
            n+=1
        return ind
        
    def findOriginFromIndex(self, index):
        if not self.get_param('filelist'):
            raise FileError('No files set in node "%s".'%self.name)
        try:
            assert index >= 0 & index < self.numSweeps()
        except AssertionError:
            raise FileError('Error in %s. Sweep %s doesn\'t exist'%(self.name, 
                                                                    index))
        n = 0
        ordered = self._dataFile.keys()
        ordered.sort()
        for Filename in ordered:
            File = getattr(self, Filename)
            if index < n + File.numSweeps:
                if hasattr(File,'Sweep_'+str(index - n)):
                    Sweep = getattr(File,'Sweep_'+str(index - n))
                else:
                    #_sweepInfo = self._dataFile[File.name].sweepInfo(index - n)
                    name = 'Sweep_'+str(index - n)
                    Sweep = SweepClass(name = name, parent = File, index = index - n)
                    setattr(File, name, Sweep)
                    self.to_default(Sweep)
                    #for prop in ['numChans', 't0','sampling']:
                        #setattr(Sweep, prop, _sweepInfo.get(prop))
                    for index_chan, chanInf in enumerate(Sweep.channelInfo):
                        chan = ChanClass(name = chanInf.name, parent = Sweep,
                               index_chan = index_chan)
                        setattr(Sweep, chanInf.name, chan)
                        self.to_default(chan)
                return (File, Sweep)
            n +=File.numSweeps
    def origin(self, index, tag = None):
        File, Sweep = self.findOriginFromIndex(index)
        return [File.name, Sweep.name]

################################################################################

class BranchNode(object):

    def __init__(self, name, parent=None):
        #super(BranchNode, self).__init__(parent)
        self.name = name
        self.parent = parent
        if parent is not None:
            parent.insertChild(self)
        self.children = []

    def orderKey(self):
        return self.name.lower()

    #def toString(self):
        #return self.name

    def __len__(self):
        return len(self.children)

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1
        
    def childWithKey(self, key):
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None
        
    def insertChild(self, child):
        child.parent = self
        bisect.insort(self.children, (child.orderKey(), child))
        
    #def hasLeaves(self):
        #if not self.children:
            #return False
        #return isinstance(self.children[0], LeafNode)

class FileClass(BranchNode):
    '''File properties'''
    def  __init__(self, name, path, parent = None):
        super(FileClass, self).__init__(name, parent)
        self.name = str(name)
        self.path = str(path)

class SweepClass(BranchNode):
    '''Sweep properties'''
    def __init__(self, name, parent, index):
        if not isinstance(parent, FileClass) and (parent is not None):
            raise ValueError('Sweep parent must be a FileClass instance')
        super(SweepClass, self).__init__(str(name), parent)
        
        self.index_sweep = int(index)
    
class ChanClass(object):
    '''Chan properties'''
    def __init__(self, name, parent, index_chan, gain = 'nd', isinput = 'nd', maxval = 'nd',
                 title = 'nd', units = 'nd', factor = 'nd'):
        if not isinstance(parent, SweepClass) and (parent is not None) and \
           not isinstance(parent, FileClass):
            raise ValueError('Chan parent must be a FileClass or a SweepClass instance')
        
        self.index_chan = int(index_chan)
        self.name = str(name)
        self.parent = parent
        self.gain = gain
        self.isinput = isinput
        self.maxval = maxval
        self.title = title
        self.units = units
        self.factor = factor

def list_instance(obj, instance):
    out = []
    for name, Object in vars(obj).iteritems():
        if Object.__class__ == instance:
            out.append(name)
    return out

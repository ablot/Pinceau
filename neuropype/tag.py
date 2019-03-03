# -*- coding: utf-8 -*-

##debuging tool!
#from IPython.Shell import IPShellEmbed
#banner = '\n*** Nested interpreter *** \n\nYou are now in a nested ipython'
#exit_msg = '*** Closing embedded IPython ***'
##paramv = ['-noconfirm_exit', '-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#paramv = ['-pi1','Neuropype In <\\#>:','-pi2','     .\\D.:','-po','Out<\\#>:']
#ipshell = IPShellEmbed(paramv, banner=banner,exit_msg=exit_msg)
##end of debuging tool

class tagManager(object):
    '''Tag manager's role is not clear yet, made for test purpose'''
    def __init__(self):
        pass
    
    def list_tag(self):
        out = {}
        for name, Object in vars(self).iteritems():
            if Object.__base__ == Tag:
                out[name] = Object
        return out
    
    def add_tagType(self, name, universe = [True, False], verbose = 1):
        name = str(name)
        if name[0].isdigit():
            name = '_' + name
        if name in self.list_tag().keys():
            if verbose: print 'Tag already defined'
            return
        class tempClass(Tag):
            pass
        U_list = [int, float]
        if (universe not in U_list) and (not isinstance(universe, list)):
            universe = [universe]
        tempClass.__name__ = name
        tempClass.universe = universe
        setattr(self, name, tempClass)
        return tempClass
    
    def tagInstance(self, typeName, tagName, value, universe = None):
        '''return a tagInstance ready to tag one datatype, check if tagType
        exists and create it if universe is given'''
        if typeName not in self.list_tag().keys():
            if universe is None:
                msg = 'tagType doesn\'t exists, create it first'
                raise TagTypeError(msg, typeName)
            self.add_tagType(typeName, universe)
        elif universe is not None:
            prevUniverse = getattr(self,typeName).universe
            if prevUniverse != universe:
                msg = 'Universe different in tagManager and tagInstance call !!'
                raise UniverseError(msg, prevUniverse, universe)
        out = getattr(self, typeName)(tagName, value)
        return out
    
    def rmTag(self, typeName):
        delattr(self, typeName)

class TagTypeError(Exception):
    ''' Tag Type Error'''
    pass

class UniverseError(Exception):
    '''Occurs when an already defined tagType has an incorrect universe'''
    pass
    

class Tag(object):
    '''Tag type, each instance has at least one value from class.universe'''
    def __init__(self, name, value, **kwargs):
        self.name = str(name)
        value = self.checkValue(value)
        if value is None:
            print 'Tag created without value, change it manually !'
            return
        self.value = value
        for k, v in kwargs:
            setattr(self, k, v)
    
    def checkValue(self,value =None):
        if value is None:
            value = self.value
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if self.universe in [int, float]:
                if not isinstance(v, self.universe):
                    print 'Error, value %s must be %s to be in universe'%(v, 
                                                                  self.universe)
                    return None
            else:
                if v not in self.universe:
                    print 'Error, value %s not in Tag universe'%v
                    return None
        return value
        
    def __call__(self):
        return self.value

def combine(tag0, tag1, AND = 1, OR = 1):
    '''Given 2 lists of tag return a new list of tags
    
    if AND = 1, OR = 1:
        output contains all the tags
    if AND = 1, OR = 0
        output contains only tags present in the two lists (same type, same
        value)
    if AND = 0, OR = 1
        output contains only tags present in one of the list
    if AND = 0, OR = 0
        output is an empty list
    
    note: combine compare tag instance, not tagTypes'''
    if not isinstance(tag0, list):
        tag0 = [tag0]
    list0 = {}
    for tag in tag0:
        list0[tag.__class__.__name__] = tag
    list1 = {}
    if not isinstance(tag1, list):
        tag1 = [tag1]
    for tag in tag1:
        list1[tag.__class__.__name__] = tag
    outlist = []
    
    commonTypes = [i for i in list0.keys() if list1.has_key(i)]
    for typeName in commonTypes:
        values0 = sorted(list0[typeName]())
        values1 = sorted(list1[typeName]())
        values = []
        commonValues = []
        differentValues = []
        for i in values0:
            if i in values1:
                commonValues.append(i)
                values1.remove(i)
            else:
                differentValues.append(i)
        differentValues += values1
        if AND:
            values += commonValues
        if OR:
            values += differentValues
        if len(values)>0:
            tag = list0[typeName]
            tag.value = values
            outlist.append(tag)
    if OR:
        differentTypes0 = [i for i in list0.keys() if i not in commonTypes]
        differentTypes1 = [i for i in list1.keys() if i not in commonTypes]
        for typeName in differentTypes0:
            outlist.append(list0[typeName])
        for typeName in differentTypes1:
            outlist.append(list1[typeName])
    return outlist
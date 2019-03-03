# -*- coding: utf-8 -*-
from neuropype.tag import Tag

class Datatype(object):
    '''Common class used by all datatypes (equivalent to node for nodes)
    
    define mainly three things:
    * tracing option through nodes (origin)
    * tagging
    * typing'''
    
    def __init__(self, name):
        self.name = name
        self.tag = []
        self.way = []
    
    def _checkTags(self):
        listag = {}
        error = 0
        for tag in self.tag:
            if tag.__class__.__base__ != Tag:
                print 'Tag %s is not a tag instance !'%tag.name
                error += 1
            else:
                if tag.__class__ in listag.keys:
                    print 'Tag type %s used several times !'%tag.__class__
                    print 'Tag names: %s and %s'%(tag.name, listag[tag.__class__].name)
                    error += 1
                else:
                    listag[tag.__class__] = tag
                tag.checkValue()
        if not error:
            print 'Tags checked, no error found'
            return
        print '!!!! %s error(s) found in self.name !!!!'%error
    
    def list_tags(self):
        '''Return a dictionary associating tagTypes to their value(s)'''
        out = {}
        for tag in self.tag:
            out[tag.__class__.__name__] = tag()
        return out

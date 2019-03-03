Tagging system is based on tag.py. This file defines two main classes:
* tagManager: Handle the different tags, make sure tag types are
unique, centralise tag creation functions * tag: class inherited by
all tagType classes. Basically one tag is an instance of a tagType
class (that inherit from neuropype.tag). This tagType class has one
class property: universe, the possible value for the tag. One tag has
a name (not sure it is needed) and a value, this value is a list of
elements from universe Ex: tagType 'drug' can have a universe being
before, wash, drug0, drug1 each tag of type 'drug' will have a
specific value, that can contain one or more element of universe. So
one can tag one sweep with drug0 and drug1

To make this tagManager available in all nodes, I've put it in tree.py Not sure
the centralisation of tagTypes is really needed, but it can surely work with it

So each datatype instance has a tag property. Each node has to deal with it
itself, so if you don't want the tags to 'disappear' in a node you have to make
it tag its output properly. The nodes also have to create the proper tagTypes if
they don't exist, tagManager.tagInstance is probably the easiest way to do it,
it return 2 kind of error that a node should be able to handle

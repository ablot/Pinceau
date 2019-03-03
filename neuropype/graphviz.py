#print 'import networkx'
#import networkx as nx
print 'importing pygraphviz'
import pygraphviz as pgv
import os

class GRAPH(object):
    def __init__(self,name, Tree, format = 'dot'):
        self.name=name
        self.Tree=Tree
        self.path = self.Tree.home+self.name+'.'+format
        self.graph=pgv.AGraph(directed=True,rankdir='LR', strict = False)
   
    def createGraph(self, groups = 0):
        '''create a simple graph from a Pathway instance'''
        
        '''clear the graph, needed if you want to remove something previously on the graph'''
        del self.graph
        self.graph = pgv.AGraph(directed=True,rankdir='LR', strict = False)
        
        '''create the nodes'''
        for node_name in self.Tree.list_nodes():
            node =getattr(self.Tree, node_name)
            if not groups:
                outputs = node.outputs.keys()
                inputs = node.inputs.keys()
            else:
                outputs = node._outputGroups.keys()
                inputs = node._inputGroups.keys()
            
            outputs.sort()
            inputs.sort()
            out = '|'.join(['<'+i+'> '+i for i in outputs if i is not None])
            inp = '|'.join(['<'+i+'> '+i for i in inputs if i is not None])
            name = '<'+node.name+'> '+node.name
            label = '{{'+inp+'}|'+name+'|{'+out+'}}'
            param = node.get_param('graphviz')
            if param is None: param = {}
            self.graph.add_node(node.name,label = label, shape='record')
            self.graph.get_node(node.name).attr.update(param)

            
        '''create the links'''
        for node_name in self.Tree.list_nodes():
            node =getattr(self.Tree, node_name)
            if not groups:
                for in_name, out in node.inputs.iteritems():
                    if out is not None:
                        from_node, out_name = out
                        self.graph.add_edge(from_node,node.name,
                                            arrowhead='ediamond', 
                                            arrowtail='none',
                                            tailport = out_name,
                                            headport = in_name)
            else:
                for inGroup_name in node._inputGroups.keys():
                    connected = node._inGrConnection.get(inGroup_name)
                    if connected is not None:
                        from_node, out_name = connected
                        self.graph.add_edge(from_node,node.name,
                                            arrowhead='ediamond', 
                                            arrowtail='none',
                                            tailport = out_name,
                                            headport = inGroup_name)
        
    def drawGraph(self,format='dot',path=None, prog='dot'):
        if path is None:
            path=self.path
        self.graph.layout(prog=prog)
            
        self.graph.draw(path,format=format)
    
    def updateGraph(self,format='dot', path=None,prog='dot', groups = 0, 
                    verbose = 0):
        self.createGraph(groups)
        if path is None: path=self.path
        self.drawGraph(format, path, prog)
                
        if verbose: print 'graph updated and saved in %s.\n'%path
    
    def show(self, path = None):
        if path is None:
            path=self.path
        if self.Tree.mw is None:
            print 'Showing graph without GUI'
            print 'This action is likely to fail'
            if not os.path.isfile(path):
                print 'file not found, create graph'
                self.updateGraph(format='dot', path=path,prog='dot')
            print 'importing matplotlib image'
            import matplotlib.image as mpimg
            print 'importing matplotlib pyplot'
            import matplotlib.pyplot as plt
            fig = plt.figure()
            img=mpimg.imread(path)
            ax = fig.add_axes([0,0,1,1])
            imgplot = ax.imshow(img, aspect = 'equal')
            plt.axis('off')
            plt.title(self.name)
        else:
            self.Tree.showGraph()
    
    # small test before I discover xdot
    # def nx_graph_init(self):
    #     self.createGraph()
    #     self.nx_graph = nx.from_agraph(self.graph)
    #     self.nx_fig = plt.figure()
    #     self.nx_ax = self.nx_fig.add_axes([.1,.1,.8,.8])
    #     self.pos = nx.spring_layout(self.nx_graph)
    #     nx.draw_networkx_nodes(self.nx_graph, ax = self.nx_ax,
    #                            pos= self.pos,
    #                            node_color = ['b']*len(self.nx_graph.nodes()))
    #     nx.draw_networkx_edges(self.nx_graph, ax = self.nx_ax,
    #                            pos=self.pos,
    #                            node_color = ['k']*len(self.nx_graph.nodes()),
    #                            arrows = False)
    #     nx.draw_networkx_labels(self.nx_graph, ax = self.nx_ax,
    #                            pos=self.pos)

    
    # def select_node(self, nodeName, color):
    #     nx.draw_networkx_nodes(self.nx_graph, ax = self.nx_ax, pos = self.pos, nodelist = [nodeName], node_color = color)
    #     self.nx_fig.canvas.draw()

    



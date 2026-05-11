import geopy.distance

from database.DAO import DAO
from datetime import datetime
import networkx as nx


def getPesoTempoPercorrenza(u, v, vel):
    dist = geopy.distance.distance((u.cordX, u.cordY), (v.cordX, v.cordY)).km
    time = dist/vel* 60 #minuti
    return time


class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo = nx.DiGraph()
        self._idMapFermate = {}
        for f in self._fermate:
            self._idMapFermate[f.id_fermata] = f

    def getShortestPath (self, u, v):
        return nx.single_source_dijkstra_path(self._grafo, u, v)

    def buildGraphPesato(self):
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)
        self.addEdgesPesati()
        self.addEdgesPesatiTempi()

    def addEdgesPesatiTempi(self):
        #Questo metodo crea degli archi, in cui il peso è pari al tempo di percorrenza di quell'arco, ottenuto come rapporto fra la distanza fra due stazioni e la velocità di percorrenza
        self._grafo.clear_edges()
        allEdgesVel = DAO.getAllEdgesVel()
        for e in allEdgesVel:
            u = self._idMapFermate[e[0]]
            v = self._idMapFermate[e[1]]
            peso = getPesoTempoPercorrenza(u, v, e[2])
            self._grafo.add_edge(u, v, weight=peso)

    def addEdgesPesati(self):
        # riutilizzare il principio di funzioonamento del metodo addEdeges3, ma contando quante volte provo ad aggiungere l'arco
        self._grafo.clear_edges()
        alledges = DAO.getAllEdges()
        for conn in alledges:
            u = self._idMapFermate[conn.id_stazP]
            v = self._idMapFermate[conn.id_stazA]
            if self._grafo.has_edge(u,v):
                self._grafo[u][v]['weight'] += 1
            else:
                self._grafo.add_edge(u, v, weight=1)

    def addEdgesPesatiV2(self):
        # Delega il calcolo del peso alla query sql, per semplificarci la vita in python
        self._grafo.clear_edges()
        allEdgesWPeso = DAO.getAllEdgesPesati()
        # (id_stazP, id_stazA, peso)
        for e in allEdgesWPeso:
            u = self._idMapFermate[e[0]]
            v = self._idMapFermate[e[1]]
            peso = e[2]
            self._grafo.add_edge(u, v, peso)

    def getArchiPesoMaggiore (self):
        edges = self._grafo.edges(data=True)
        edgesMaggiori = []
        for e in edges:
            if self._grafo.get_edge_data(e[0], e[1])["weight"] > 1:
                # self._grafo[e[0]][e[1]]["weight"]
                edgesMaggiori.append(e)
        return edgesMaggiori

    def getBFSNodesFromEdges(self, source):
        archi = nx.bfs_edges(self._grafo, source)
        nodiBFS = []
        for u, v in archi:
            nodiBFS.append(v)
        return nodiBFS

    def getBFSNodesFromTree(self, source):
        tree = nx.bfs_tree(self._grafo, source)
        archi = list(tree.edges())
        nodi = list(tree.nodes())
        return nodi

    def getDFSNodesFromEdges(self, source):
        archi = nx.dfs_edges(self._grafo, source)
        nodiDFS = []
        for u, v in archi:
            nodiDFS.append(v)
        return nodiDFS

    def getDFSNodesFromTree(self, source):
        tree = nx.dfs_tree(self._grafo, source)
        archi = list(tree.edges())
        nodi = list(tree.nodes())
        return nodi

    def buildGraph(self):
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)

        # tic = datetime.now()
        # self.addedges()
        # toc = datetime.now()
        # print("Tempo impiegato da modo 1:", toc-tic)
        #
        # tic = datetime.now()
        # self.addedges2()
        # toc = datetime.now()
        # print("Tempo impiegato da modo 2:", toc-tic)

        tic = datetime.now()
        self.addedges3()
        toc = datetime.now()
        print("Tempo impiegato da modo 3:", toc-tic)

    def addedges(self):
        self._grafo.clear_edges()
        for u in self._fermate:
            for v in self._fermate:
                if DAO.hasconn(u,v):
                    self._grafo.add_edge(u,v)

    def addedges2(self):
        self._grafo.clear_edges()
        for u in self._fermate:
            for conn in DAO.getvicini(u):
                v = self._idMapFermate[conn.id_stazA]
                self._grafo.add_edge(u,v)

    def addedges3(self):
        self._grafo.clear_edges()
        alledges=DAO.getAllEdges()
        for conn in alledges:
            u = self._idMapFermate[conn.id_stazP]
            v = self._idMapFermate[conn.id_stazA]
            self._grafo.add_edge(u, v)


    def get_numnodi(self):
        return len(self._grafo.nodes())
    def get_numarchi(self):
        return len(self._grafo.edges())
    @property
    def fermate(self):
        return self._fermate
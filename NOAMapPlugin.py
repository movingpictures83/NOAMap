# Create noa wile that will map node id with it's name to appear in the graph

import pandas as pd

def get_mapping_dict(metadata):
    metadata_path = metadata

    name_col = 1 #started from 0
    metabolite_col=-1

    map_dict = {}

    with open(metadata_path, 'r') as f:
        f.readline()
        for line in f.readlines():
            line = line.strip("\n")
            row = line.split("\t")
            id = row[metabolite_col]
            if id!="":
                map_dict[id] = id + "__" + row[name_col].replace(",","").replace(" ","_")
    return map_dict


def get_graph_dict(gml_file):
    # Write graph to dictionary:
    graph_dict = {}
    with open(gml_file, "r") as f_gml:
        node = False
        edge = False

        for line in f_gml.readlines():
            if line == "node [\n":
                node = True
            elif line == "edge [\n":
                edge = True
            elif line == "]\n":
                node = False
                edge = False

            if node:
                if "id " in line:
                    id = line.split(" ")[1].strip("\n").strip('"')
                    graph_dict[id] = {}
                elif "label " in line:
                    label = line.split(" ")[1].strip("\n").strip('"')
                    graph_dict[id]["label"] = label
                    graph_dict[id]["edges"] = []
            elif edge:
                if "source " in line:
                    source = line.split(" ")[1].strip("\n").strip('"')
                elif "target " in line:
                    target = line.split(" ")[1].strip("\n").strip('"')
                elif "weight " in line:
                    weight = line.split(" ")[1].strip("\n").strip('"')
                    graph_dict[source]["edges"].append(
                        {"target": graph_dict[target]["label"], "weight": weight})
    return graph_dict

def create_noa(gml_file, noa_out, metadata):


    hmdb_map = get_mapping_dict(metadata)
    graph_dict = get_graph_dict(gml_file)

    with open(noa_out, "w") as out:
        out.write("Name\tLabelFixed\n")
        for id in graph_dict.keys():
            name = graph_dict[id]["label"]
            if "HMDB" in name:
                out.write("{}\t{}\n".format(name, hmdb_map[name]))
            else:
                out.write("{}\t{}\n".format(name, name))


import PyPluMA

class NOAMapPlugin:
    def input(self, infile):
        inputfile = open(infile, 'r')
        self.parameters = dict()
        for line in inputfile:
            contents = line.strip().split('\t')
            self.parameters[contents[0]] = contents[1]

    def run(self):
        pass

    def output(self, outputfile):
       gml_file = PyPluMA.prefix()+"/"+self.parameters["gmlfile"]
       noa_out = outputfile
       create_noa(gml_file, noa_out, PyPluMA.prefix()+"/"+self.parameters["metadata"])


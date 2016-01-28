#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
                                  harris2graph
                              -------------------
        begin                : 2015-03-25
        copyright            : (C) 2015 by L - P: Heritage LLP
        copyright            : (C) 2015 by John Layt
        email                : john@layt.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import sys, os, argparse, csv

#Global data
dataset = ''
nodes = []
edges = []
nodeId = 0
edgeId = 0
nodeWidth = 50.0
nodeHeight = 25.0
graph = 'gml'

def parseValueList(input, tag):
    return input[len(tag):].strip().replace(',', ' ').split()

def nodeIdForLabel(label):
    for node in nodes:
        if node['label'] == label:
            return node['id']
    return -1

def getNode(id):
    for node in nodes:
        if node['id'] == id:
            return node

def setNode(node, unit, indegree, outdegree):
    global nodeId
    if node:
        nodes.append({'id': nodeId, 'label': node, 'unit': unit, 'indegree': indegree, 'outdegree': outdegree})
        nodeId += 1

def setEdges(sourceId, sourceLabel, targets):
    global edgeId
    for targetLabel in targets:
        setEdge(sourceId, sourceLabel, -1, targetLabel)
        edgeId += 1

def setEdge(sourceId, sourceLabel, targetId, targetLabel):
    global edgeId
    edges.append({'id': edgeId, 'source': sourceId, 'sourceLabel': sourceLabel, 'target': targetId, 'targetLabel': targetLabel, 'weight': 1})
    edgeId += 1

def weightEdges():
    for edge in edges:
        if getNode(edge['source'])['outdegree'] == 1:
            edge['weight'] = edge['weight'] + 2
        if getNode(edge['target'])['indegree'] == 1:
            edge['weight'] = edge['weight'] + 2

def outEdges(id):
    outedges = []
    for edge in edges:
        if edge['source'] == id:
            outedges.append(edge)
    return outedges

def inEdges(id):
    inedges = []
    for edge in edges:
        if edge['target'] == id:
            inedges.append(edge)
    return inedges

def readCsv(csvFile):
    reader = csv.reader(csvFile)
    inNodes = set()
    inEdges = set()
    for record in reader:
        try:
            above = str(record[0])
            below = str(record[1])
            inNodes.add(above)
            inNodes.add(below)
            inEdges.add((above, below))
        except:
            if record:
                print 'Error reading row: ' + record
    index = {}
    for node in sorted(inNodes):
        index[node] = nodeId
        setNode(node, 'context', 0, 0)
    for edge in inEdges:
        above = edge[0]
        below = edge[1]
        setEdge(index[above], above, index[below], below)

def readLst(file):
    line = file.readline().strip()
    if (line is None or not line.startswith('Stratigraphic Dataset')):
        sys.stderr.write('Invalid Header Line\n')
        return False
    dataset = line.strip()[len('Stratigraphic Dataset'):].strip()
    if args.name:
        dataset = args.name
    elif not dataset:
        dataset = 'harris'
    line = file.readline().strip()
    if (line is None or line != ''):
        sys.stderr.write('Missing Blank Line')
        return False
    line = file.readline().strip()
    if (line is None or line != 'Name'):
        sys.stderr.write('Invalid Name Line')
        return False
    context = ''
    above = []
    contemporary = []
    equal = []
    below = []
    unit = ''
    for line in file:
        if (line.strip() == ''):
            pass
        elif (not line.startswith(' ')):
            if (context):
                setEdges(nodeId, context, below)
                setNode(context, unit, len(above), len(below))
            context = line.strip()
            above = []
            contemporary = []
            equal = []
            below = []
            unit = ''
        else:
            attribute = line.strip()
            if (attribute.lower().startswith('above:')):
                above.extend(parseValueList(attribute, 'above:'))
            elif (attribute.lower().startswith('contemporary with:')):
                contemporary.extend(parseValueList(attribute, 'contemporary with:'))
            elif (attribute.lower().startswith('equal to:')):
                equal.extend(parseValueList(attribute, 'equal to:'))
            elif (attribute.lower().startswith('below:')):
                below.extend(parseValueList(attribute, 'below:'))
            elif (attribute.lower().startswith('unit class:')):
                unit = attribute[len('unit class:'):].strip()

    if context:
        setEdges(nodeId, context, below)
        setNode(context, unit, len(above), len(below))

    for edge in edges:
        edge['target'] = nodeIdForLabel(edge['targetLabel'])


def writeGv(simple):
    print 'digraph ' + dataset.replace(' ', '_') + ' {'
    if not simple:
        weightEdges()
        print '    splines=polyline' # Should be ortho but ports support not implemented
        print '    concentrate=true'
        print '    ranksep="1.0 equally"'
        print '    nodesep="2.0 equally"'
        print '    node [shape=box]'
        print '    edge [arrowhead=none headport=n tailport=s width=' + str(nodeWidth) + ' height=' + str(nodeHeight) + ']'

    for edge in edges:
        if simple:
            print '    "' + str(edge['sourceLabel']) + '" -> "' + str(edge['targetLabel']) + '";'
        else:
            print '    "' + str(edge['sourceLabel']) + '" -> "' + str(edge['targetLabel']) + '" [weight=' + str(edge['weight']) + '];'


    print '}'


def writeGml(simple):
    print 'graph ['
    print '    directed 1'

    for node in nodes:
        print '    node ['
        print '        id ' + str(node['id'])
        print '        label "' + str(node['label']) + '"'
        if not simple:
            print '        graphics ['
            print '            type "rectangle"'
            print '            w ' + str(nodeWidth)
            print '            h ' + str(nodeHeight)
            print '        ]'
        print '    ]'

    for edge in edges:
        print '    edge ['
        print '        id ' + str(edge['id'])
        print '        source ' + str(edge['source'])
        print '        target ' + str(edge['target'])
        if not simple:
            print '        graphics ['
            print '            arrow "none"'
            print '        ]'
        print '    ]'

    print ']'


def writeGraphML(simple):
    print '<?xml version="1.0" encoding="UTF-8"?>'

    print '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"'
    print '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    print '         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">'

    print '    <graph id="' + dataset + '" edgedefault="directed">'

    for node in nodes:
        if simple:
            print '        <node id="' + str(node['label']) + '"/>'
        else:
            print '        <node id="' + str(node['label']) + '">'
            print '            <port name="North"/>'
            print '            <port name="South"/>'
            print '        </node>'

    for edge in edges:
        if simple:
            print '        <edge id="' + str(edge['id']) + '" source="' + str(edge['sourceLabel']) + '" target="' + str(edge['targetLabel']) + '"/>'
        else:
            print '        <edge id="' + str(edge['id']) + '" source="' + str(edge['sourceLabel']) + '" target="' + str(edge['targetLabel']) + '" sourceport="South" targetport="North"/>'

    print '    </graph>'
    print '</graphml>'


def writeGxl(simple):
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<!DOCTYPE gxl SYSTEM "http://www.gupro.de/GXL/gxl-1.0.dtd">'

    print '<gxl xmlns:xlink=" http://www.w3.org/1999/xlink">'

    print '    <graph id="' + dataset + '" edgeids="true" edgemode="directed">'

    for node in nodes:
        print '        <node id="' + str(node['label']) + '"/>'

    for edge in edges:
        print '        <edge id="' + str(edge['id']) + '" from="' + str(edge['sourceLabel']) + '" to="' + str(edge['targetLabel']) + '"/>'

    print '    </graph>'
    print '</gxl>'


def writeTgf(simple):
    for node in nodes:
        print str(node['id'])  + ' ' + str(node['label'])
    print '#'
    for edge in edges:
            print str(edge['source'])  + ' ' + str(edge['target'])


def writeCsv(simple):
    if simple:
        for edge in edges:
            print '"' + str(edge['sourceLabel'])  + '", "' + str(edge['targetLabel']) + '"'
    else:
        for node in nodes:
            print '"node", ' + str(node['id'])  + ', "' + str(node['label']) + '"'
        for edge in edges:
            print '"edge", ' + str(edge['id'])  + ', ' + str(edge['source'])  + ', ' + str(edge['target'])


parser = argparse.ArgumentParser(description='A tool to convert legacy .LST Harris Matrix files into modern graph formats.')
parser.add_argument("-i", "--input", help="Choose input file format, optional, defaults to infile suffix", choices=['lst', 'csv'])
parser.add_argument("-g", "--graph", help="Choose output graph format, optional, defaults to outfile suffix", choices=['gv', 'dot', 'gml', 'graphml', 'gxl', 'tgf', 'csv'])
parser.add_argument("-n", "--name", help="Name for graph")
parser.add_argument("-wn", "--width", help="Width of node", type=float)
parser.add_argument("-hn", "--height", help="Height of node", type=float)
parser.add_argument("-s", "--simple", help="Only output basic node/edge data", action='store_true')
parser.add_argument('infile', help="Source .lst file", nargs='?', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('outfile', help="Destination graph file", nargs='?', type=argparse.FileType('w'), default=sys.stdout)

args = parser.parse_args()

if args.input:
    informat = args.input
elif args.infile.name != '<stdin>':
    basename, informat = os.path.splitext(args.infile.name)
    informat = informat.strip('.')
informat = informat.lower()

if args.graph:
    graph = args.graph
elif args.outfile.name != '<stdout>':
    basename, graph = os.path.splitext(args.outfile.name)
    graph = graph.strip('.')
graph = graph.lower()

if (args.width is not None and args.width > 0):
    nodeWidth = args.width
if (args.height is not None and args.height > 0):
    nodeHeight = args.height

if informat == 'csv':
    readCsv(args.infile)
else:
    readLst(args.infile)

if (args.name is not None and args.name):
    dataset = args.name

old_stdout = sys.stdout
sys.stdout = args.outfile

if (graph == 'gv' or graph == 'dot'):
    writeGv(args.simple)
elif (graph == 'graphml'):
    writeGraphML(args.simple)
elif (graph == 'gxl'):
    writeGxl(args.simple)
elif (graph == 'tgf'):
    writeTgf(args.simple)
elif (graph == 'csv'):
    writeCsv(args.simple)
else:
    writeGml(args.simple)

sys.stdout = old_stdout

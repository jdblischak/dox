#!/usr/bin/env python3

# Gathers all the counts per gene.
# usage: gather-gene-counts.py [files] > gene-counts.txt
#   e.g. gather-gene-counts.py counts/*genecounts.txt > gene-counts.txt
# Should be run from data directory.

import glob
import sys

if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    files = glob.glob("counts/*genecounts.txt")

# print(len(files))

# Create header
sys.stdout.write("individual\tflow_cell\tlane\tindex")
# Get gene names from first file
gene_list = []
f = files[0]
handle = open(f, "r")
for line in handle:
    if line[0] == "#" or line[:6] == "Geneid":
        continue
    cols = line.strip("\n").split("\t")
    gene = cols[0]
    gene_list.append(gene)
    sys.stdout.write("\t" + gene)
handle.close()
sys.stdout.write("\n")

# Process each file
for f in files:
    # Get meta data from filename
    dir, fname = f.split("/")
    fname_parts = fname.split(".")[0].split("-")
    individual, flow_cell, lane, index = fname_parts
    # Update variable names
    individual = "i" + individual

    sys.stdout.write(individual + "\t" + flow_cell + "\t" + \
                     lane + "\t" + index)

    # Get counts from f
    g = 0 # iterator for indexing gene names
    handle = open(f, "r")
    for line in handle:
        if line[0] == "#" or line[:6] == "Geneid":
            continue
        cols = line.strip("\n").split("\t")
        gene = cols[0]
        assert gene == gene_list[g], "Gene names are not in correct order in file: %s"%(f)
        g += 1
        counts = cols[6]
        sys.stdout.write("\t" + counts)
    handle.close()
    sys.stdout.write("\n")

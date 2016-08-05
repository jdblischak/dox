#!/usr/bin/env python3

# Create VCF file of phased genotypes.

# To do:
#
# * Filter by call rate
# * Filter individuals
# * What does a phasing value of 3 indicate?

import glob
import os
import pandas as pd

test = True

#work_dir = "/mnt/gluster/home/jdblischak/ober/Hutterite_phased/"

class Variant():

    def __init__(self, line):
        cols = line.strip().split("\t")
        self.id = cols[0]
        self.chr = cols[1]
        self.start = cols[2]
        self.end = cols[3]
        self.type = cols[4]
        self.ref = cols[5]
        self.alt = cols[6]
        database = cols[7].split(":")
        self.dbsnp = database[0]
        self.rsid = database[1]
        self.phase = [x[0] for x in cols[8:]]
        self.allele1 = [x[1] for x in cols[8:]]
        self.allele2 = [x[2] for x in cols[8:]]
        self.individual = ["ind" + str(i) for i in range(len(self.allele1))]
        self.qual = "."
        self.filter = "."

    def __repr__(self):
        result = """\
Contains the following SNP for %d individuals:
    ID: %s
    RSID: %s (%s)
    Location: %s:%s-%s
    Alleles (ref, alt): %s, %s
"""%(len(self.individual), self.id, self.rsid, self.dbsnp,
     self.chr, self.start, self.end, self.ref, self.alt)
        return result

    def format(self, original = False):
        variant_info = "%s\t"*8%(self.id, self.chr, self.start, self.end,
                                 self.type, self.ref, self.alt,
                                 self.dbsnp + ":" + self.rsid)
        result = variant_info
        if original:
            for i in range(len(self.allele1)):
                g = self.phase[i] + self.allele1[i] + self.allele2[i]
                result = result + g + "\t"
        else:
            for i in range(len(self.allele1)):
                g = self.view_genotype(num = i)
                result = result + g + "\t"
        # Change the final character from a tab to a newline
        result = result[:-1] + "\n"
        return result

    def view_genotype(self, num):
        if self.allele1[num] == "0":
            a1 = self.ref
        elif self.allele1[num] == "1":
            a1 = self.alt
        elif self.allele1[num] == "N":
            a1 = "."
        else:
            a1 = self.allele1[num]
        if self.allele2[num] == "0":
            a2 = self.ref
        elif self.allele2[num] == "1":
            a2 = self.alt
        elif self.allele2[num] == "N":
            a2 = "."
        else:
            a2 = self.allele2[num]
        if self.phase[num] == "1":
            p = "|"
        else:
            p = "/"
        return a1 + p + a2

    def format_vcf(self, info, format):
        variant_info = "%s\t"*9%(self.chr, self.start, self.rsid,
                                 self.ref, self.alt, self.qual, self.filter,
                                 info, format)
        result = variant_info
        for i in range(len(self.allele1)):
            if self.phase[i] == "1":
                p = "|"
            else:
                p = "/"
            if self.allele1[i] == "N":
                a1 = "."
            elif self.allele1[i] in ["0", "1"]:
                a1 = self.allele1[i]
            else:
                exit("Invalid allele 1 of variant %s: %s"%(self.rsid,
                                                           self.allele1[i]))
            if self.allele2[i] == "N":
                a2 = "."
            elif self.allele2[i] in ["0", "1"]:
                a2 = self.allele2[i]
            else:
                exit("Invalid allele 2 of variant %s: %s"%(self.rsid,
                                                           self.allele2[i]))

            g = a1 + p + a2
            result = result + g + "\t"

        # Change the final character from a tab to a newline
        result = result[:-1] + "\n"
        return result

    def call_rate(self):
        # How many individuals have gentoypes
        total = len(self.allele1)
        genotyped = 0
        for i in range(total):
            if self.allele1[i] != "N" and self.allele2[i] != "N":
                genotyped = genotyped + 1
        return genotyped / total

    def filter_individuals(self):
        pass

def write_vcf_metainfo(handle, version, date, source, reference,
                     contig, phasing):
    handle.write("##fileformat=%s\n"%(version))
    handle.write("##fileDate=%s\n"%(date))
    handle.write("##source=%s\n"%(source))
    handle.write("##reference=%s\n"%(reference))
    handle.write("##contig=%s\n"%(contig))
    handle.write("##phasing=%s\n"%(phasing))
    handle.write("##INFO=<ID=CR,Number=1,Type=Float,Description=\"Call Rate\">\n")
    handle.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")


def write_vcf_header(handle, individuals):
    handle.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT")
    for ind in individuals:
        handle.write("\t" + ind)
    handle.write("\n")

if __name__ == "__main__":
    if test:
        test_line = "7228749\tchr10\t1924784\t1924785\tsnp\tC\tT\tdbsnp.119:rs9888007\t301\t100\t111\t100\t111\t110\t101\t1NN\n"
        x = Variant(test_line)
        assert x.format(original = True) == test_line, \
            "Formatting corrupted in object storage"
        print(x)
        outfile = open("test.vcf", "w")
        write_vcf_metainfo(handle = outfile, version = "VCFv4.2",
                           date = "20160627", source = "CGI",
                           reference = "hg19", contig = "chr10",
                           phasing = "partial")
        write_vcf_header(handle = outfile, individuals = x.individual)
        outfile.write(x.format_vcf(info = "CR=%f"%(x.call_rate()), format = "GT"))
        outfile.close()

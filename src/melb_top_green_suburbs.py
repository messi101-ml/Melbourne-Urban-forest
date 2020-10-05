import pandas as pd
import json
import re
import string
import time
import csv

# shapely
from shapely.geometry import asShape
from shapely.ops import unary_union
from shapely.geometry import Polygon
import shapely.wkt
from shapely import wkb 
from shapely import wkt
# read both JSON and green text files 
# Convert to list of polygons
# For each polygon suburb calculate intersection area with green polygon area
# Add to the green area

start_time = time.time()
suburbsInput ='melb_inner_2016.json'
greenInputfilenames = ['part-00000', 'part-00001','part-00002','part-00003','part-00004','part-00005']
# suburbsInput ='two_suburbs.json'
# greenInputfilenames = ['two_lines.txt']
output_filename = "finalsa1_with_green_areas.csv"
# suburbsInput ='melb_inner_2016.json'
# greenInputfilenames = ['part-00000.txt', 'part-00001.txt','part-00002.txt','part-00003.txt','part-00004.txt','part-00005.txt']



# to replace every 2nd occurence with , so that it can be converted to polygon
def polystr_to_polygon(s, sub, repl):
    find = s.find(sub)
    # loop util we find no match
    i = 1
    while find != -1:
        if  (i - 1)/2  == (i - 1)//2 and i != 1 :
            s = s[:find]+repl+s[find + len(sub):]
        find = s.find(sub, find + len(sub) + 1)
        i += 1
    poly = shapely.wkt.loads(s)
    return poly

def read_melbourn_suburb_file(suburbsInput):
    jsonpdf = pd.read_csv(suburbsInput,sep= "}{",header=None)
    jsonpdf.columns = ['jsonstring']
    return jsonpdf

def return_polygons_list(jsonpdf):
    sa1 = list()
    for index, row in jsonpdf.iterrows():
        jsonline =''
        salStartPos =''
        sa1EndPos = ''
        coordStartPos = ''
        coordEndPos = ''
        jsonline = row['jsonstring']  
        sa1StartPos = re.search("\"sa1_7dig16\"\:",jsonline)
        sa1EndPos = sa1StartPos.start() + 14
        sa1.append(jsonline[sa1EndPos:sa1EndPos+7])
        coordStartPos = re.search("\"coordinates\"\:",jsonline)
        coordEndPos = coordStartPos.start() + 14
        coords = jsonline[coordEndPos:]
        modcds = []
        modcds = coords.replace("[[[[", "(").replace("]]]]", ")").replace("]", ")").replace("[", "(").replace("}}","")
        l = eval( "[%s]"%modcds)
        poly = Polygon(l)
        sa1.append(poly)
        sa1.append(round(poly.area * 10000,3))
    return sa1   

def read_green_areas(inputfile):
    greenjsonpdf = pd.read_csv(inputfile,sep= "\"",header=None)
    greenjsonpdf.columns = ['area','greenpolygon','field1']
    return greenjsonpdf


def main():
    
    sub = " "
    repl= ","
    fullGreenPolygons = list()

    # read suburbs file
    jsonpdf = read_melbourn_suburb_file(suburbsInput)

    # get polygon list of suburbs
    sa1 = return_polygons_list(jsonpdf)

    # iterate through mulitple input green area files
    for inputfilename in greenInputfilenames:
        fullgreenpdf = read_green_areas(inputfilename)
    # iterate through pdf to create polygon list        
        for index, row in fullgreenpdf.iterrows():
            polyline =''
            polyline = row['greenpolygon'].replace("\"","")
            greenpoly = polystr_to_polygon(polyline, " ", ",") 
            fullGreenPolygons.append(greenpoly)

    # print(len(fullGreenPolygons))
    # print(type(fullGreenPolygons))

    # Now iterate through SA1 list of polygons of suburbs with green areas of polygons
    # find the insterect area and append to total green area of the suburb(sa1)

    sa1index=0
    sa1polyindex= 1
    sa1areaindex= 2
    colindex =0
    finalsa1 = list()

    for sa1_row in sa1:
        if sa1index == colindex:
            finalsa1.append(sa1[sa1index])  
            sa1index += 3
        if sa1polyindex == colindex:
            intersectarea = 0  
            for greenpoly in fullGreenPolygons:  
                instersectpoly =sa1[sa1polyindex].intersection(greenpoly)
                if instersectpoly.area > 0:
    #                 print('test')
#                     print(instersectpoly.area)
                    intersectarea = round(intersectarea + (instersectpoly.area* 10000),10)
            sa1polyindex += 3
            finalsa1.append(sa1[sa1areaindex])
        if sa1areaindex == colindex:
            finalsa1.append(intersectarea)  
            sa1areaindex += 3    
        colindex +=1   
        
# write to outputfile
    outF = open(output_filename, "w")
    outF.write('SA1,Area,Green Area\n')
    i = 0
    filestring = ''
    for finalsal_row in finalsa1:
        if i ==0:
            filestring = str(finalsal_row)
        if i > 0:
            filestring = filestring + ',' + str(finalsal_row)
        i +=1
        if i == 3:
            filestring += '\n'
#             print(filestring)
            outF.write(filestring)
            i=0
            filestring = ''
    outF.close()       
    calc_time = time.time() - start_time
    print('Calculation time:', round(calc_time / 60, 2), 'min')
if __name__ == "__main__":
    main()
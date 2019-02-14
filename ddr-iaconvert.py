#! /usr/bin/env python
#
# ddr-iaconvert.py
# Creates CSV for batch upload to ia using cli tool
#  

description = """Converts DDR csv metadata into IA's cli upload csv format."""

epilog = """
This command converts DDR metadata into a CSV file formatted for use with Internet 
Archive's (IA) command-line upload tool (https://github.com/jjjake/internetarchive). 
The command examines a given directory of DDR binary files and associated metadata 
CSV file that has been exported from the DDR system.
EXAMPLE
     $ ddr-iaconvert ./ddr-densho-1-entities.csv ./ddr-densho-1-files.csv
"""

"""
entities:
id,status,public,title,description,creation,location,creators,language,genre,
format,extent,contributor,alternate_id,digitize_person, digitize_organization,
digitize_date,credit,topics,persons,facility,chronology,geography,parent,
rights,rights_statement,notes,sort,signature_id

files:
id,external,role,basename_orig,mimetype,public,rights,sort,thumb,label,
digitize_person,tech_notes,external_urls,links,sha1,sha256,md5,size
"""

import argparse
import sys, shutil, os
import datetime
import csv 
import converters

def load_data(csvpath,data):
    csvfile = open(csvpath, 'rb')
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        data.append(row)
    return data

def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def generate_link_text(parentid,segnumber,totalsegs):
    prefix = parentid + '-'
    if totalsegs == '1':
        nextid = None
        previd = None
    elif segnumber == '1':
        previd = None
        nextid = prefix + str(int(segnumber) + 1)
    elif int(segnumber) < int(totalsegs):
        nextid = prefix + str(int(segnumber) + 1)
        previd = prefix + str(int(segnumber) - 1)
    else:
        nextid = None
        previd = prefix + str(int(segnumber) - 1)
        
    if nextid:
        nextlink = '[ <a href=\"https://archive.org/details/' + nextid + '\">Next segment</a> ]'
    else:
        nextlink = ''

    if previd:
        prevlink = '[ <a href=\"https://archive.org/details/' + previd + '\">Previous segment</a> ]'
    else:
        prevlink = ''

    if prevlink != '' and nextlink != '':
        nextlink = "  --  " + nextlink
        
    return prevlink + nextlink


# Main
def parseCreators(rawcreators):
    creators = {}
    for kv in rawcreators.split(';'):
        namepart
    return creators

def getCollection(isSegment,id):
    if isSegment:
        collection = id[:id.rfind('-')]
    else:
        collection = 'Densho'
    return collection

def getMediaType(mimetype):
    mediatypemap = {
        'video': 'movies',
        'audio': 'audio',
        'image': 'image', 
        'application': 'texts', #get pdfs
        'text': 'texts'
    }
    return mediatypemap.get(mimetype.split('/')[0])

def getDescription(isSegment,identifier,descrip,location,creators,sort):
    description = ''
    if isSegment:
        totalsegs = ''
        sequenceinfo = 'Segment ' + segno + ' of ' + totalsegs
        linktext = generate_link_text(collection,segno,totalsegs)
    denshoboilerplate = "See this item in the <a href=\"https://ddr.densho.org/\" target=\"blank\">Densho Digital Repository</a> at: <a href=\"https://ddr.densho.org/" + identifier  + "/\" target=\"_blank\">https://ddr.densho.org/" + identifier + '/</a>.'
    description = 'Interview location: ' + location + '<p>' + descrip +'<p>' + sequenceinfo + '<p>' + linktext + '<p>' + denshoboilerplate
 
    return description
    
def getCredits(personnel):
    credits = ''

    return credits

def getLicense(code):
    licenseurl =''
    if code == 'cc':
        licenseurl = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'
    return licenseurl



def doConvert(entcsv,filecsv):
    entdata = []
    load_data(entcsv,entdata)
    filedata = []
    load_data(filecsv,filedata)
    
    print('entdata length: {}'.format(str(len(entdata))))
    print('filedata length: {}'.format(str(len(filedata))))
    
    entities_by_ddrid = build_dict(entdata,key="id")
    
    #iterate through files
    for f in filedata:
        if f['external'] == '1':
            if f['id'] in entities_by_ddrid:
                ent = entities_by_ddrid[f['id']]
                identifier = ent['id']
                creators_parsed = {}
                isSegment = True if ent['format'] == 'vh' else False
                if isSegment:
                    parentid = entities_by_ddrid[f['id'][:f['id']]]
                    creators_parsed = parseCreators(ent['creators'])
                filename = '{}-{}-{}{}'.format(ent['id'],f['role'],f['sha1'][:10],f['basename_orig'][f['basename_orig'].rfind('.'):])
                collection = getCollection(isSegment,ent['id'])
                mediatype = getMediaType(f['mimetype'])
                description = getDescription(isSegment, ent['id'],ent['description'],ent['location'],creators_parsed,ent['sort'])
                title = ent['title']
                contributor = ent['contributor']
                creator = ''
                date = ent['creation']
                subject0 = 'Japanese Americans'
                subject1 = 'Oral history'
                subject2 = ''
                licenseurl = getLicense(ent['rights'])
                credits = getCredits(ent['creators'])
                runtime = ent['extent']
                
                print('Results: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(identifier,filename,collection,mediatype,description,title,contributor,creator,date,subject0,subject1,subject2,licenseurl,credits,runtime))
    return

def main():

    parser = argparse.ArgumentParser(description=description, epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('entitycsv', help='Absolute path to DDR entities csv file.')
    parser.add_argument('filecsv', help='Absolute path to DDR files csv file.')

    args = parser.parse_args()
    print('Entity csv path: {}'.format(args.entitycsv))
    print('File csv path: {}'.format(args.filecsv))
    
    started = datetime.datetime.now()
    inputerrs = ''
    if not os.path.isfile(args.entitycsv):
        inputerrs + 'Entities csv does not exist: {}\n'.format(args.entitycsv)
    if not os.path.isfile(args.filecsv):
        inputerrs + 'Files csv does not exist: {}'.format(args.filecsv)
    if inputerrs != '':
        print('Error -- script exiting...\n{}'.format(inputerrs))
    else:
        doConvert(args.entitycsv,args.filecsv)
    
    finished = datetime.datetime.now()
    elapsed = finished - started
    
    print('Started: {}'.format(started))
    print('Finished: {}'.format(finished))
    print('Elapsed: {}'.format(elapsed))
    
    return

if __name__ == '__main__':
    main()

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
    csvfile = open(csvpath, 'r')
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
    creators = converters.text_to_rolepeople(rawcreators)
    return creators

def getMediaType(mimetype):
    mediatypemap = {
        'video': 'movies',
        'audio': 'audio',
        'image': 'image', 
        'application': 'texts', #get pdfs
        'text': 'texts'
    }
    return mediatypemap.get(mimetype.split('/')[0])

def getDescription(isSegment,identifier,descrip,location,segnum,totalsegs):
    description = ''
    sequenceinfo = ''
    if isSegment:
        sequenceinfo = 'Segment {} of {}<p>{}<p>'.format(segnum,str(totalsegs),generate_link_text(identifier[:identifier.rfind('-')],segnum,totalsegs))
    locationinfo = 'Interview location: {}'.format(location) if isSegment else 'Location: {}'.format(location)
    denshoboilerplate = 'See this item in the <a href=\"https://ddr.densho.org/\" target=\"blank\" rel=\"nofollow\">Densho Digital Repository</a> at: <a href=\"https://ddr.densho.org/{}/\" target=\"_blank\" rel=\"nofollow\">https://ddr.densho.org/{}/</a>.'.format(identifier,identifier)
    description = locationinfo + descrip +'<p>' + sequenceinfo + denshoboilerplate
 
    return description

def getCreators(creatorsdata):
    creators = ''
    for i, c in enumerate(creatorsdata):
        creators += '{}: {}{}'.format(c['role'].capitalize(),c['namepart'],'' if i == (len(creatorsdata) - 1) else ', ')
    return creators

def getCredits(personnel):
    credits = ''
    for i, c in enumerate(personnel):
        credits += '{}: {}{}'.format(c['role'].capitalize(),c['namepart'],'' if i == (len(personnel) - 1) else ', ')
    return credits

def getLicense(code):
    if code == 'cc':
        licenseurl = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'
    elif code == 'pdm':
        licenseurl = 'http://creativecommons.org/publicdomain/mark/1.0/'
    else:
        licenseurl =''

    return licenseurl

def getFirstFacility(rawfacilities):
    facility = ''
    facilitydata = converters.text_to_listofdicts(rawfacilities)
    if facilitydata:
        facility = facilitydata[0]['term']
    return facility


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
                interviewid = ''
                creators_parsed = parseCreators(ent['creators'])
                totalsegs = 0
                isSegment = True if ent['format'] == 'vh' else False
                if isSegment:
                    #get the interview id
                    interviewid = entities_by_ddrid[f['id'][:f['id'].rfind('-')]]
                    #get segment info
                    for s in entities_by_ddrid:
                        if s.key.startsWith(interviewid):
                            totalsegs +=1
                    
                filename = '{}-{}-{}{}'.format(ent['id'],f['role'],f['sha1'][:10],f['basename_orig'][f['basename_orig'].rfind('.'):])
                #note this is the IA collection bucket; not the DDR collection
                collection = interviewid if isSegment else 'Densho'
                mediatype = getMediaType(f['mimetype'])
                description = getDescription(isSegment, ent['id'],ent['description'],ent['location'],ent['sort'],totalsegs)
                title = ent['title']
                contributor = ent['contributor']
                creator = getCreators(creators_parsed)
                date = ent['creation']
                subject0 = 'Japanese Americans'
                subject1 = 'Oral history'
                #if entity has facility, get the first one
                subject2 = getFirstFacility(ent['facility'])
                licenseurl = getLicense(ent['rights'])
                credits = getCredits(creators_parsed)
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

#! /usr/bin/env python

#########################################################
                
##NOAA weather data extract
##  M Boldin  Sept 2014 -- Dec 2014

## Extracts gz with daily data from ftp://ftp.ncdc.noaa.gov/pub/data/gsod/ 
## Converts to csv file with columns
#          "Station", "Year", "Month", "Day", 
#          "MeanTemp", "NTempObs", "DewPoint", "NDewPointObs", 
#          "SeaLevelPressure", "NSeaLevPressObs", "StationPressure", 
#          "NStatPressObs", "Visibility", "NVisibilityObs", "MeanWindSpeed", 
#          "NWindObs", "MaxSustWindSpeed", "MaxWindGust", "MaxTemp",  
#          "MaxTempSource", "MinTemp", "MinTempSource", "PrecipAmount", 
#          "NPrecipReportHours", "PrecipFlag", "SnowDepth", "Fog", "Rain", 
#          "Snow", "Hail", "Thunder", "Tornado" 

##   based on download and parse functions 
##    written by Eldan Goldenberg, Sep-Oct 2012
##    http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com
                
##    Need USAF &  WBAN codes
##      "ftp://ftp.ncdc.noaa.gov/pub/data/inventories/ISH-HISTORY.TXT )\n")            
                
## Dec 2014  
##   x--tested Station find & Download using USAF-WBAN codes
##   x--next check parse of csv 
##   --each year 30 seconds approx
##   --skipped SJU San Juan PR
##             HNL Honolulu,
##             FLL Ft Lauderdaile problem acodes[20]
##             DEN Denver
##   x--dates for elapsed time
##   x--created airport list 2 with USAF & WBAN codes, alist2 
##   x--alist2 used in down load loop                  
               
##   ck snow depth =/ snowfall 
##   ck precip flag  = G
##    download with station letter code -->  Kxxx-122335566-344679
##    by year  ##   
##  

############################################################

import os
import sys
import datetime
from datetime import datetime as dt
import time

import gzip
import csv
import urllib

#################################################################

alist2= """
1   ATL      722190    13874 | Atlanta         GA | Hartsfield-Jackson Atlanta International
2   ORD      725300    94846 | Chicago         IL | Chicago O'Hare International            
3   LAX      722950    23174 | Los Angeles     CA | Los Angeles International               
4   DFW      722590    03927 | Dallas/Fort Worth TX | Dallas/Fort Worth International         
5   DEN      724670    03017 | Denver          CO | Denver International                    
6   JFK      744860    94789 | New York        NY | John F. Kennedy International           
7   SFO      724940    23234 | San Francisco   CA | San Francisco International             
8   CLT      723140    13881 | Charlotte       NC | Charlotte Douglas International         
9   LAS      723860    23169 | Las Vegas       NV | McCarran International                  
10  PHX      722780    23183 | Phoenix         AZ | Phoenix Sky Harbor International        
11  IAH      722430    12960 | Houston         TX | George Bush Intercontinental/Houston    
12  MIA      722020    12839 | Miami           FL | Miami International                     
13  MCO      722050    12815 | Orlando         FL | Orlando International                   
14  EWR      725020    14734 | Newark          NJ | Newark Liberty International            
15  SEA      727930    24233 | Seattle         WA | Seattle/Tacoma International            
16  MSP      726580    14922 | Minneapolis     MN | Minneapolis-St Paul International       
17  DTW      725370    94847 | Detroit         MI | Detroit Metro Wayne County              
18  PHL      724080    13739 | Philadelphia    PA | Philadelphia International              
19  BOS      725090    14739 | Boston          MA | Logan International                     
20  LGA      725030    14732 | New York        NY | LaGuardia                               
21  FLL      722025    12849 | Fort Lauderdale FL | Fort Lauderdale-Hollywood International 
22  BWI      724060    93721 | Baltimore       MD | Baltimore/Washington International Thurgood Marshall
23  IAD      724030    93738 | Washington      DC | Washington Dulles International         
24  SLC      725720    24127 | Salt Lake City  UT | Salt Lake City International            
25  DCA      724050    13743 | Washington      DC | Ronald Reagan Washington National       
26  MDW      725340    14819 | Chicago         IL | Chicago Midway International            
27  HNL      725340    14819 | Honolulu        HI | Honolulu International                  
28  SAN      722900    23188 | San Diego       CA | San Diego International                 
29  TPA      722110    12842 | Tampa           FL | Tampa International                     
30  PDX      726980    24229 | Portland        OR | Portland International                  
31  STL      724340    13994 | St. Louis       MO | Lambert-St. Louis International         
32  HOU      722435    12918 | Houston         TX | William P Hobby                         
33  OAK      724930    23230 | Oakland         CA | Metropolitan Oakland International      
34  MCI      724460    03947 | Kansas City     MO | Kansas City International               
35  BNA      723270    13897 | Nashville       TN | Nashville International                 
36  AUS      722540    13904 | Austin          TX | Austin - Bergstrom International        
37  RDU      723060    13722 | Raleigh/Durham  NC | Raleigh-Durham International            
38  SNA      722977    93184 | Santa Ana       CA | John Wayne Airport-Orange County        
39  SMF      724839    93225 | Sacramento      CA | Sacramento International                
40  CLE      725240    14820 | Cleveland       OH | Cleveland-Hopkins International         
41  MSY      722310    12916 | New Orleans     LA | Louis Armstrong New Orleans International
42  SJU      722310    12916 | San Juan        PR | Luis Munoz Marin International          
43  SJC      724945    23293 | San Jose        CA | Norman Y. Mineta San Jose International 
44  SAT      722530    12921 | San Antonio     TX | San Antonio International               
45  DAL      722580    13960 | Dallas          TX | Dallas Love Field                       
46  PIT      725200    94823 | Pittsburgh      PA | Pittsburgh International                
47  MKE      726400    14839 | Milwaukee       WI | General Mitchell International          
48  RSW      722108    12894 | Fort Myers      FL | Southwest Florida International         
49  IND      724380    93819 | Indianapolis    IN | Indianapolis International              
50  MEM      723340    13893 | Memphis         TN | Memphis International
"""

## Using
# Downloader for NOAA historical weather data
# Written by Eldan Goldenberg, Sep-Oct 2012
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com

# This program is free software; you can redistribute it and/or
#        modify it under the terms of the GNU General Public License
#        as published by the Free Software Foundation; either version 2
#        of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
# The licence text is available online at:
#        http://www.gnu.org/licenses/gpl-2.0.html

# Background:
# NOAA publishes an amazing trove of historical weather data from stations all
#        over the world - http://www.ncdc.noaa.gov/cgi-bin/res40.pl - but in a rather
#        awkward format: each year is a separate folder, in which each station
#        is one file, identified by two arbitrary ref numbers. Each file is gzipped
#        text in a rather non-standard format with some inconvenient features like
#        NULL tokens varying per field, and numbers being concatenated together
#        with flags that give interpretation information:
#        ftp://ftp.ncdc.noaa.gov/pub/data/gsod/readme.txt
# This script lets the user specify a station and a number of years to download.
#        It then iterates through, downloading enough years, parsing them into a much
#        more standard CSV format read for use in (e.g.) Excel or Tableau, and
#        concatenating them into one continuous file per station.

# USE:
# Simply call this script, with the optional argument --verbose if you want
# debug output. It will prompt you for everything else it needs interactively.

# TODO short term: make it take a list of stations at the beginning, so it can
#        be left running unattended after that.
# TODO long term: replace manual USAF & WBAN code input with a lookup that lets
#        users just enter a station name, and gets the two codes from that file.
# TODO total pipedream: let user give a location, and automagically find the
#        nearest station based on lat & long.
# TODO for scraperwiki: have it load in the whole list of stations and just
#        iterate over them.

verbose = True

# I've assumed you'll want the same number of years for every station you
#        download in one session, so we ask this before going into the main loop.
maxyears = 1

# This function goes through each downloaded file line by line, and translates
#        it from NOAA's idiosyncratic format to CSV with all the fields separated
#        out rationally.
def NOAAparse(f_in, f_out, stationname):
    # Set up connections to input and output files. The CSV library also helps
    #        with reading the input file, because we can treat it as space separated
    #        with consecutive spaces being collapsed together
    reader = csv.reader(f_in, delimiter=' ', quoting=csv.QUOTE_NONE, skipinitialspace=True)
    writer = csv.writer(f_out, dialect=csv.excel)
    for row in reader:
        if (row[0] != 'STN---'):
            # If it's the header row, just skip; otherwise process
            outrow = [stationname] # the station name is not in the input file

            # skipping first 2 cols of the input file as they are the USAF & WBAN codes
            #        which we're replacing with the actual station name.

            # expanding col 3 into separate Y, M & D fields makes them easier to work
            #        with in Tableau
            outrow.append((row[2])[:4]) # first 4 digits are the year
            outrow.append((row[2])[4:6]) # next 2 are the month
            outrow.append((row[2])[-2:]) # final 2 are the day

            # now we can use a loop to get through a bunch of field pairs that all
            #        work the same:
            # MeanTemp, NTempObs, DewPoint, NDewPointObs, SeaLevelPressure,
            #        NSeaLevPressObs, StationPressure, NStatPressObs
            for i in range(3, 11, 2):
                # for each of these, 9999.9 means NULL, and the number of observations
                #        follows the value
                if (row[i+1] == "0") or (row[i] == "9999.9"):
                    outrow.append("NULL")
                    outrow.append(0)
                else:
                    outrow.append(row[i])
                    outrow.append(row[i+1])

            # Now the same principle for Visibility, which uses a different NULL token
            # Visibility, NVisibilityObs
            if (row[12] == "0") or (row[11] == "999.9"):
                outrow.append("NULL")
                outrow.append(0)
            else:
                outrow.append(row[11])
                outrow.append(row[12])

            # Now for wind data, which is 4 fields of which the second is the number
            #        of observations from which the other 3 values were determined
            # MeanWindSpeed, NWindObs, MaxSustWindSpeed, MaxWindGust
            if row[14] == "0":
                # if there are 0 observations, then set a bunch of nulls
                outrow.append("NULL")
                outrow.append("0")
                outrow.append("NULL")
                outrow.append("NULL")
            else:
                for i in range(13, 17, 1):
                    if row[i] == "999.9": outrow.append("NULL")
                    else: outrow.append(row[i])

            # Temp fields may or may not have a "*" appended after the number, so we
            #        handle these by first checking what the last character is:
            # "MaxTemp", "MaxTempSource", "MinTemp", "MinTempSource"
            for i in range(17, 19, 1):
                if (row[i])[-1] == "*":
                    # then the flag is present, indicating the source was derived
                    #        indirectly from hourly data
                    outrow.append((row[i])[:-1])
                    outrow.append("hourly")
                else:
                    # if it's not present then this was an explicit max/min reading
                    outrow.append(row[i])
                    outrow.append("explicit")

            # Precipitation has its own extra special flag source and NULL placeholder
            # PrecipAmount, NPrecipReportHours, PrecipFlag
            if row[19] == "99.99":
                # then it's null, so:
                outrow.append("NULL")
                outrow.append("NULL")
                outrow.append("NULL")
            else:
                outrow.append((row[19])[:-1])
                # translations of the flag, as per
                #        ftp://ftp.ncdc.noaa.gov/pub/data/gsod/readme.txt
                if (row[19])[-1] == "A": outrow.append("6")
                elif (row[19])[-1] == "B": outrow.append("12")
                elif (row[19])[-1] == "C": outrow.append("18")
                elif (row[19])[-1] == "D": outrow.append("24")
                elif (row[19])[-1] == "E": outrow.append("12")
                elif (row[19])[-1] == "F": outrow.append("24")
                elif (row[19])[-1] == "G": outrow.append("24")
                elif (row[19])[-1] == "H": outrow.append("0")
                elif (row[19])[-1] == "I": outrow.append("0")
                else: outrow.append("ERR")
                outrow.append((row[19])[-1])

            # SnowDepth is relatively straightforward
            if row[20] == "999.9":
                outrow.append("NULL")
            else:
                outrow.append(row[20])

            # Fog, Rain, Snow, Hail, Thunder, Tornado
            # these are stored as one six-bit binary string, so we unpack it here
            for i in range(0, 6, 1):
                outrow.append((row[21])[i])

            # And we're done!  Now write the row to the output file
            writer.writerow(outrow)

    sys.stdout.flush() # need to flush the output buffer to show progress live


# This is the main control function. Each pass gets the user's input to pick a
#        station, and then loops over years to download the relevant files, calling
#        parsefile() to parse each one into standard CSV
def NOAAdownload(code1, code2, scode=None, year1=None, year2=None):
    # get parameters for and start constructing filenames
    URLroot = "ftp://ftp.ncdc.noaa.gov/pub/data/gsod/" # base URL for all files
    filesuffix = ".op.gz" # suffix for all the raw files
    firstyear = 1928 # this is the first year available for any station
    USAFcode = code1
    WBANcode = code2
    #stationname = code1 + code2
    stationcode = str(USAFcode) + '-' + str(WBANcode)
    stationname = stationcode
    if scode:
        stationname = scode + '-' + stationcode

    if year2==None:
        year2= datetime.datetime.now().year
    if year1==None:
        year1= year2
    maxyears= year2-year1+1
    print stationname, year1, year2
    yearsdownloaded = 0

    fn_out= stationname + '-' + str(year1) + '-' + str(year2) + '.csv'

    for year in range(year1, year2+1, 1):
        # start before the current year (it is incomplete)
        # looping back from prior year to year.
        #print "Year: %s" % year
        
        # First assemble the URL for the year of interest
        fullURL = (URLroot + str(year) + '/' + stationcode + '-' +
            str(year) + filesuffix)
        if verbose:
            print "Trying %s  -- %s " % (year, fullURL)

        # Now we try to download the file, with very basic error handling if verbose
        try:
            urllib.urlretrieve(fullURL,str(year)+filesuffix)
            print "   ... retrieved ",
            yearsdownloaded += 1
        except IOError as e:
            print(e)
        else: # if we got the file without any errors, then
            # uncompress the file
            f_in = gzip.open(str(year)+filesuffix)
            if verbose: 
                print " ... decompressed ... ",
            # and start writing the output
            if yearsdownloaded == 1:
                # since it's the first year, open the file and write the header row
                firstyear = year
                f_out = open(fn_out,'w')
                hx= [ "Station", "Year", "Month", "Day", \
                      "MeanTemp", "NTempObs", "DewPoint", "NDewPointObs", \
                      "SeaLevelPressure", "NSeaLevPressObs", "StationPressure", \
                      "NStatPressObs", "Visibility", "NVisibilityObs", "MeanWindSpeed", \
                      "NWindObs", "MaxSustWindSpeed", "MaxWindGust", "MaxTemp",  \
                      "MaxTempSource", "MinTemp", "MinTempSource", "PrecipAmount", \
                      "NPrecipReportHours", "PrecipFlag", "SnowDepth", "Fog", "Rain", \
                      "Snow", "Hail", "Thunder", "Tornado" ]
                csv.writer(f_out).writerow(hx)
            
            # This function does the actual ETL
            NOAAparse(f_in, f_out, stationname)

            if verbose:
                print "parsed."
            
            # clean up after ourselves
            f_in.close()
            os.remove(str(year)+filesuffix)
        
        urllib.urlcleanup()
        
        if yearsdownloaded == maxyears:
            break # if we have enough years, then end this loop
        else:
            time.sleep(5) # slow down here to stop the server locking us out
        
        time.sleep(1)
    
    if yearsdownloaded < maxyears:
        # If we didn't get as many years as requested, alert the user
        print("No more years are available at the NOAA website for this station.")
    print("Successfully downloaded " + str(yearsdownloaded) + " years between " +
           str(year) + " and " + str(firstyear) + " for station " + stationname)
        
    f_out.close()
    print 'Wrote output to %s'  % fn_out

############################################
# Extra

# Make list of stations
def NOAAstations(fname) :
    f1 = open(fname,'r')
    stations=[]
    for line in csv.reader(f1,delimiter=',', quotechar='"'):
        stations.append(line)
    f1.close()
    stations= stations[1:]    
    return stations
    '"USAF","WBAN","STATION NAME","CTRY","FIPS","STATE","CALL","LAT","LON","ELEV(.1M)","BEGIN","END"\n'

###############################################
                
if __name__ == '__main__' :

    print 'NOAA weather station data downloader'
    print dt.now()
    print 40*'*'
            
    ##Download loop2

    ## Pull out airport codes
    alist2b=alist2.split("\n") 
    for ax1 in alist2b[:2]:  # 1-4, 6-20, 21-31, 33-43
        if ax1:
            print
            dt1= dt.now()
            ax2=ax1.split("|")
            #print ax2
            scodes2= ax2[0].split()
            (jj, scall, usaf, wban)= scodes2
            if scall not in ('HNL', 'SJU', 'DEN', 'FLL', 'HOU'):
                print scodes2, ax2[-1]  
                year1= 2014
                year2= 2014
                NOAAdownload(usaf, wban, scall, year1, year2)
            dt2= dt.now()
            print '%s  | %s  seconds: %-4s' % (dt2.strftime('%Y-%m-%d %H:%M:%S'), (dt2-dt1), (dt2-dt1).seconds )

    print ' ... DONE'
    print dt.now()
    print 40*'*'


    station = str(scall) + '-' + str(usaf) + '-' + str(wban)
    #year1=2013
    #year2=2014
    fn2= station + '-' + str(year1) + '-' + str(year2) + '.csv'
    
    print 'Reading %s' % fn2
    fx2 = open(fn2)
    dx=[]   
    for line in csv.reader(fx2, delimiter=',', quotechar='"'):
        if (not line[0]=='Station' and not line[0]==''): 
            dx.append(line)
    fx2.close()
    hx= [ "Station", "Year", "Month", "Day", \
          "MeanTemp", "NTempObs", "DewPoint", "NDewPointObs", \
          "SeaLevelPressure", "NSeaLevPressObs", "StationPressure", \
          "NStatPressObs", "Visibility", "NVisibilityObs", "MeanWindSpeed", \
          "NWindObs", "MaxSustWindSpeed", "MaxWindGust", "MaxTemp",  \
          "MaxTempSource", "MinTemp", "MinTempSource", "PrecipAmount", \
          "NPrecipReportHours", "PrecipFlag", "SnowDepth", "Fog", "Rain", \
          "Snow", "Hail", "Thunder", "Tornado" ]
    #hx2 = tuple(hx[0:4]) + ("Date",) + (hx[4],hx[20],hx[18], hx[22], hx[25]) + (hx[24], hx[27], hx[28])
    print 'Station      Year Month Day    Date  MeanT   MinT   MaxT Precip  SnowD --Flags Precip Rain Snow'
    for rx in dx:
        #print dx
        #dtx= dt.date(int(rx[1]), int(rx[2]), int(rx[3]))
        #if (dtx >= dt.date(2013,12,1)) and (dtx <= dt.date(2014,2,28)):         
        px = tuple(rx[0:4]) + (dtx,) + (rx[4],rx[20],rx[18], rx[22], rx[25]) + (rx[24], rx[27], rx[28])
        print '%10s %4s %2s %3s %10s %6s %6s %6s %6s %6s -- %1s %1s %1s' % px

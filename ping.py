#!/usr/bin/env python
# import stuff
import urllib, re, calendar, time
# misc prep
now = time.gmtime() # set year to this year; needed for baseTime
baseTime = calendar.timegm((int(time.strftime("%Y", now)),1,1,0,0,0,0,0,0))
nowTime = calendar.timegm((int(time.strftime("%Y", now)), int(time.strftime("%m", now)), int(time.strftime("%d", now)), int(time.strftime("%H", now)), int(time.strftime("%M", now)),0,0, 0,0))
ptypeLst = ["Hail","Test","None","Rain","Drizzle","Freezing Rain","Freezing Drizzle","Rain/Snow","Rain/Ice Pellets","Ice Pellets/Snow","Snow","Wet Snow","Ice Pellets","Graupel"]
### Step 1: Process the raw data ###############################################
# open PING homepage
raw = urllib.urlopen("http://www.nssl.noaa.gov/projects/ping/display/ping.php")
# remove top junk
daynum, timenum, lat, lon, ptype = [], [], [], [], []
rawtimenum = []
hailmag = []
print("Processing data...")

for line in raw:
    if line[:2] == 'pr': # ptype report
        match = re.search('\[(.+?)\]\=\[(.+?)\,(.+?)\,(.+?)\,(.+?)\]',line)
        if match:
            daynum.append(match.group(1))
            rawtimenum.append(int(match.group(2)))
            timenum.append(time.strftime("%m/%d/%Y %H:%M UTC", time.gmtime(baseTime + (int(match.group(2))*60))))
            lat.append(match.group(3))
            lon.append(match.group(4))
            ptype.append(match.group(5))
            hailmag.append('-999') # placeholder
    elif line[:2] == 'hr': # hail report
        match = re.search('\[(.+?)\]\=\[(.+?)\,(.+?)\,(.+?)\,(.+?)\]',line)
        if match:
            daynum.append(match.group(1))
            rawtimenum.append(int(match.group(2)))
            timenum.append(time.strftime("%m/%d/%Y %H:%M UTC", time.gmtime(baseTime + (int(match.group(2))*60))))
            lat.append(match.group(3))
            lon.append(match.group(4))
            hailmag.append(match.group(5))
            ptype.append('0')
print("::: Done processing PING data ")

# post-processing to grab latest x hours
minTime = min(rawtimenum)
maxTime = max(rawtimenum)
nowMinutes = (nowTime - baseTime) / 60
times = {}
times[15] = nowMinutes - 15
times[30] = nowMinutes - 30
times[60] = nowMinutes - 60
### Step 2: Create the placefile ##################################################
for t in times.keys():
    # open placefile to write
    f = open('ping-' + str(t) + 'min.txt', 'w')
    # write basic header stuff for placefile
    f.write('Title: Latest ' + str(t) + 'min PING reports\n')
    f.write('Refresh: 5\n') # refresh time in minutes
    f.write('Color: 255 255 255\n') # default color to be used
    f.write('IconFile: 1, 15, 15, 8, 8, "http://gr.wxjoe.com/i/pingIcons.png"\n')
    # fileNum, width, height, hotX, hotY, fileName
    f.write('Font: 1, 11, 1, "Courier New"\n') # whatever
    message = "; Created by Joe Moore \n; Generated at " + time.strftime("%x %X %Z") + "\n; Found " + str(len(daynum)) + " total reports\n; Made with Python!\n; Public Domain"
    f.write(message + '\n\n')
    reports = 0
    # Now let's write the actual data!
    for i in range(len(daynum)):
        if rawtimenum[i] > times[t]:
            reports += 1
            f.write('Object: ' + lat[i] + ', ' + lon[i] + '\n')
            # Everything else must have a tab! I think!
            f.write('Threshold: 999\n') # Display at any zoom level (?)
            if ptype[i] == '0': # if hail
                f.write(' Icon: 0, 0, 000, 1, ' + str(int(ptype[i])+1) + ', "Time: ' + timenum[i] + '\\nPtype: ' + ptypeLst[int(ptype[i])] + '\\nHail Size: ' + str(float(hailmag[i])/4.) + ' inches"\n')
                f.write(' Text: 0, -15, 1, "' + str(float(hailmag[i])/4.) + '" "\n')
            else: # else, any other ptype
                f.write(' Icon: 0, 0, 000, 1, ' + str(int(ptype[i])+1) + ', "Time: ' + timenum[i] + '\\nPtype: ' + ptypeLst[int(ptype[i])] + '"\n')
            f.write('End:\n\n')

    f.write('; Plotted ' + str(reports) + ' reports')
    f.close()
    print("::: Done writing Placefile")

##log = open('reportCount.txt', 'a')
##log.write(time.strftime("%x %X %Z") + ' ' + str(reports) + '\n')
##log.close()


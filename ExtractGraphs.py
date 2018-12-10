# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 08:22:15 2018

@author: s267636
"""
import time
import lmfit
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os
import fnmatch
import datetime
import git
 
plt.close('all')

#%%  Set Variables For Each Run

book='2' ## Where is the description of this experiment in James Bremner'
page='7' ## Lab Book?

pattern = '*consolidated_data.csv' #This sets the file ending is for the data to be plotted

dirpath= 'Z:\\Data\\Book'+str(book)+'\\b' +str(book) +'p' # possible location of files

plotcutoff=200 #How many data points are cut from the beinning and end of the data so that the flyback noise is ignored
alloweddeviation=4 #How many standard deviations away from the mean we call an "outlier"
numberoftubes=3 #How many gas cells are multiplexed?

colour1='#377eb8'
colour2='#e41a1c'
colour3='#4daf4a'
#%%
rootPath = dirpath + page



print rootPath

#Set up empty variables to store data
Collated_Normalised_Absorption=pd.DataFrame()
List_of_filenames = []
residuals1=pd.DataFrame([])
residuals2=pd.DataFrame([])
residuals3=pd.DataFrame([])
wrapped1=pd.DataFrame([])
wrapped2=pd.DataFrame([])
wrapped3=pd.DataFrame([])
averaged1=pd.DataFrame([])
averaged2=pd.DataFrame([])
averaged3=pd.DataFrame([])
normalised1=pd.DataFrame([])
normalised2=pd.DataFrame([])
normalised3=pd.DataFrame([])

#%%

def Translation(inputlist,runnumber=40): #The data comes into the system in the wrong shape, this just fixes that
    inputlist=inputlist.T
    inputlist.columns=[range(runnumber)]
    inputlist=np.array(inputlist)
    return(inputlist)


def ApplyPlotStyle(TubeNumber,yAxisTitle='Light Intensity (a.u)'): #The style for the plots
    ax.set_ylabel(yAxisTitle)
    ax.set_xlabel('Time (s)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.title.set_text('Tube Number ' +str(TubeNumber))
    

#%% This takes in the Intensity Data from the consolidated data file and stores it as a bunch of dataframes
    
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
        dirlist = ( os.path.join(root, filename))
        with open(dirlist, 'r') as f:
            #print filename
            runnumber=int(filename[7:-21])
            
            my_csv=pd.read_csv(f)
            filewrapped1=my_csv['Wrapped Intensity 1'].dropna()
            filewrapped2=my_csv['Wrapped Intensity 2'].dropna()
            filewrapped3=my_csv['Wrapped Intensity 3'].dropna()
            
            fileaveraged1=my_csv['Averaged Intensity 1'].dropna()
            fileaveraged2=my_csv['Averaged Intensity 2'].dropna()
            fileaveraged3=my_csv['Averaged Intensity 3'].dropna()
            
            fileresiduals1=my_csv['Residuals Tube 1'].dropna()
            fileresiduals2=my_csv['Residuals Tube 2'].dropna()
            fileresiduals3=my_csv['Residuals Tube 3'].dropna()
            
            I01=my_csv['Fitted Tube 1'].dropna()
            I02=my_csv['Fitted Tube 2'].dropna()
            I03=my_csv['Fitted Tube 3'].dropna()
            
            fileNormalisedAbsorption1=pd.Series(fileresiduals1/I01)
            fileNormalisedAbsorption2=pd.Series(fileresiduals2/I02)
            fileNormalisedAbsorption3=pd.Series(fileresiduals3/I03)
            
            averaged1=averaged1.append(fileaveraged1)
            averaged2=averaged2.append(fileaveraged2)
            averaged3=averaged3.append(fileaveraged3)
            
            wrapped1=wrapped1.append(filewrapped1)
            wrapped2=wrapped2.append(filewrapped2)
            wrapped3=wrapped3.append(filewrapped3)
            
            residuals1=residuals1.append(fileresiduals1)
            residuals2=residuals2.append(fileresiduals2)
            residuals3=residuals3.append(fileresiduals3)
            
            fileNormalisedAbsorption1=fileNormalisedAbsorption1.rename('Normalised Tube 1')
            fileNormalisedAbsorption2=fileNormalisedAbsorption2.rename('Normalised Tube 2')
            fileNormalisedAbsorption3=fileNormalisedAbsorption3.rename('Normalised Tube 3')
            
            #fileNormalisedAbsorption2.columns=['Normalised 2']
            
            normalised1=normalised1.append(fileNormalisedAbsorption1)
            normalised2=normalised2.append(fileNormalisedAbsorption2)
            normalised3=normalised3.append(fileNormalisedAbsorption3)
            

            timesignal1=my_csv['Time[s]']
            print runnumber

#runnumber=runnumber-1 #This is because a file is missing     
            

#%% Just tidies the data gathered from all of the files into the right shape.
(residuals1,residuals2,residuals3)=map(Translation,(residuals1,residuals2,residuals3),(runnumber,runnumber,runnumber))
(wrapped1,wrapped2,wrapped3)=map(Translation,(wrapped1,wrapped2,wrapped3),(runnumber,runnumber,runnumber))
(normalised1,normalised2,normalised3)=map(Translation,(normalised1,normalised2,normalised3),(runnumber,runnumber,runnumber))
(averaged1,averaged2,averaged3)=map(Translation,(averaged1,averaged2,averaged3),(runnumber,runnumber,runnumber))


z=len(wrapped1)
timesignal=timesignal1[0:z]
timesignal.rename('Time')
timesignal=np.array(timesignal)


 
#%% This tests each run and if it lays too far from the mean (set by a number of standard deviations from that mean) and creates
#    a new dataframe without these outliers

wrappedmean1=wrapped1.mean(axis=1)
wrappedstd1=wrapped1.std(axis=1)
wrappedmean2=wrapped2.mean(axis=1)
wrappedstd2=wrapped2.std(axis=1)
wrappedmean3=wrapped3.mean(axis=1)
wrappedstd3=wrapped3.std(axis=1)



columntodelete1=[]
columntodelete2=[]
columntodelete3=[]

for column in range(0,runnumber): #This block compares the value at each point in each intensity plot 
                                    #to the average of all the intensity plots at that point
                                    #And notes the ones ones that are outliers as defined by the user
    for row in range(plotcutoff,len(timesignal)-plotcutoff):
  
        if wrapped1[row,column]>(wrappedmean1[row] + alloweddeviation*wrappedstd1[row]):
            columntodelete1.append(column)
        if wrapped1[row,column]<(wrappedmean1[row] - alloweddeviation*wrappedstd1[row]):
            columntodelete1.append(column)
        if wrapped2[row,column]>(wrappedmean2[row] + alloweddeviation*wrappedstd2[row]):
            columntodelete2.append(column)
        if wrapped2[row,column]<(wrappedmean2[row] - alloweddeviation*wrappedstd2[row]):
            columntodelete2.append(column)
        if wrapped3[row,column]>(wrappedmean3[row] + alloweddeviation*wrappedstd3[row]):
            columntodelete3.append(column)
        if wrapped3[row,column]<(wrappedmean3[row] - alloweddeviation*wrappedstd3[row]):
            columntodelete3.append(column)


columntodelete1=list(set(columntodelete1))
columntodelete2=list(set(columntodelete2))
columntodelete3=list(set(columntodelete3))

#This block creates a new dataframe with just the nonoutliers for each gas cell
(wrappedcleaned1,wrappedcleaned2,wrappedcleaned3)=np.delete((wrapped1,wrapped2,wrapped3),[columntodelete1],axis=1)
(residualscleaned1,residualscleaned2,residualscleaned3)=np.delete((residuals1,residuals2,residuals3),[columntodelete1],axis=1)
(normalisedcleaned1,normalisedcleaned2,normalisedcleaned3)=np.delete((normalised1,normalised2,normalised3),[columntodelete1],axis=1)

allrows=range (1,runnumber+1)
cleanrows1=list(set(allrows)-set(columntodelete1))
cleanrows2=list(set(allrows)-set(columntodelete2))
cleanrows3=list(set(allrows)-set(columntodelete3))

#%% Creates the filename and file location for the new images
dummypicturename='Z:\\Images\\Book BOOKNO\\bBOOKNOpPAGENO\\bBOOKNOpPAGENOThreeTubesSlopesAllData.svg'
fixed_filename=dummypicturename.replace('BOOKNO', str(book))  
fixed_filename=fixed_filename.replace('PAGENO', str(page))
 
imagedirectory='Z:\\Images\\Book '+str(book)+'\\b' +str(book) +'p'+page+ '\\' 
if not os.path.exists(imagedirectory):
            os.makedirs(imagedirectory)


#%% Gathers the list of graphs to make along with the Title, and y-axis label for each



fullplotlist=[[wrapped1,wrapped2,wrapped3],[wrappedcleaned1,wrappedcleaned2,wrappedcleaned3],[normalised1,normalised2,normalised3]]
TitlesList=('Intensities','Cleaned Up Intensities','Normalised Absorption')
yAxisList=('Light Intensity (a.u)','Light Intensity (a.u)','Normalised Absorption (a.u)')

#%% 

for variable in range(len(fullplotlist)):
    fig=plt.figure(figsize=(10,12))
    plt.subplots_adjust(hspace=0.3)
    #fig.suptitle('Intensities', fontsize=24)
    fig.suptitle('Book ' + book + ' Page ' + page + ' ' + TitlesList[variable], fontsize=12)

    for tube in range(0,numberoftubes):
        ax=fig.add_subplot(numberoftubes,1,tube+1)
    
        ax.plot(timesignal[plotcutoff:-plotcutoff],fullplotlist[variable][tube][:][plotcutoff:-plotcutoff], color=colour1)
        ax.plot(timesignal[plotcutoff:-plotcutoff],fullplotlist[variable][tube][:][plotcutoff:-plotcutoff].mean(axis=1), color='black')
        #ax.plot(timesignal[plotcutoff:-plotcutoff],(plotlist[1][:][plotcutoff:-plotcutoff] + alloweddeviation*wrappedstd1[plotcutoff:-plotcutoff]))
        #ax.plot(timesignal[plotcutoff:-plotcutoff],(plotlist[1][:][plotcutoff:-plotcutoff] - alloweddeviation*wrappedstd1[plotcutoff:-plotcutoff]))
        ApplyPlotStyle(tube+1,yAxisList[variable])
    cleanedupfilename=fixed_filename.replace('ThreeTubesSlopesAllData','ThreeSlopes'+TitlesList[variable])
    fig.savefig(cleanedupfilename)
    
fig=plt.figure(figsize=(10,12))
ax=ax=fig.add_subplot(111)
ax.plot(timesignal[plotcutoff:-plotcutoff],normalised1[:][plotcutoff:-plotcutoff].mean(axis=1), color=colour1,linestyle=':', label='Tube 1')
ax.plot(timesignal[plotcutoff:-plotcutoff],normalised2[:][plotcutoff:-plotcutoff].mean(axis=1), color=colour2, linestyle='-.', label='Tube 2')
ax.plot(timesignal[plotcutoff:-plotcutoff],normalised3[:][plotcutoff:-plotcutoff].mean(axis=1), color=colour3, linestyle='--', label='Tube 3')
ApplyPlotStyle('All Tubes','NormalisedAbsorption (a.u)')
ax.title.set_text('Normalised Absorption')
ax.legend()

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha


readme='Date of creation: ' +str(datetime.datetime.today().strftime('%Y-%m-%d')) +'\nGit Hash of Software Used: ' +str(sha) + '\nNumber of data points ignored at each end of run: ' +str(plotcutoff) + '\nNumber of Standard Deviations from mean which denotes an outlier: ' + str(alloweddeviation) + '\nNumber of Runs: '+ str(runnumber) + '\nIgnored Runs Tube 1: ' +str(columntodelete1) +'\nIgnored Runs Tube 2: ' +str(columntodelete2) +'\nIgnored Runs Tube 3: ' +str(columntodelete3)
print readme
textfilename=fixed_filename.replace('ThreeTubesSlopesAllData.svg','readme.txt')

with open(textfilename, "w") as text_file:
    text_file.write(readme)
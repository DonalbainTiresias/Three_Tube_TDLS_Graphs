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

plt.close('all')
book='2'
page='7'
pattern = '*consolidated_data.csv' 
#dirpath='C:\\Users\\JamesBremner\\Desktop\\b2p'
dirpath= 'Z:\\Data\\Book'+str(book)+'\\b' +str(book) +'p'
rootPath = dirpath + page
plotcutoff=200
alloweddeviation=4 #How many standard deviations away from the mean we call an "outlier"
numberoftubes=3

imagedirectory='Z:\\Images\\Book '+str(book)+'\\b' +str(book) +'p'+page+ '\\' 
if not os.path.exists(imagedirectory):
            os.makedirs(imagedirectory)


print rootPath

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


def Translation(inputlist,runnumber=40):
    inputlist=inputlist.T
    inputlist.columns=[range(runnumber)]
    inputlist=np.array(inputlist)
    return(inputlist)


def ApplyPlotStyle(TubeNumber,yAxisTitle='Light Intensity (a.u)'):
    ax.set_ylabel(yAxisTitle)
    ax.set_xlabel('Time (s)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.title.set_text('Tube Number ' +str(TubeNumber))
    

#my_csv=pd.read_csv('Z:\\Data\\Book1\\b1p199\\b1p199_00034\\Amp\\b1p199_00034_amplitude.csv', header=0)
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
            


(residuals1,residuals2,residuals3)=map(Translation,(residuals1,residuals2,residuals3),(runnumber,runnumber,runnumber))
(wrapped1,wrapped2,wrapped3)=map(Translation,(wrapped1,wrapped2,wrapped3),(runnumber,runnumber,runnumber))
(normalised1,normalised2,normalised3)=map(Translation,(normalised1,normalised2,normalised3),(runnumber,runnumber,runnumber))
(averaged1,averaged2,averaged3)=map(Translation,(averaged1,averaged2,averaged3),(runnumber,runnumber,runnumber))


z=len(wrapped1)
timesignal=timesignal1[0:z]
timesignal.rename('Time')
timesignal=np.array(timesignal)


 


wrappedmean1=wrapped1.mean(axis=1)
wrappedstd1=wrapped1.std(axis=1)
wrappedmean2=wrapped2.mean(axis=1)
wrappedstd2=wrapped2.std(axis=1)
wrappedmean3=wrapped3.mean(axis=1)
wrappedstd3=wrapped3.std(axis=1)



columntodelete1=[]
columntodelete2=[]
columntodelete3=[]

for column in range(0,runnumber-1):
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

cleanedupwrapped1=np.delete(wrapped1,[columntodelete1],axis=1)
residualscleaned1=np.delete(residuals1,[columntodelete1],axis=1)

columntodelete2=list(set(columntodelete2))
cleanedupwrapped2=np.delete(wrapped2,[columntodelete2],axis=1)
residualscleaned2=np.delete(residuals2,[columntodelete2],axis=1)

columntodelete3=list(set(columntodelete3))
cleanedupwrapped3=np.delete(wrapped3,[columntodelete3],axis=1)
residualscleaned3=np.delete(residuals3,[columntodelete3],axis=1)

dummypicturename='Z:\\Images\\Book BOOKNO\\bBOOKNOpPAGENO\\bBOOKNOpPAGENOThreeTubesSlopesAllData.svg'
fixed_filename=dummypicturename.replace('BOOKNO', str(book))  
fixed_filename=fixed_filename.replace('PAGENO', str(page))
 







fullplotlist=[[wrapped1,wrapped2,wrapped3],[cleanedupwrapped1,cleanedupwrapped2,cleanedupwrapped3],[normalised1,normalised2,normalised3]]
TitlesList=('Intensities','Cleaned Up Intensities','Normalised Absorption')
yAxisList=('Light Intensity (a.u)','Light Intensity (a.u)','Normalised Absorption (a.u)')

for variable in range(len(fullplotlist)):
    fig=plt.figure(figsize=(10,12))
    plt.subplots_adjust(hspace=0.3)
    #fig.suptitle('Intensities', fontsize=24)
    fig.suptitle('Book ' + book + ' Page ' + page + ' ' + TitlesList[variable], fontsize=12)

    for tube in range(0,numberoftubes):
        ax=fig.add_subplot(numberoftubes,1,tube+1)
    
        ax.plot(timesignal[plotcutoff:-plotcutoff],fullplotlist[variable][tube][:][plotcutoff:-plotcutoff], color='#bebada')
        ax.plot(timesignal[plotcutoff:-plotcutoff],fullplotlist[variable][tube][:][plotcutoff:-plotcutoff].mean(axis=1), color='black')
        #ax.plot(timesignal[plotcutoff:-plotcutoff],(plotlist[1][:][plotcutoff:-plotcutoff] + alloweddeviation*wrappedstd1[plotcutoff:-plotcutoff]))
        #ax.plot(timesignal[plotcutoff:-plotcutoff],(plotlist[1][:][plotcutoff:-plotcutoff] - alloweddeviation*wrappedstd1[plotcutoff:-plotcutoff]))
        
        ApplyPlotStyle(tube+1,yAxisList[variable])
    cleanedupfilename=fixed_filename.replace('ThreeTubesSlopesAllData','ThreeTubes'+TitlesList[variable])
    fig.savefig(cleanedupfilename)
    
fig=plt.figure(figsize=(10,12))

ax=ax=fig.add_subplot(1,1,1)
ax.plot(timesignal[plotcutoff:-plotcutoff],normalised1[:][plotcutoff:-plotcutoff].mean(axis=1), color='#e41a1c', linestyle=':', label='Tube 1')
ax.plot(timesignal[plotcutoff:-plotcutoff],normalised2[:][plotcutoff:-plotcutoff].mean(axis=1), color='#377eb8', linestyle='-', label='Tube 2')
ax.plot(timesignal[plotcutoff:-plotcutoff],normalised3[:][plotcutoff:-plotcutoff].mean(axis=1), color='#4daf4a', linestyle='--', label='Tube 3')
ax.legend()
ax.set_ylabel('Normalised Absorption (a.u)')
ax.set_xlabel('Time (s)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.title.set_text('b' +str(book) + 'p' + str(page) + ' All Tubes Normalised Absorption')
cleanedupfilename=fixed_filename.replace('ThreeTubesSlopesAllData','ThreeTubesNormalisedAbsorption')
fig.savefig(cleanedupfilename)


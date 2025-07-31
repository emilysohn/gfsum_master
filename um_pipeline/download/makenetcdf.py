#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concatenates cubes from UM output pp files into netcdf files. Not parallelised, slow and memory-intensive
Base code developed by Hamish Gordon,Jesus Vergara Temprado and Kirsty Pringle
Additions to customize script for HALOsouth developed by Eric Giuffrida
h.gordon@leeds.ac.uk
eejvt@leeds.ac.uk
K.Pringle@leeds.ac.uk
egiuffri@andrew.cmu.edu

Aerosol modellers group
Institute for climate and atmospheric science (ICAS)
University of Leeds 2016

Center for Atmospheric Particle Studies (CAPS)
Carnegie Mellon Universtiy 2025
"""

import sys
import numpy as np
import time
import iris
from glob import glob
import datetime
from scipy.io import netcdf
import os
import pandas as pd

def lat_range(cell):
   return (latbottom < cell < lattop)


def height_level_range(cell):
    return cell in [0,2,5,6,9,11,13,15,16,17,18,20,24,26,29,33,35,37,41,46]


def make_directories(newdir):
    try:
        os.makedirs(newdir, exist_ok=True)
        print(f"Created or already exists: {newdir}")
    except Exception as e:
        print(f"❌ Error creating directory {newdir}: {e}")
        raise
    return f"Created Folder: {newdir}"



def save_small_nc_files(bigarray, ncfolder, stashcode, timepointslist):
    print('Begin Saving')
    print('Save Location: {}'.format(ncfolder))
    i=0
    for j in range(0,len(bigarray)):
        for cube in bigarray[j]:
            #print cube
            saving_name = ncfolder+'glm_'+stashcode+'_'+str(timepointslist[i])+'.nc'
            print ('saving',saving_name)
            iris.save(cube, saving_name, netcdf_format="NETCDF4")
            i=i+1
    return('Saving Complete')


def concatenate_nc_files(smallncfolder, bigncfolder, stashcode):
    print('Begin Concatenation')
    print('Save Location: {}'.format(bigncfolder))
    cubes = iris.load(smallncfolder+'*'+stashcode+'*.nc')

    print(cubes)
    cube = cubes[0]
    print(cube)
    time_array = cube.coord('time').points
    print('Concatenated {} files'.format(len(time_array)))
    saving_name = bigncfolder+'glm_'+cube.name()+'_'+stashcode+'.nc'
    iris.save(cube,saving_name, netcdf_format="NETCDF4")
    print('File {} Saved'.format(saving_name))
    print('\n')


def delete_smallnc(smallncfolder, stashcode):
    stashfiles = sorted(glob(smallncfolder+'*'+stashcode+'*'))
    for stashfile in stashfiles:
        os.remove(stashfile)
    print('Deleted {} small nc files for stash {}'.format(len(stashfiles), stashcode))


def main(stashcode, cycle):
    latconstr = iris.Constraint(latitude=lat_range)
    #model_lev_constr = iris.Constraint(model_level_number=height_level_range)

    rose = 'u-dq502'
    files_directory_UKCA = '/jet/home/earhg/cylc-run/'+rose+'/share/cycle/'
    iday=cycle   #current cycle as MM-DD
    print (iday)
    print (stashcode)
    filechunks = ['pa','pb','pc','pd','pe']

    files_directory=files_directory_UKCA+'2025'+iday+'T0000Z/glm/um/' 
    pp_files1=[sorted(glob(files_directory+'*gl*'+chunk+'*')) for chunk in filechunks]
    if iday == '0601': 
        pp_files = pp_files1 #for no overlap
    else:
        pp_files = pp_files1 #for no overlap
    #pp_files = [pp_files1[0][8:], pp_files1[1][8:], pp_files1[2][8:]] #for 24 hour overlap
    #pp_files = [pp_files1[0][16:], pp_files1[1][16:], pp_files1[2][16:]] #for 48 hour overlap
    
    rosefolder = '/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/'+rose+'/'
    smallncfolder = rosefolder+'temp_folder/'
    bigncfolder = rosefolder+cycle+'/'
    
    stashconstr = iris.AttributeConstraint(STASH=stashcode)
    cubes=iris.load((pp_files[0])[0],stashconstr)
    print ('loading cubes '+str(pp_files[0][0]))
    if len(pp_files) > 1:
        for filelist in pp_files[1:]:
            print ('loading cubes '+str(filelist[0]))
            cubel = iris.load(filelist[0],stashconstr)
            for cube1 in cubel:
                cubes.append(cube1)
    coord_names = [coord.name() for coord in cubes[0].coords()]
    
    print (cubes)
    print(coord_names)
    print(cubes[0].coord('time').points)
    tacc3hr = 0

    bigarray=[]
    timepointslist=[]
    print('Begin Cube Data Processing')

    for cube in cubes:
        cl = iris.cube.CubeList()
    
        #Remove unwanted dimensions
        cube.remove_coord('forecast_reference_time')
        altitude_factories = [f for f in cube.aux_factories if f.standard_name == 'altitude']
        for f in altitude_factories:
            cube.remove_aux_factory(f)        
        try:
            cube.remove_coord('surface_altitude')
        except Exception:
            pass
        try:
            cube.remove_coord('altitude')
        except Exception:
            pass
        if 'ukmo__process_flags' in cube.attributes:
            del cube.attributes['ukmo__process_flags']      
        if tacc3hr==1:
            print (cube.coord('time').points)
            print (cube.coord('time').bounds)
            cube.coord('time').bounds = None
            iris.util.promote_aux_coord_to_dim_coord(cube,'time')
        
        #Select (lat,lon) region of interest (not needed for HALO simulations)
        #cubelat = cube.intersection(longitude=(-60,45.5))
        #cube = cubelat.extract(latconstr)

        #Select desired model levels if stash has altitude coordinate
        #try:
        #    cube = cube.extract(model_lev_constr) 
        #except Exception:
        #    pass
        
        #Add cube and their indv times to a list
        timepointslist.append(cube.coord('time').points)
        time = cube.coord('time')
        dates = time.units.num2date(time.points)
        if len(dates) > 1:
            for sub_cube in cube.slices_over('time'):
                print(sub_cube)
                cl.append(sub_cube)
        else:
            cl.append(cube)
        bigarray.append(cl)
    
    print(bigarray)
    print(timepointslist)
    
    if any(len(files) > 1 for files in pp_files):
        n_steps = max(len(files) for files in pp_files)

        for fileindex in range(1, n_steps):
            morecubes = []

            for chunk_files in pp_files:
                if fileindex < len(chunk_files):
                    step_file = chunk_files[fileindex]
                    print ('loading cubes ' + str(step_file))
                    chunk_cubes = iris.load(step_file, stashconstr)
                    morecubes.extend(chunk_cubes)
            i = 0  # Reset cube index for bigarray
    
            for cube in morecubes:
                print (cube.coord('time').points)
                #print cube
                #print cube.ndim
                for j in timepointslist[i]:
                    it=0
                    for k in cube.coord('time').points:
                        if k ==j:
                            print ('removing',j)
                            if it==0:
                                cube = cube[1:,...]
                            elif it==1 and len(cube.coord('time').points)==2:
                                cube = cube[0:1,...]
                            else:
                                raise ValueError('Overlapping fudged removal failure')
                            print (cube)
                        it=it+1

                #Remove unwanted dimensions
                cube.remove_coord('forecast_reference_time')
                altitude_factories = [f for f in cube.aux_factories if f.standard_name == 'altitude']
                for f in altitude_factories:
                    cube.remove_aux_factory(f)
                try:
                    cube.remove_coord('surface_altitude')
                except Exception:
                    pass
                try:
                    cube.remove_coord('altitude')
                except Exception:
                    pass
                if 'ukmo__process_flags' in cube.attributes:
                    del cube.attributes['ukmo__process_flags']
                if tacc3hr==1:
                    cube.coord('time').bounds=None
                    iris.util.promote_aux_coord_to_dim_coord(cube,'time')
                #cubelat = cube.intersection(longitude=(-60,45.5))
                #cube =cubelat.extract(latconstr)
                
                #Select desired model levels if stash has altitude coordinate
                #try:
                #    cube = cube.extract(model_lev_constr)
                #except Exception:
                #    pass

                #Add cube and their indv times to the list
                if cube.name() ==(bigarray[i])[0].name() and cube.attributes['STASH']==(bigarray[i])[0].attributes['STASH']:
                    if len(cube.coord('time').points) >1:
                        for sub_cube in cube.slices_over('time'):
                            bigarray[i].append(sub_cube)
                    else:
                        bigarray[i].append(cube)
                else:
                    for cubelist in bigarray:
                        if cube.name() ==cubelist[0].name() and cube.attributes['STASH']==cubelist[0].attributes['STASH']:
                            if len(cube.coord('time').points) >1:
                                for sub_cube in cube.slices_over('time'):
                                    bigarray[i].append(sub_cube)
                            else:
                                cubelist.append(cube)
                            break
                for j in cube.coord('time').points:
                    array=timepointslist[i]
                    print(j)
                    timepointslist[i] = np.append(array,j)
                i=i+1
            print (timepointslist)
            fileindex=fileindex+1
    
    #print(bigarray)
    #print(timepointslist)
    #print(np.shape(bigarray))
    #print(np.shape(timepointslist))
    #print(bigarray[0][-1])

    make_directories(rosefolder)
    make_directories(smallncfolder)
    make_directories(bigncfolder)
    save_small_nc_files(bigarray, smallncfolder, stashcode, timepointslist[0])
    concatenate_nc_files(smallncfolder, bigncfolder, stashcode)
    delete_smallnc(smallncfolder, stashcode)
    return()


stash = str(sys.argv[1])
cycle = str(sys.argv[2])
main(stash, cycle)
sys.exit()






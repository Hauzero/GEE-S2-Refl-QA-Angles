#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 16:41:11 2019

@author: leon  (HAUZERO)
"""
import numpy as np
import pandas as pd
import ee

### authenticate GEE ###
ee.Initialize()

## Define region of interest ### 
p1 = ee.Geometry.Point([-1.1571388888888887,7.3265278]);

### Define timeframe or interesting ###
collection = ee.ImageCollection('COPERNICUS/S2_SR').filterDate('2018-01-01','2018-12-31').filterBounds(p1)

### Get information ###

collectionList = collection.toList(collection.size())
collectionSize = collectionList.size().getInfo()
ft = ee.FeatureCollection(ee.List([]))
for i in xrange(collectionSize): 
      img = ee.Image(collectionList.get(i))
      ft2 = img.reduceRegions(p1, ee.Reducer.first(),100)
      fdf = ft2.getInfo()
      cx, cy = fdf['features'][0]['geometry']['coordinates']
      date = img.date().format()
      anglezen = img.get('MEAN_SOLAR_ZENITH_ANGLE'); 
      angleazi = img.get('MEAN_SOLAR_AZIMUTH_ANGLE'); 
      viewzen = img.get('MEAN_INCIDENCE_ZENITH_ANGLE_B3'); 
      viewazi = img.get('MEAN_INCIDENCE_AZIMUTH_ANGLE_B3');
      ab = pd.Series(fdf['features'][0]['properties'])
      if i == 0:
          fdf2 = pd.DataFrame(columns=fdf['columns'])
          fdf2['date'] = date.getInfo()
          fdf2['VIEW_AZIMUTH'] = viewazi.getInfo()
          fdf2['VIEW_ZENITH'] = viewzen.getInfo()
          fdf2['SUN_ZENITH'] = anglezen.getInfo()
          fdf2['SUN_AZIMUTH'] = angleazi.getInfo()
          fdf2['.xgeo'] = (cx)
          fdf2['.ygeo'] = (cy)
      fdf2 = fdf2.append(ab, ignore_index=True)
      fdf2['date'][i] = date.getInfo()
      fdf2['VIEW_AZIMUTH'][i] = viewazi.getInfo()
      fdf2['VIEW_ZENITH'][i] = viewzen.getInfo()
      fdf2['SUN_ZENITH'][i] = anglezen.getInfo()
      fdf2['SUN_AZIMUTH'][i] = angleazi.getInfo()
      fdf2['.xgeo'][i] = (cx)
      fdf2['.ygeo'][i] = (cy)
      
      
rawin = fdf2
bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']

### create text file from the collected data ### 

filepath = '/data-input/'
long, lat = p1.getInfo()['coordinates']
dataout = np.array([])


rho_unc = np.zeros((len(bands)))
rho_unc[rho_unc == 0] = 0.010

#### SHAPE/ORDER OF TEXT FILE TO BE CREATED :: #####
    #    DoY QA QA_PASS SZA SAA VZA VAA RHO_B1 RHO_B2 RHO_B3 RHO_B4 RHO_B5 RHO_B6 RHO_B7
    #   doy qa qa_pass sza saa vza vaa rho_b1 rho_b2 rho_b3 rho_b4 rho_b5 rho_b6 rho_b7

print len(rawin)

for ix in range(len(rawin)):
    rho = np.array([])
    date = rawin['date'][ix].replace('T','-').split('-')
    newday = pd.Timestamp(year=int(date[0]), month=1, day=1)
    date = pd.Timestamp(year=int(date[0]), month=int(date[1]), day=int(date[2]))
    doy = (date - newday).days + 1
    qa = 0
    
    ## SCL == 4 for vegetation
    qa_pass = rawin['SCL'][ix]
    sza = rawin['SUN_ZENITH'][ix]
    saa = rawin['SUN_AZIMUTH'][ix]
    vza = rawin['VIEW_ZENITH'][ix]
    vaa = rawin['VIEW_AZIMUTH'][ix]
    
    
    meta = np.array([doy, qa, qa_pass, sza, saa, vza, vaa])

    for ib in bands:
        rho = np.append(rho,rawin[ib][ix]*0.0001)
                 
    if  qa_pass == 4: 
        print meta, rho, rho_unc
        
        filename =  'long' + str(float("{0:.6f}".format(long))) + 'lat' + str(float("{0:.6f}".format(lat))) + 'year'  + str(date.year) + '.txt'
        filedir = filepath + filename        
        pixrow = np.concatenate((meta, rho, rho_unc))
        #    dataout = np.vstack((dataout,pixrow))
        
        with open(filedir,'a') as f_handle:
                    np.savetxt(f_handle, pixrow, fmt='%.3f',delimiter=' ', newline = ' ')      



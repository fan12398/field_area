# -*- coding: utf-8 -*-

import numpy as np
from cv2 import cv2
import sys
import log
import logging

#log = log.Log(__name__, file_level=logging.WARN, console_level=logging.INFO).getlog()

def getCropMask(color, depth, mid):
    
    lower_g = np.array([mid-40,mid-40,mid-40])
    upper_g = np.array([mid+40,mid+40,mid+40])
    mask = cv2.inRange(color, lower_g, upper_g)
    '''
    hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    lower_g = np.array([mid-10,0,30])
    upper_g = np.array([mid+10,255,255])
    mask = cv2.inRange(hsv, lower_g, upper_g)
    '''
    mask = cv2.medianBlur(mask, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    ''' 去除掩模小的连通域 '''
    if(cv2.__version__[0] == '4'):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boundaries = []
    for con in contours:
        if(cv2.contourArea(con) > 1000):
            boundaries.append(con)
            cv2.drawContours(mask, [con], 0, 255, -1)
        else:
            cv2.drawContours(mask, [con], 0, 0, -1)
    
    ''' 将掩模与深度做与运算 '''
    depth_bin = np.uint8(depth>0)*255
    mask = cv2.bitwise_and(mask, depth_bin)
    return(mask)

def calculateArea(depth, mask, imu_data):
    if(np.max(mask) == 0):
        return(0)
    depth = cv2.bitwise_and(depth, depth, mask=mask)
    xyzpoints = depth2world(depth)
    if(len(xyzpoints) == 0):
        return(0)
    x_angle = (imu_data[0]-180)*np.pi/180
    y_angle = -(imu_data[1]-90)*np.pi/180
    xyzpoints = spin3D(xyzpoints, [x_angle, y_angle, 0])
    shadow = getShadowImage(xyzpoints)
    area = getShadowArea(shadow)
    return(area)

'''
@note: points格式
[[x1, y1, z1]
 [x2, y2, z2],
 ...
 [xn, yn, zn]]
@before
for i in range(points_num):
    x = depth[valid_pos[0][i], valid_pos[1][i]]
    y = (322-valid_pos[1][i])*x/408.05
    z = (241-valid_pos[0][i])*x/410.89
    points[i] = [x, y, z]
    #azim = np.arctan((322-valid_pos[1][i])/408.05)
    #elev = np.arctan((241-valid_pos[0][i])/410.89)
    #r = depth[valid_pos[0][i], valid_pos[1][i]]
    #points[i] = sph2cart(azim, elev, r)
'''
#Color 480p: [fx=408.0519104003906,fy=410.8918762207031,cx=321.9118957519531,cy=240.68490600585938]
def depth2world(depth):
    valid_pos = depth.nonzero()
    points_num = len(valid_pos[0])
    d = np.array([depth[valid_pos]]).transpose()
    B = (np.array([[241],[322]]) - np.array(valid_pos)) / np.array([[410.89], [408.05]])
    B = np.array([np.ones(points_num), B[1], B[0]]).transpose()
    points = B*d
    return(points)

def sph2cart(azimuth, elevation, r):
    x = r * np.cos(elevation) * np.cos(azimuth)
    y = r * np.cos(elevation) * np.sin(azimuth)
    z = r * np.sin(elevation)
    return(x, y, z)

def spin3D(points, spin_angles):
    spin_x = np.array([[1, 0, 0],
                       [0, np.cos(spin_angles[0]), -np.sin(spin_angles[0])],
                       [0, np.sin(spin_angles[0]), np.cos(spin_angles[0])]])

    spin_y = np.array([[np.cos(spin_angles[1]), 0, np.sin(spin_angles[1])],
                       [0, 1, 0],
                       [-np.sin(spin_angles[1]), 0, np.cos(spin_angles[1])]])

    spin_z = np.array([[np.cos(spin_angles[2]), -np.sin(spin_angles[2]), 0],
                       [np.sin(spin_angles[2]), np.cos(spin_angles[2]), 0],
                       [0, 0, 1]])
    spin = np.matmul(spin_z, spin_y)
    spin = np.matmul(spin, spin_x)
    points = np.transpose(points)
    points = np.matmul(spin, points)
    return(np.transpose(points))

def getShadowImage(points):
    if(sys.platform == 'win32'):
        Debug = True
    else:
        Debug=False
    ''' 得到投影图 '''
    origin = np.amin(points, 0)
    span = np.ptp(points, 0)
    height = np.int(span[0]) + 1
    width = np.int(span[1]) + 1
    shadow = np.zeros((height, width), np.uint8)

    relative_coor = points - origin
    relative_coor = relative_coor.astype(np.int)

    for p in relative_coor:
        shadow[p[0]][p[1]] = 255
    if(Debug):
        cv2.imshow('origin_shadow', shadow)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    #shadow = cv2.morphologyEx(shadow, cv2.MORPH_CLOSE, kernel)
    shadow = cv2.dilate(shadow, kernel)
    if(Debug):
        cv2.imshow('shadow1', shadow)
    
    #shadow = cv2.medianBlur(shadow, 7)
    shadow = cv2.GaussianBlur(shadow, (3,3), 1)
    if(Debug):
        cv2.imshow('shadow2', shadow)

    if(cv2.__version__[0] == '4'):
        contours, _ = cv2.findContours(shadow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        _, contours, _ = cv2.findContours(shadow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for con in contours:
        if(cv2.contourArea(con) > 500):
            cv2.drawContours(shadow, [con], 0, 255, -1)
        else:
            cv2.drawContours(shadow, [con], 0, 0, -1)        
    if(Debug):
        cv2.imshow('final_shadow', shadow)
    return(shadow)

def getShadowArea(shadow):
    area = 0
    if(cv2.__version__[0] == '4'):
        contours, _ = cv2.findContours(shadow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        _, contours, _ = cv2.findContours(shadow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for con in contours:
        con_area = cv2.contourArea(con)
        if(con_area > 500):
            area += con_area
    area = np.int(area/900)
    return(area)
    
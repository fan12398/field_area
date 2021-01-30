# -*- coding: utf-8 -*-

import numpy as np
from cv2 import cv2
import sys
import log
import logging

#log = log.Log(__name__, file_level=logging.WARN, console_level=logging.INFO).getlog()

def getRectArea_960p(depth, color, cam_param, imu_data):
    focus = (cam_param.fx + cam_param.fy) / 2
    center = np.array([cam_param.cx, cam_param.cy]).astype(np.int)
    bottom_width = 800
    top_height = 200
    bottom_height = 320

    bottomleft = np.array([-bottom_width/2, bottom_height])
    bottomright = np.array([bottom_width/2, bottom_height])

    k = 1.0
    alpha1 = k * bottom_height/focus
    alpha2 = k * top_height/focus
    #spin_angles = (np.array(imu_data) + np.array([-180,0,0]))*np.pi/180
    #integrated version
    spin_angles = (-np.array(imu_data) + np.array([-180,0,0]))*np.pi/180
    alpha = spin_angles[1]

    top_width = bottom_width * np.cos(alpha+alpha2) / np.cos(alpha-alpha1)

    topleft = np.array([-top_width/2, -top_height])
    topright = np.array([top_width/2, -top_height])
    
    points = np.array([topleft, topright, bottomright, bottomleft])
    # spin
    #points = spin2D(points, spin_angles[0])
    points = points.astype(np.int) + center
    cv2.line(color, tuple(points[0]), tuple(points[1]), (0,0,255), 4)
    cv2.line(color, tuple(points[1]), tuple(points[2]), (0,0,255), 4)
    cv2.line(color, tuple(points[2]), tuple(points[3]), (0,0,255), 4)
    cv2.line(color, tuple(points[3]), tuple(points[0]), (0,0,255), 4)

    blp = getLinePoints(tuple(points[2]), tuple(points[3]), [1280,960])
    blpy = (blp[0]/2).astype(np.int)
    blpx = (blp[1]/2).astype(np.int)
    bottom_line = depth[(blpy,blpx)]
    bottom_depth = np.median(bottom_line) / 3
    real_bw = bottom_depth * bottom_width / focus
    real_bh = bottom_depth * (top_height+bottom_height) / focus * (1/np.cos(alpha)+np.tan(alpha)*np.sin(alpha2)/np.cos(alpha+alpha2))
    
    #cv2.imshow('depth', color)
    #print(real_bw, real_bh)
    area = int(real_bh * real_bw / 100)
    return(area)

def getRectArea_480p(depth, color, cam_param, imu_data):
    focus = (cam_param.fx + cam_param.fy) / 2
    center = np.array([cam_param.cx, cam_param.cy]).astype(np.int)
    bottom_width = 400
    top_height = 100
    bottom_height = 160

    bottomleft = np.array([-bottom_width/2, bottom_height])
    bottomright = np.array([bottom_width/2, bottom_height])

    k = 1.0
    alpha1 = k * bottom_height/focus
    alpha2 = k * top_height/focus
    #spin_angles = (np.array(imu_data) + np.array([-180,0,0]))*np.pi/180
    #integrated version
    spin_angles = (-np.array(imu_data) + np.array([-180,0,0]))*np.pi/180
    alpha = spin_angles[1]

    top_width = bottom_width * np.cos(alpha+alpha2) / np.cos(alpha-alpha1)

    topleft = np.array([-top_width/2, -top_height])
    topright = np.array([top_width/2, -top_height])
    
    points = np.array([topleft, topright, bottomright, bottomleft])
    # spin
    #points = spin2D(points, spin_angles[0])
    points = points.astype(np.int) + center
    cv2.line(color, tuple(points[0]), tuple(points[1]), (0,0,255), 2)
    cv2.line(color, tuple(points[1]), tuple(points[2]), (0,0,255), 2)
    cv2.line(color, tuple(points[2]), tuple(points[3]), (0,0,255), 2)
    cv2.line(color, tuple(points[3]), tuple(points[0]), (0,0,255), 2)

    blp = getLinePoints(tuple(points[2]), tuple(points[3]), [640,480])
    bottom_line = depth[blp]
    bottom_depth = np.median(bottom_line) / 3
    real_bw = bottom_depth * bottom_width / focus
    real_bh = bottom_depth * (top_height+bottom_height) / focus * (1/np.cos(alpha)+np.tan(alpha)*np.sin(alpha2)/np.cos(alpha+alpha2))
    
    #cv2.imshow('depth', color)
    #print(real_bw, real_bh)
    area = int(real_bh * real_bw / 100)
    return(area)

''' version 1 algorithm '''
def getRectArea_480p_v1(depth, color, imu_data):
    focus = 409
    center = np.array([322, 241])
    bottom_width = 400
    top_height = 100
    bottom_height = 160

    bottomleft = np.array([-bottom_width/2, bottom_height])
    bottomright = np.array([bottom_width/2, bottom_height])

    k = 1.1
    alpha1 = k * np.arctan(bottom_height/focus)
    alpha2 = k * np.arctan(top_height/focus)
    spin_angles = (np.array(imu_data) + np.array([-180,0,0]))*np.pi/180
    alpha = -spin_angles[0]

    top_width = bottom_width * np.cos(alpha+alpha2) / np.cos(alpha-alpha1)

    topleft = np.array([-top_width/2, -top_height])
    topright = np.array([top_width/2, -top_height])
    
    points = np.array([topleft, topright, bottomright, bottomleft])
    # spin
    points = spin2D(points, spin_angles[1])
    points = points.astype(np.int) + center
    cv2.line(color, tuple(points[0]), tuple(points[1]), 65535, 2)
    cv2.line(color, tuple(points[1]), tuple(points[2]), 65535, 2)
    cv2.line(color, tuple(points[2]), tuple(points[3]), 65535, 2)
    cv2.line(color, tuple(points[3]), tuple(points[0]), 65535, 2)
    
    center_depth = depth[tuple(center)] / 3
    alpha1 = 0.4 * alpha1
    alpha2 = 1.4 * alpha2
    real_bw = center_depth * np.cos(alpha) / np.cos(alpha-alpha1) * bottom_width / focus
    real_bh = center_depth * np.cos(alpha) * (np.tan(alpha+alpha2) - np.tan(alpha-alpha1))

    cv2.imshow('depth', color)
    print(real_bw, real_bh)

    area = int(real_bh * real_bw / 100)
    return(area)


def getLinePoints(pt1, pt2, scope):
    delta_x = pt2[0] - pt1[0]
    delta_y = pt2[1] - pt1[1]
    uRow = pt1[0]
    uCol = pt1[1]

    if(delta_x > 0):
        incx = 1  #设置单步方向 
    elif(delta_x == 0):
        incx=0    #垂直线 
    else:
        incx = -1
        delta_x = -delta_x

    if(delta_y > 0):
        incy = 1
    elif(delta_y == 0):
        incy = 0  #水平线 
    else:
        incy = -1
        delta_y = -delta_y
	
    if(delta_x > delta_y):
        distance = delta_x #选取基本增量坐标轴 
    else:
        distance = delta_y
    
    xerr = 0
    yerr = 0
    xp = np.array([], dtype=np.int64)
    yp = np.array([], dtype=np.int64)
    for i in range(distance+1):
        if((0<=uRow<scope[0]) and (0<=uCol<scope[1])):
            xp = np.append(xp, uRow)
            yp = np.append(yp, uCol)
        xerr += delta_x
        yerr += delta_y
        if(xerr >= distance):
            xerr -= distance
            uRow += incx
        if(yerr >= distance):
            yerr -= distance
            uCol += incy
    return(yp, xp)

def spin2D(points, spin_angle):
    spin = np.array([[np.cos(spin_angle), np.sin(spin_angle)],
                     [-np.sin(spin_angle), np.cos(spin_angle)]])
    points = np.transpose(points)
    points = np.matmul(spin, points)
    return(np.transpose(points))


def polygonArea(vertex):
    area = 0
    vertex.append(vertex[0])
    for i in range(len(vertex)-1):
        area += vertex[i][0]*vertex[i+1][1] - vertex[i+1][0]*vertex[i][1]
    return(np.abs(area/2))

################# 投影面积计算方法 ##################################
def getCropMask(color, depth, hue):
    ''' 拿到掩模 '''
    ### H-[65 98] S-[33 255] V-[117 255] ###
    ## 原 [30,100,40]
    ##    [100,255,255]
    hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    lower_g = np.array([hue-20,33,30])
    upper_g = np.array([hue+20,255,255])
    mask = cv2.inRange(hsv, lower_g, upper_g)
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
    y_angle = (imu_data[0]-90)*np.pi/180
    x_angle = imu_data[1]*np.pi/180
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
    y = (322-valid_pos[1][i])*x/554.256
    z = (241-valid_pos[0][i])*x/579.411
    points[i] = [x, y, z]
    #azim = np.arctan((322-valid_pos[1][i])/554.256)
    #elev = np.arctan((241-valid_pos[0][i])/579.411)
    #r = depth[valid_pos[0][i], valid_pos[1][i]]
    #points[i] = sph2cart(azim, elev, r)
'''
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
    
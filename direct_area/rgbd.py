# -*- coding: utf-8 -*-
"""
Auther: Fan Tenglong
Time: 2019-03-16
"""

import logging
import time, ctypes
import numpy as np
from cv2 import cv2
from axonopenni import openni2
from axonopenni import _openni2 as c_api
import log

class RGBD_Camera(object):
    def __init__(self, loglevel=logging.WARN):
        super().__init__()
        openni2.initialize()
        openni2.DeviceListener()
        self.log = log.Log(__name__, file_level=loglevel, console_level=loglevel).getlog()

    def open(self):
        self.dev = openni2.Device.open_any()
        dev_info = self.dev.get_device_info()
        depth_info = self.dev.get_sensor_info(openni2.SENSOR_DEPTH)
        color_info = self.dev.get_sensor_info(openni2.SENSOR_COLOR)
        self.log.info("设备信息: %r" %dev_info)
        self.log.debug("Depth传感器类型：%r, 模式：%r" % (depth_info.sensorType, depth_info.videoModes))
        self.log.debug("Color传感器类型：%r, 模式：%r" % (color_info.sensorType, color_info.videoModes))
        cam_detail = self.dev.get_property(c_api.AXONLINK_DEVICE_PROPERTY_GET_CAMERA_PARAMETERS, c_api.AXonLinkCamParam)
        self.color_params = cam_detail.astColorParam
        self.log.debug("Color相机校正参数960p: %r" %self.color_params[0])
        self.log.debug("Color相机校正参数480p: %r" %self.color_params[1])
        self.flag_960p = False

    def select_ImageRegistration(self, mode=0):
        mode = int(mode)
        self.dev.is_image_registration_mode_supported(c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_DEPTH_TO_COLOR)
        result = self.dev.get_image_registration_mode()
        self.log.debug("当前图像配准模式: %r" %result)
        if(mode == 0):
            obj = c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_OFF
        elif(mode == 1):
            obj = c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_DEPTH_TO_COLOR
        elif(mode == 2):
            obj = c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_DEPTH_IR_TO_COLOR
        elif(mode == 3):
            obj = c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_COLOR_TO_DEPTH
        elif(mode == 4):
            obj = c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_COLOR_UNDISTORTION_ONLY
        else:
            self.log.error("Test ImageRegistration Mode Error！")
            return(False)

        res = self.dev.is_image_registration_mode_supported(mode)
        self.log.debug("Support Result: %r" %res)
        if res:
            try:
                c_api.oniDeviceSetProperty(self.dev._handle, c_api.ONI_DEVICE_PROPERTY_IMAGE_REGISTRATION, ctypes.byref(obj), ctypes.sizeof(obj))
                result = self.dev.get_image_registration_mode()
            except Exception as e:
                self.log.error("Test Registration Error!: %r" %e)
                return(False)
            self.log.info("设置后的图像配准模式: %r" %result)
            if(obj == result):
                return(True)
            else:
                self.log.error("图像配准设置失败")
                return(False)
        else:
            self.log.error("Is_image_registration_mode_supported Error")
            return(False)

    def set_dcsync(self):
        try:
            result = self.dev.get_depth_color_sync_enabled()
            self.log.debug("当前Depth to Color帧同步使能为: %r" %result)
            enable = self.dev.set_depth_color_sync_enabled(True)
            result2 = self.dev.get_depth_color_sync_enabled()
            self.log.info("设置帧同步后使能为: %r" %result2)
        except Exception as e:
            self.log.error("set_dcsync Error!：%r" %e)
            return(False)
        else:
            if(enable.value == 0):
                return(True)
            else:
                return(False)
    
    def set_color_960p(self):
        # videoModes[4]
        # OniVideoMode(pixelFormat = OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX = 1280, resolutionY = 960, fps = 30)
        colorvm = self.dev.get_sensor_info(openni2.SENSOR_COLOR).videoModes[4]
        self.streams[1].set_video_mode(colorvm)
        self.flag_960p = True
    
    def get_color_params(self):
        return(self.color_params)

    def get_depth_value_unit(self):
        format = self.dev.get_sensor_info(openni2.SENSOR_DEPTH).videoModes[0].pixelFormat
        unit = openni2.get_depth_value_unit(format)
        self.log.info("当前深度数据的单位为: %f mm" %unit)
        return unit

    def create_streams(self):
        dvs = self.dev.create_depth_stream()
        cvs = self.dev.create_color_stream()
        self.streams = [dvs, cvs]
        for vs in self.streams:
            vs.start()
    
    def get_streams(self):
        return(self.streams)
    
    def close_streams(self):
        if('streams' in dir(self)):
            for vs in self.streams:
                vs.stop()
                vs.close()
        else:
            self.log.warn("streams未创建, 直接关闭")

    def start_one_shot(self, ignore_cnt=0, bgr=True):
        if('streams' not in dir(self)):
            self.log.warn('streams未创建, 开始创建...')
            self.create_streams()
        frame_cnt = 0
        while(True):
            try:
                openni2.wait_for_any_stream(self.streams, 1)
            except Exception as e:
                self.log.error("wait_for_any_stream error: %r" %e)
            else:
                frame_cnt += 1
                dframe = self.streams[0].read_frame()
                cframe = self.streams[1].read_frame()
                if(dframe!=None and cframe!=None and frame_cnt>ignore_cnt):
                    break

        dframe_data = np.array(dframe.get_buffer_as_uint16()).reshape([480, 640])
        if(self.flag_960p):
            cframe_data = np.array(cframe.get_buffer_as_triplet()).reshape([960, 1280, 3])
        else:
            cframe_data = np.array(cframe.get_buffer_as_triplet()).reshape([480, 640, 3])
        if(bgr):
            cframe_data = cv2.cvtColor(cframe_data, cv2.COLOR_RGB2BGR)
        return(dframe_data, cframe_data)

    def close(self):
        self.close_streams()
        if('dev' in dir(self)):
            self.dev.close()
        openni2.unload()


if __name__ == "__main__":
    rgbd = RGBD_Camera(logging.DEBUG)
    try:
        rgbd.open()
    except Exception as e:
        print("RGBD相机打开失败: %r" %e)
        exit(0)
    
    param_960p = rgbd.get_color_params()[0]

    rgbd.create_streams()
    rgbd.set_color_960p()
    rgbd.set_dcsync()                       # 设置同步使能
    rgbd.select_ImageRegistration(1)        # 设置图像对齐模式
    depth, color = rgbd.start_one_shot(0)
    rgbd.close()
    print('depth shape', depth.shape)
    print('color shape', color.shape)
    cv2.imshow('dpt', depth)
    cv2.imshow('color', color)
    print("\n**** 按下任何按键退出程序 *****")
    cv2.waitKey(0)

    
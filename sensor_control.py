import os
import numpy as np
import cv2
import csv

from datetime import datetime as dt
from shutil import rmtree, move
from pyk4a import PyK4A

from tkinter import Tk, Label, ttk, messagebox, StringVar, BooleanVar
from tkinter import LabelFrame, Menu, DISABLED, NORMAL, LEFT

from app.user_info import UserInfo
from app.paho_mqtt import PahoMqtt
from app.utils import *


class SensorControl(Tk):

    def __init__(self, screenName=None, baseName=None,
                 useTk=1, sync=0, use=None):
        super().__init__(screenName=screenName, baseName=baseName,
                         useTk=useTk, sync=sync, use=use)

        #######################################################################
        # Attributes ----------------------------------------------------------
        self.age = ['User', 'User']
        self.sex = ['User', 'User']
        self.height = ['User', 'User']
        self.weight = ['User', 'User']
        self.is_streaming = False
        self.is_displaying = False

        self.frame_count = 0
        self.time_stamp_tmp = 0
        self.depth_frame_tmp = 0
        self.rgb_frame_tmp = 0

        self.activity = StringVar()
        self.activity1 =StringVar()
        self.sensor_ignore = BooleanVar()
        self.buffer_ignore = BooleanVar()
        self.debug_mode = BooleanVar()

        # Clients
        self.kinect_client = PahoMqtt(BROKER, "KINECT", c_msg="kinect")
        self.kinect_client.loop_start()
        self.sound_client = PahoMqtt(BROKER, "SOUND", c_msg="sound")
        self.sound_client.loop_start()
        self.clients = list()
        dis = 0
        for i, item in enumerate(SENSORS):
            if item[2]:
                self.clients.append(PahoMqtt(BROKER, f"{item[1]}",
                                             c_msg=item[0]))
                self.clients[i-dis].subscribe(item[0])
                self.clients[i-dis].loop_start()
            else:
                dis += 1

        # Attributes ----------------------------------------------------------
        #######################################################################
        # Tk widgets ----------------------------------------------------------

        self.title("Control")
        self.resizable(0, 0)
        self.configure(bg='white')

        # Sensor Frame 1
        self.sensor_frame1 = LabelFrame(self, text="Sensor control",
                                        background='white')
        self.sensor_frame1.pack(side=LEFT, fill="y")

        self.sensor_state = list()
        for item in self.clients:
            self.sensor_state.append(Label(self.sensor_frame1,
                                           text=f"SENSOR {item.info}",
                                           background='white',
                                           font=("default", 15, 'bold')))
            self.sensor_state[-1].grid(row=len(self.sensor_state),
                                       column=0)

        self.start_btn = ttk.Button(self.sensor_frame1,
                                    text="Refresh", command=self.refresh)
        self.start_btn.grid(row=len(self.clients)+1, column=0)

        # Stream Frame 2
        self.sensor_frame2 = LabelFrame(self, text="Person 1",
                                        background='white')
        self.sensor_frame2.pack(side=LEFT, fill="y")
        self.user_age = Label(self.sensor_frame2, text="Age",
                              background='white',
                              font=("default", 10, 'bold'))
        self.user_age.grid(row=0, column=0)
        self.age_label = Label(self.sensor_frame2, text=self.age[0],
                               background='white',
                               font=("default", 10, 'bold'))
        self.age_label.grid(row=0, column=1)
        self.user_sex = Label(self.sensor_frame2, text="Sex",
                              background='white',
                              font=("default", 10, 'bold'))
        self.user_sex.grid(row=1, column=0)
        self.sex_label = Label(self.sensor_frame2, text=self.sex[0],
                               background='white',
                               font=("default", 10, 'bold'))
        self.sex_label.grid(row=1, column=1)
        self.user_height = Label(self.sensor_frame2, text="Height",
                                 background='white',
                                 font=("default", 10, 'bold'))
        self.user_height.grid(row=2, column=0)
        self.height_label = Label(self.sensor_frame2, text=self.height[0],
                                  background='white',
                                  font=("default", 10, 'bold'))
        self.height_label.grid(row=2, column=1)
        self.user_weight = Label(self.sensor_frame2, text="Weight",
                                 background='white',
                                 font=("default", 10, 'bold'))
        self.user_weight.grid(row=3, column=0)
        self.weight_label = Label(self.sensor_frame2, text=self.weight[0],
                                  background='white',
                                  font=("default", 10, 'bold'))
        self.weight_label.grid(row=3, column=1)

        self.activity_menu = ttk.Combobox(self.sensor_frame2,
                                          value=ACTIVITIES,
                                          textvariable=self.activity)
        self.activity_menu.current(0)
        self.activity_menu.config(state="readonly", width=15)
        self.activity_menu.bind("<<ComboboxSelected>>")
        self.activity_menu.grid(row=4, column=0, columnspan=2, pady=5)

        self.stream_start_btn = ttk.Button(self.sensor_frame2,
                                           text="Stream start",
                                           command=self.stream_start,
                                           width=11)
        self.stream_start_btn.grid(row=5, column=0, padx=2, pady=2)
        self.stream_stop_btn = ttk.Button(self.sensor_frame2,
                                          text="Stream stop",
                                          command=self.stream_stop,
                                          width=11)
        self.stream_stop_btn["state"] = DISABLED
        self.stream_stop_btn.grid(row=5, column=1, padx=2, pady=2)

        self.stream_reset_btn = ttk.Button(self.sensor_frame2,
                                           text="Stream reset",
                                           command=lambda:
                                               self.stream_reset(delete=True),
                                           width=11)
        self.stream_reset_btn["state"] = DISABLED
        self.stream_reset_btn.grid(row=7, column=1, padx=2, pady=2)

        self.stream_save_btn = ttk.Button(self.sensor_frame2,
                                          text="Stream save",
                                          command=self.stream_save,
                                          width=11)
        self.stream_save_btn["state"] = DISABLED
        self.stream_save_btn.grid(row=7, column=0, padx=2, pady=2)

        self.act_start_btn = ttk.Button(self.sensor_frame2,
                                        text="Activity start",
                                        command=lambda: self.activity_start(0),
                                        width=11)
        self.act_start_btn["state"] = DISABLED
        self.act_start_btn.grid(row=6, column=0, padx=2, pady=5)

        self.act_end_btn = ttk.Button(self.sensor_frame2,
                                      text="Activity end",
                                      command=lambda: self.activity_end(0),
                                      width=11)
        self.act_end_btn["state"] = DISABLED
        self.act_end_btn.grid(row=6, column=1, padx=2, pady=5)

        ###################################################################################
        # Stream Frame 3
        self.sensor_frame3 = LabelFrame(self, text="Person 2",
                                        background='white')
        self.sensor_frame3.pack(side=LEFT, fill="y")
        self.user1_age = Label(self.sensor_frame3, text="Age",
                              background='white',
                              font=("default", 10, 'bold'))
        self.user1_age.grid(row=0, column=0)
        self.age1_label = Label(self.sensor_frame3, text=self.age[1],
                               background='white',
                               font=("default", 10, 'bold'))
        self.age1_label.grid(row=0, column=1)
        self.user1_sex = Label(self.sensor_frame3, text="Sex",
                              background='white',
                              font=("default", 10, 'bold'))
        self.user1_sex.grid(row=1, column=0)
        self.sex1_label = Label(self.sensor_frame3, text=self.sex[1],
                               background='white',
                               font=("default", 10, 'bold'))
        self.sex1_label.grid(row=1, column=1)
        self.user1_height = Label(self.sensor_frame3, text="Height",
                                  background='white',
                                  font=("default", 10, 'bold'))
        self.user1_height.grid(row=2, column=0)
        self.height1_label = Label(self.sensor_frame3, text=self.height[1],
                                   background='white',
                                   font=("default", 10, 'bold'))
        self.height1_label.grid(row=2, column=1)
        self.user1_weight = Label(self.sensor_frame3, text="Weight",
                                 background='white',
                                 font=("default", 10, 'bold'))
        self.user1_weight.grid(row=3, column=0)
        self.weight1_label = Label(self.sensor_frame3, text=self.weight[1],
                                  background='white',
                                  font=("default", 10, 'bold'))
        self.weight1_label.grid(row=3, column=1)

        self.activity1_menu = ttk.Combobox(self.sensor_frame3,
                                          value=ACTIVITIES,
                                          textvariable=self.activity1)
        self.activity1_menu.current(0)
        self.activity1_menu.config(state="readonly", width=15)
        self.activity1_menu.bind("<<ComboboxSelected>>")
        self.activity1_menu.grid(row=4, column=0, columnspan=2, pady=5)

        self.act_start_btn1 = ttk.Button(self.sensor_frame3,
                                         text="Activity start",
                                         command=lambda: self.activity_start(1),
                                         width=11)
        self.act_start_btn1["state"] = DISABLED
        self.act_start_btn1.grid(row=5, column=0, padx=2, pady=5)

        self.act_end_btn1 = ttk.Button(self.sensor_frame3,
                                      text="Activity end",
                                      command=lambda: self.activity_end(1),
                                      width=11)
        self.act_end_btn1["state"] = DISABLED
        self.act_end_btn1.grid(row=5, column=1, padx=2, pady=5)
        ###################################################################################

        # Menu
        menubar = Menu(self)
        tool = Menu(menubar, tearoff=0)
        tool.add_command(label="Insert user info", command=self.user_info)
        tool.add_command(label="Display kinect", command=self.disp_kinect)
        tool.add_checkbutton(label="Ignore sensor error",
                             onvalue=1, offvalue=0,
                             variable=self.sensor_ignore)
        tool.add_checkbutton(label="Ignore buffer error",
                             onvalue=1, offvalue=0,
                             variable=self.buffer_ignore)
        tool.add_checkbutton(label="debug mode",
                             onvalue=1, offvalue=0,
                             variable=self.debug_mode)
        tool.add_command(label="Close sensors", command=self.close)
        menubar.add_cascade(label="Tools", menu=tool)
        self.config(menu=menubar)

        # Tk widgets ----------------------------------------------------------
        #######################################################################
        # Sensor controls -----------------------------------------------------

        self.azure = PyK4A()
        self.azure.start()

        self.stream_reset()
        self.get_video()
        self.stream_video()
        self.stream_depth()

        self.set_state()
        self.refresh()

        # Main loop -----------------------------------------------------------
        self.mainloop()
        # Main loop -----------------------------------------------------------
        #######################################################################

    def get_video(self):
        img = self.azure.get_capture()
        time_stamp = img.color_timestamp_usec
        delta = time_stamp - self.time_stamp_tmp
        self.time_stamp_tmp = time_stamp
        if self.is_streaming:
            print(delta)
            if np.any(img.color):
                if delta < 33400:
                    pass
                else:
                    print('stream dropping 33400')
                    self.video_stream.append(self.rgb_frame_tmp)
                    self.depth_stream.append(self.depth_frame_tmp)
                self.depth_frame_tmp = img.depth
                self.rgb_frame_tmp = img.color
                self.video_stream.append(self.rgb_frame_tmp)
                self.depth_stream.append(self.depth_frame_tmp)
            else:
                print('stream dropping')
        self.after(30, self.get_video)

    def stream_video(self):
        if self.is_streaming:
            if self.video_stream.__len__() > 0:
                self.frame_count += 1
                img_color = self.video_stream.pop(0)
                img_color = img_color[:, :, 2::-1].astype(np.uint8)
                img_color = img_color[:, :, 2::-1]
                self.rgb_out.write(img_color)
            elif self.video_stream.__len__() == 0:
                pass
        self.after(VIDEO_SPEED, self.stream_video)

    def stream_depth(self):
        if self.is_streaming:
            if self.depth_stream.__len__() > 0:
                img_depth = self.depth_stream.pop(0)
                cv2.normalize(img_depth, img_depth, 0,
                              255, cv2.NORM_MINMAX)
                img_depth = cv2.cvtColor(img_depth,
                                         cv2.COLOR_GRAY2RGB)
                img_depth = img_depth.astype(np.uint8)
                self.depth_out.write(img_depth)
            elif self.depth_stream.__len__() == 0:
                pass
        self.after(VIDEO_SPEED, self.stream_depth)

    def activity_start(self, index):
        label = None
        if index == 0:
            label = f'0 {self.activity.get()} start'
            self.act_end_btn['state'] = NORMAL
            self.act_start_btn['state'] = DISABLED
        elif index == 1:
            label = f'1 {self.activity1.get()} start'
            self.act_end_btn1['state'] = NORMAL
            self.act_start_btn1['state'] = DISABLED
        for client in self.clients:
            client.label = f'{label}'
        self.activity_list.append(label)
        msg = f'{ACTIVITIE_START}-{label}'
        self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
        self.sound_client.publish(topic='sound', msg=msg, qos=0)
        self.video_activity_time.append([self.frame_count, label])
        self.stream_stop_btn['state'] = DISABLED
        self.stream_start_btn['state'] = DISABLED
        self.stream_save_btn['state'] = DISABLED
        self.stream_reset_btn['state'] = DISABLED
        

    def activity_end(self, index):
        label = None
        if index == 0:
            label = f'0 {self.activity.get()} end'
            self.act_end_btn['state'] = DISABLED
            self.act_start_btn['state'] = NORMAL
        elif index == 1:
            label = f'1 {self.activity1.get()} end'
            self.act_end_btn1['state'] = DISABLED
            self.act_start_btn1['state'] = NORMAL
        for client in self.clients:
            client.label = f'{label}'
        msg = f'{ACTIVITIE_STOP}-{label}'
        self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
        self.sound_client.publish(topic='sound', msg=msg, qos=0)
        self.video_activity_time.append([self.frame_count, label])
        self.stream_stop_btn['state'] = NORMAL
        self.stream_start_btn['state'] = DISABLED
        self.stream_save_btn['state'] = DISABLED
        self.stream_reset_btn['state'] = DISABLED

    def stream_start(self):
        sen_count = 0
        for i in range(len(self.clients)):
            if self.clients[i].sensor_ready:
                sen_count += 1
            else:
                if self.sensor_ignore.get():
                    sen_count += 1
                else:
                    messagebox.showwarning("Sensor Error",
                                           f"{SENSOR_ERROR}-{i+1}")
        if sen_count == len(self.clients) and self.age[0] != 'User':
            if not self.clients[0].is_started:
                self.start_sec = dt.today()
                self.date = self.start_sec.strftime(DATE_FORMAT)
                self.time = self.start_sec.strftime(TIME_FORMAT)
                self.time_path = \
                    f"{SAVE_PATH}/{self.date}/{self.time}"
                os.makedirs(f'{CACHE_PATH}/{self.date}/{self.time}')
                self.srt = open(f"{CACHE_PATH}/{self.date}/{self.time}/k3_rgb.srt", "w+")
                self.rgb_out = cv2.VideoWriter(f"{CACHE_PATH}/{self.date}/{self.time}/k3_rgb.avi",
                                               cv2.VideoWriter_fourcc(*'DIVX'),
                                               FPS, AZURE_KINECT_RGB_SIZE)
                self.depth_out = cv2.VideoWriter(f"{CACHE_PATH}/{self.date}/{self.time}/k3_depth.avi",
                                                 cv2.VideoWriter_fourcc(*'DIVX'),
                                                 FPS, AZURE_KINECT_DEPTH_SIZE)
                self.is_streaming = True
                for client in self.clients:
                    client.stream_init(f'{CACHE_PATH}/{self.date}/{self.time}')
            else:
                self.is_streaming = True
                for client in self.clients:
                    client.is_streaming = True
            msg = f'{START}-{self.time_path}'
            self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
            self.sound_client.publish(topic='sound', msg=msg, qos=0)
            self.stream_start_btn['state'] = DISABLED
            self.stream_start_btn['text'] = "Resume stream"
            self.stream_stop_btn['state'] = NORMAL
            self.stream_reset_btn['state'] = DISABLED
            self.stream_save_btn['state'] = DISABLED
            self.act_end_btn['state'] = DISABLED
            self.act_start_btn['state'] = NORMAL
            self.act_end_btn1['state'] = DISABLED
            self.act_start_btn1['state'] = NORMAL
        else:
            messagebox.showerror('ERROR', f'Insert user info or check sensors')
            self.is_streaming = False
            self.stream_stop(send=False)
            self.stream_reset(delete=True)

    def stream_stop(self, send=True):
        self.is_streaming = False
        for client in self.clients:
            client.is_streaming = False
        if send:
            self.stop_sec = dt.today()
            msg = f'{STOP}-?'
            self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
            self.sound_client.publish(topic='sound', msg=msg, qos=0)
        self.stream_stop_btn['state'] = DISABLED
        self.stream_start_btn['state'] = NORMAL
        self.stream_save_btn['state'] = NORMAL
        self.stream_reset_btn['state'] = NORMAL
        self.act_end_btn['state'] = DISABLED
        self.act_start_btn['state'] = DISABLED

        self.act_end_btn1['state'] = DISABLED
        self.act_start_btn1['state'] = DISABLED

    def stream_save(self):
        msg = f'{SAVE}-{self.time_path}'
        self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
        self.sound_client.publish(topic='sound', msg=msg, qos=0)
        for index, item in enumerate(self.video_activity_time):
            time = round(item[0] * 33.333)
            label = item[1]
            s_h, s_m, s_s, ms = get_time_1(time)
            s_s_t = str((s_s + SUB_DURATION) % 60).zfill(2)
            s_m_t = str((s_m + (s_s + SUB_DURATION)//60)).zfill(2)
            s_h_t = str((s_h + ((s_m + (s_s +
                                        SUB_DURATION)//60)//60))).zfill(2)
            s_h = str(s_h).zfill(2)
            s_m = str(s_m).zfill(2)
            s_s = str(s_s).zfill(2)
            self.srt.writelines([f"{(index+1)*2-1}\n",
                                f"{s_h}:{s_m}:{s_s},{ms} --> {s_h_t}:{s_m_t}:{s_s_t},{ms}\n",
                                f"{label}\n",
                                "\n"])
        self.srt.close()
        self.rgb_out.release()
        self.depth_out.release()
        try:
            os.mkdir(f'{SAVE_PATH}/{self.date}')
        except FileExistsError:
            pass
        move(f'{CACHE_PATH}/{self.date}/{self.time}', f'{SAVE_PATH}/{self.date}')
        usr_info = open(f'{SAVE_PATH}/{self.date}/{self.time}/user_info.csv', "w+", newline='')
        writer = csv.writer(usr_info)
        with usr_info:
            writer.writerow([self.age, self.sex, self.height, self.weight])
        rmtree(f'{CACHE_PATH}/{self.date}')
        self.summary()
        self.stream_reset()

    def stream_reset(self, delete=False):
        try:
            msg = f'{RESET}-{self.time_path}'
            self.sound_client.publish(topic='sound', msg=msg, qos=0)
            self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
        except AttributeError:
            pass
        self.stream_start_btn['text'] = "Stream start"
        self.stream_reset_btn['state'] = DISABLED
        self.stream_save_btn['state'] = DISABLED
        self.stream_stop_btn['state'] = DISABLED
        self.stream_start_btn['state'] = NORMAL
        self.act_start_btn['state'] = DISABLED
        self.act_start_btn['state'] = DISABLED
        self.video_stream = list()
        self.depth_stream = list()
        self.activity_list = list()
        self.video_activity_time = []

        for client in self.clients:
            client.is_started = False

        try:
            del(self.rgb_out)
            del(self.depth_out)
        except AttributeError:
            pass

        if delete:
            try:
                os.remove(f'{CACHE_PATH}/{self.date}/{self.time}/k3_rgb.avi')
                os.remove(f'{CACHE_PATH}/{self.date}/{self.time}/k3_depth.avi')
                os.remove(f'{CACHE_PATH}/{self.date}/{self.time}/k3_rgb.srt')
                for client in self.clients:
                    os.remove(f'{CACHE_PATH}/{self.date}/{self.time}/sensor_{client.info}.csv')
                rmtree(f'{CACHE_PATH}/{self.date}')
            except Exception as e:
                if self.debug_mode.get():
                    print(str(e))
                else:
                    pass

    def summary(self):
        os.system("clear")
        print("----  RESULT SUMMARY  ----")
        print(f"start time: {self.start_sec.strftime(TIME_FORMAT)} ---> end time: {self.stop_sec.strftime(TIME_FORMAT)}")
        print(f"Duration: {get_time_date(self.start_sec, self.stop_sec)}")
        print("\n----------------------------------------------------")
        print("Activities performed:")
        for index, label in enumerate(self.activity_list):
            spaces = [" " for i in range(index)]
            space = "".join(spaces)
            print(f"{space}{index+1}: {label}")
        print("----------------------------------------------------")

    def user_info(self):
        user = UserInfo(self)
        self.wait_window(user.win)
        self.age = user.age
        self.sex = user.sex
        self.weight = user.weight
        self.height = user.height
        try:
            self.age_label['text'] = user.age[0]
            self.sex_label['text'] = user.sex[0]
            self.height_label['text'] = str(user.height[0])
            self.weight_label['text'] = str(user.weight[0])
        except Exception:
            self.age1_label['text'] = 'User'
            self.sex1_label['text'] = 'User'
            self.height1_label['text'] = 'User'
            self.weight1_label['text'] = 'User'
        try:
            self.age1_label['text'] = str(user.age[1])
            self.sex1_label['text'] = user.sex[1]
            self.height1_label['text'] = str(user.height[1])
            self.weight1_label['text'] = str(user.weight[1])
        except Exception:
            self.age1_label['text'] = 'User'
            self.sex1_label['text'] = 'User'
            self.height1_label['text'] = 'User'
            self.weight1_label['text'] = 'User'
        del(user)

    def refresh(self):
        for i in range(len(self.clients)):
            if self.clients[i].sensor_ready:
                self.sensor_state[i]["foreground"] = 'green'
            else:
                self.sensor_state[i]["foreground"] = 'red'

    def set_state(self):
        for client in self.clients:
            if client.counter != client.counter_temp:
                client.counter_temp = client.counter
                client.death_counter = 0
                if self.debug_mode.get():
                    print(f'[INFO] SENSOR-{client.info} is working')
            else:
                print(f'[WARNING] SENSOR-{client.info} is not responding')
                client.death_counter += 1
                client.sensor_ready = False
            if client.death_counter > 8:
                messagebox.showerror('ERROR', f'SENSOR {client.info} DEAD')
        self.after(1000, self.set_state)

    def disp_kinect(self):
        if self.is_displaying:
            self.is_displaying = False
            msg = f'{STOP}-?'
            self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
            self.sound_client.publish(topic='sound', msg=msg, qos=0)
        else:
            self.is_displaying = True
            msg = f'{PLAY}-?'
            self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
            self.sound_client.publish(topic='sound', msg=msg, qos=0)

    def close(self):
        msg = f'{QUIT}-?'
        self.kinect_client.publish(topic='kinect', msg=msg, qos=0)
        self.sound_client.publish(topic='sound', msg=msg, qos=0)


SensorControl()

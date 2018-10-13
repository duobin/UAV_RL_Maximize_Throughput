# !usr/bin/env python
# -*- coding:utf-8 -*-
# Author:LiuQian,time:2018/5/18

import numpy as np
import tkinter as tk
import time

UNIT = 40
MAZE_H = 15
MAZE_W = 25

np.random.seed(1)


class Maze(tk.Tk, object):
    def __init__(self):
        super(Maze, self).__init__()
        self.action_space = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                             '11', '12', '13', '14', '15', '16', '17', '18', '19',
                             '20', '21', '22', '23', '24', '25']
        self.n_actions = len(self.action_space)
        self.n_features = 3  # 无人机位置, 电池量，信道
        self.battery = 10
        self.title('UAV测试环境')
        self.geometry('{0}x{1}'.format(MAZE_W * UNIT, MAZE_H * UNIT))
        self._build_maze()
        self.tau = 0

    def _build_maze(self):
        self.canvas = tk.Canvas(self, bg='white', height=MAZE_H * UNIT, width=MAZE_W * UNIT)

        # --------------------------构建固定点---------------------------
        self.oval_center = np.array([[100, 100], [220, 60], [500, 100], [220, 180], [380, 220],
                                     [180, 300], [60, 380], [220, 380], [460, 380], [100, 460],
                                     [340, 460], [220, 540], [500, 540], [660, 20], [780, 60],
                                     [980, 220], [700, 140], [580, 180], [900, 220], [620, 260],
                                     [940, 340], [820, 380], [660, 460], [940, 540], [700, 580]])
        for i in range(25):
            self.canvas.create_oval(self.oval_center[i, 0] - 10, self.oval_center[i, 1] - 10,
                                    self.oval_center[i, 0] + 10, self.oval_center[i, 1] + 10,
                                    fill='blue')

        # --------------------------用户--------------------------------
        self.user_center = np.array([[380, 100], [180, 140], [100, 260], [500, 260], [340, 340],
                                     [140, 380], [60, 540], [340, 580], [940, 20], [620, 100],
                                     [860, 140], [740, 300], [580, 420], [980, 420], [780, 500]])
        for i in range(15):
            self.canvas.create_oval(self.user_center[i, 0] - 5, self.user_center[i, 1] - 5,
                                    self.user_center[i, 0] + 5, self.user_center[i, 1] + 5,
                                    fill='black')

        # --------------------------UAV标识-----------------------------
        self.img = tk.PhotoImage(file="UAV.png")
        self.uav = self.canvas.create_image((40, 40), image=self.img)

        # pack all
        self.canvas.pack()

    def reset_uav(self):
        self.update()
        time.sleep(0.1)
        self.battery = 10
        self.canvas.delete(self.uav)
        self.uav = self.canvas.create_image((40, 40), image=self.img)
        # return np.array([self.canvas.coords(self.uav)[0] / (MAZE_W * UNIT),
        #  self.canvas.coords(self.uav)[1] / (MAZE_H * UNIT)])
        return [self.canvas.coords(self.uav)[0] / (MAZE_W * UNIT), self.canvas.coords(self.uav)[1] / (MAZE_H * UNIT)]
        # return np.hstack((np.array([self.canvas.coords(self.uav)[0] / (MAZE_W * UNIT),
        #                           self.canvas.coords(self.uav)[1] / (MAZE_H * UNIT)]), self.battery / 10))

    def step(self, action):
        s = np.array(self.canvas.coords(self.uav))
        for i in range(25):
            if action == i:
                self.canvas.delete(self.uav)
                point = self.oval_center[i, :]
                self.uav = self.canvas.create_image((point[0], point[1]), image=self.img)
                break

        next_coords = self.canvas.coords(self.uav)  # next state,返回值是列表[ , ]

        # np.random.seed(2)
        u = np.random.uniform(0, 10, 15)               # 任务量可改！！！

        # reward function
        for j in range(25):
            if next_coords == self.oval_center[j, :].tolist():
                p = 0.1                      # 功率
                rho = 10e-5                  # 单位db
                sigma = 9.999999999999987e-15   # 加性高斯白噪声

                # 飞行能耗，归一化问题
                ef = p * (np.sqrt((s[0] - self.oval_center[j, 0]) ** 2 +
                                  (s[1] - self.oval_center[j, 1]) ** 2)) / 800

                # 盘旋能耗
                distance = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])    # 15个用户间距离

                for k in range(15):
                    distance[k] = (next_coords[0] - self.user_center[k, 0])**2 +\
                                  (next_coords[1] - self.user_center[k, 1])**2

                o = distance.tolist().index(distance.min())  #距离下一个坐标最近用户索引

                eh = p * (u[o] / np.emath.log2(1 + ((p*(rho / (100**2 + distance.min())))/sigma))) * 5

                # 效用函数
                utility = 1 - np.exp(-((u[o] ** 2) / (u[o] + 8)))

                # 计算能耗
                ec = 0.3 * u[o] / 10

                self.battery -= (ef + ec + eh)
                reward = utility - ef - ec - eh

                if self.battery <= 0:
                    done = True
                else:
                    done = False

                #s_ = np.hstack((np.array([next_coords[0] / (MAZE_H * UNIT), next_coords[1] / (MAZE_W * UNIT)]),
                #               self.battery / 10))
                s_ = [next_coords[0] / (MAZE_H * UNIT), next_coords[1] / (MAZE_W * UNIT)]
                self.tau += 1
                # print('Reward:', reward)
                return s_, reward, self.tau, done

    def render(self):
        # time.sleep(0.5)
        self.update()


if __name__ == "__main__":
    env = Maze()
    env.mainloop()

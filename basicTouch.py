#!/usr/bin/env python3

import math
import numpy as np
import math
import pyrosim

HEIGHT = 0.3
EPS = 0.05
np.random.seed(0)

def send_to_simulator(sim, weight_matrix):
    main_body = sim.send_box(x=0, y=0, z=HEIGHT+EPS,
                             length=HEIGHT, width=HEIGHT,
                             height=EPS*2.0, mass=1)

    # id arrays
    thighs = [0]*4
    shins = [0]*4
    hips = [0]*4
    knees = [0]*4
    foot_sensors = [0]*4
    sensor_neurons = [0]*5
    motor_neurons = [0]*8

    delta = float(math.pi)/2.0

    # quadruped is a box with one leg on each side
    # each leg consists thigh and shin cylinders
    # with hip and knee joints
    # each shin/foot then has a touch sensor
    for i in range(4):
        theta = delta*i
        x_pos = math.cos(theta)*HEIGHT
        y_pos = math.sin(theta)*HEIGHT

        thighs[i] = sim.send_cylinder(x=x_pos, y=y_pos, z=HEIGHT+EPS,
                                      r1=x_pos, r2=y_pos, r3=0,
                                      length=HEIGHT, radius=EPS, capped=True
                                      )

        hips[i] = sim.send_hinge_joint(main_body, thighs[i],
                                       x=x_pos/2.0, y=y_pos/2.0, z=HEIGHT+EPS,
                                       n1=-y_pos, n2=x_pos, n3=0,
                                       lo=-math.pi/4.0, hi=math.pi/4.0,
                                       speed=1.0)

        motor_neurons[i] = sim.send_motor_neuron(joint_id=hips[i])

        x_pos2 = math.cos(theta)*1.5*HEIGHT
        y_pos2 = math.sin(theta)*1.5*HEIGHT

        if i>0:
            shins[i] = sim.send_cylinder(x=x_pos2, y=y_pos2, z=(HEIGHT+EPS)/2.0,
                                         r1=0, r2=0, r3=1,
                                         length=HEIGHT, radius=EPS,
                                         mass=1. if i!=2 else 10., capped=True)
        else:
            shins[i] = sim.send_cylinder(x=x_pos2*4.0/3.0, y=y_pos2*4.0/3.0, z=HEIGHT+EPS,
                                         r1=1, r2=0, r3=0,
                                         length=HEIGHT, radius=EPS,
                                         mass=1., capped=True)

        knees[i] = sim.send_hinge_joint(thighs[i], shins[i],
                                        x=x_pos2, y=y_pos2, z=HEIGHT+EPS,
                                        n1=-y_pos, n2=x_pos, n3=0,
                                        lo=-math.pi/2.0, hi=math.pi/2.0)

        motor_neurons[i+4] = sim.send_motor_neuron(knees[i])
        foot_sensors[i] = sim.send_touch_sensor(shins[i])
        sensor_neurons[i] = sim.send_sensor_neuron(foot_sensors[i])

        fneuron = sim.send_function_neuron(lambda x: 0.02*math.sin(x))
        sim.send_synapse(fneuron, motor_neurons[4], 1.0)

    ENVCUBESIZE = 0.15

    env_cube = sim.send_box(x=2.5*HEIGHT, y=0, z=ENVCUBESIZE/2.,
                            length=ENVCUBESIZE, width=ENVCUBESIZE,
                            height=ENVCUBESIZE, mass=1)

    sim.create_collision_matrix('all')
    sim.send_camera((0,-HEIGHT*10,HEIGHT), (90,0,0))

    return None

    ## layouts are useful for other things not relevant to this example
    #layout = {'thighs': thighs,
    #          'shins': shins,
    #          'hips': hips,
    #          'knees': knees,
    #          'feet': foot_sensors,
    #          'sensor_neurons': sensor_neurons,
    #          'motor_neurons': motor_neurons}

    # return layout

if __name__ == "__main__":

    seconds = 100.0
    dt = 0.05
    eval_time = int(seconds/dt)
    print(eval_time)
    gravity = -1.0

    sim = pyrosim.Simulator(eval_time=eval_time, debug=True,
                               play_paused=False,
                               gravity=gravity,
                               play_blind=False,
                               use_textures=True,
                               capture=False,
                               dt=dt)
    num_sensors = 5
    num_motors = 8

    # our weight matrix specifies the values for the
    # starting and ending weights as well as the starting and
    # ending times for the synapses
    weight_matrix = np.random.rand(num_sensors+num_motors,
                                   num_sensors+num_motors, 4)
    weight_matrix[:, :, 0:1] = weight_matrix[:, :, 0:1]*2.-1.

    send_to_simulator(sim, weight_matrix=weight_matrix)
    sim.start()

    sim.wait_to_finish()

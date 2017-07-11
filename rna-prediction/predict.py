import tensorflow as tf
import os
import numpy as np
import RNA
import copy
from numpy.random import choice

base_seq = [1,1,1,1,1,1,1,1,1,1,1,1,1] + ([0]*95)
current_struc = [1,1,1,1,1,1,1,1,1,1,1,1,1] + ([0]*95)
target_struc = [2,2,2,2,1,1,1,1,1,3,3,3,3] + ([0]*95)
current_energy = [0.0] + ([0]*107)
target_energy = [0.0] + ([0]*107)
locks = [2,2,1,1,2,2,2,2,2,1,1,1,1] + ([0]*95)

TF_SHAPE = 648
len_puzzle = 13

inputs2 = np.array([base_seq,current_struc,target_struc,current_energy,target_energy,locks])
inputs = inputs2.reshape([-1,TF_SHAPE])

with tf.Graph().as_default() as base_graph:
  saver1 = tf.train.import_meta_graph(os.getcwd()+'/models/baseDNN3.meta')
sess1 = tf.Session(graph=base_graph)
saver1.restore(sess1,os.getcwd()+'/models/baseDNN3')

x = base_graph.get_tensor_by_name('x_placeholder:0')
y = base_graph.get_tensor_by_name('y_placeholder:0')
keep_prob = base_graph.get_tensor_by_name('keep_prob_placeholder:0')

base_weights = base_graph.get_tensor_by_name('op7:0')

base_feed_dict={x:inputs,keep_prob:1.0}

with tf.Graph().as_default() as location_graph:
  saver2 = tf.train.import_meta_graph(os.getcwd()+'/models/locationDNN.meta')
sess2 = tf.Session(graph=location_graph)
saver2.restore(sess2,os.getcwd()+'/models/locationDNN')

x2 = location_graph.get_tensor_by_name('x_placeholder:0')
y2 = location_graph.get_tensor_by_name('y_placeholder:0')
keep_prob2 = location_graph.get_tensor_by_name('keep_prob_placeholder:0')

location_weights = location_graph.get_tensor_by_name('op7:0')

location_feed_dict = {x2:inputs,keep_prob2:1.0}
movesets = []
iteration = 0
while(True):
    if np.all(inputs2[1] == inputs2[2]):
        print("Puzzle Solved")
        break
    else:
        location_array = ((sess2.run(location_weights,location_feed_dict))[0])

        base_array = ((sess1.run(base_weights,base_feed_dict))[0])
        base_array = base_array - min(base_array)
        print base_array + 1635
        print base_array
        total = sum(base_array)
        base_array = base_array/total
        print base_array
        print sum(base_array)
        base_change = (choice([1,2,3,4],1,p=base_array,replace=False))[0]

        location_array = location_array[:len_puzzle] - min(location_array[:len_puzzle])
        total_l = sum(location_array)
        location_array = location_array/total_l
        location_change = (choice(list(range(1,len(location_array)+1)),1,p=location_array,replace=False))[0]

        inputs2 = inputs.reshape([6,TF_SHAPE/6])

        
        temp = copy.deepcopy(inputs2[0])
        temp[location_change] = base_change
        move = [base_change,location_change]
        movesets.append(move)
        print move
        str_seq = []
        for i in temp:
            if i == 1:
                str_seq.append('A')
            elif i == 2:
                str_seq.append('U')
            elif i == 3:
                str_seq.append('G')
            elif i == 4:
                str_seq.append('C')
        str_seq = ''.join(str_seq)
        str_struc,current_e = RNA.fold(str_seq)
        rna_struc = []
        for i in inputs2[2]:
            if i == 1:
                rna_struc.append('.')
            elif i == 2:
                rna_struc.append('(')
            elif i == 3:
                rna_struc.append(')')
        rna_struc = ''.join(rna_struc)
        target_e = RNA.energy_of_structure(str_seq,rna_struc,0)
        enc_struc = []
        for i in str_struc:
            if i == '.':
                enc_struc.append(1)
            elif i == '(':
                enc_struc.append(2)
            elif i == ')':
                enc_struc.append(3)
        inputs2[0] = temp
        inputs2[1][:len(enc_struc)] = enc_struc
        inputs2[3][0] = current_e
        inputs2[4][0] = target_e
        inputs = inputs2.reshape([-1,TF_SHAPE])
        base_feed_dict={x:inputs,keep_prob:1.0}
        location_feed_dict = {x2:inputs,keep_prob2:1.0}
        iteration += 1
        print iteration
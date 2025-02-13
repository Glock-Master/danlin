# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 15:27:48 2019

@author: Daniel Lin
"""

import tensorflow as tf
import tensorflow_hub as hub

from keras.models import Model
from keras.layers import Input, Dense, Embedding, Flatten, Bidirectional, CuDNNGRU, GRU, CuDNNLSTM, LSTM, GlobalMaxPooling1D, Lambda
from keras.layers.core import Dropout

class elmo_model(object):
    
    def __init__ (self, config):
    
        self.MAX_LEN = config['model_settings']['model_para']['max_sequence_length']
        #embedding_dim = config['model_settings']['model_para']['embedding_dim']
        self.use_dropout = config['model_settings']['model_para']['use_dropout']
        self.dropout_rate = config['model_settings']['model_para']['dropout_rate']
        self.LOSS_FUNCTION = config['model_settings']['loss_function']
        self.OPTIMIZER = config['model_settings']['optimizer']['type']
        self.dnn_size = config['model_settings']['model_para']['dnn_size']
        self.rnn_size = config['model_settings']['model_para']['rnn_size']
        self.embedding_trainable = config['model_settings']['model_para']['embedding_trainable']

    """
    To integrate with Keras, we simply create a function that we’ll use in a Lambda layer. 
    Note that we must explicitly cast the input as a string.
    """
    def make_elmo_embedding(self, x):
        # Load the elmo model which is a pre-trained models trained on the 1 Billion Word Benchmark
        elmo_model = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
    
        embeddings = elmo_model(tf.squeeze(tf.cast(x, tf.string)), signature="default", as_dict=True)["elmo"]
        
        return embeddings

    def build_elmo_network(self, GPU_flag):
        elmo_input = Input(shape=(None, ), dtype='string') 
        elmo_embedding = Lambda(self.make_elmo_embedding, output_shape=(None, 1024))(elmo_input)
        if GPU_flag:
            bilstm_1 = Bidirectional(CuDNNLSTM(self.rnn_size, return_sequences=True))(elmo_embedding)
            bilstm_2 = Bidirectional(CuDNNLSTM(self.rnn_size, return_sequences=True), merge_mode='concat')(bilstm_1)
        else:
            bilstm_1 = Bidirectional(LSTM(self.rnn_size, activation='tanh', return_sequences=True))(elmo_embedding)
            bilstm_2 = Bidirectional(LSTM(self.rnn_size, activation='tanh', return_sequences=True), merge_mode='concat')(bilstm_1)
        gmp_layer = GlobalMaxPooling1D()(bilstm_2)
        if self.use_dropout:
            dropout_layer_2 = Dropout(self.dropout_rate)(gmp_layer)
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(dropout_layer_2)
        else:
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(gmp_layer)
        # Output Layer
        pred = Dense(units=1, activation='sigmoid')(dense_1)
        
        model = Model(inputs=elmo_input, outputs=pred, name = 'Elmo_network')
        
        model.compile(loss=self.LOSS_FUNCTION,
                 optimizer=self.OPTIMIZER,
                 metrics=['accuracy'])
        #model.summary()
        return model

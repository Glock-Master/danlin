# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:46:14 2019

@author: Daniel Lin

"""

from keras.models import Model
from keras.layers import Input, Dense, Embedding, Flatten, Bidirectional, CuDNNGRU, GRU, CuDNNLSTM, LSTM, GlobalMaxPooling1D
from keras.layers.core import Dropout

class Deep_model(object):
    
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
           
    def build_DNN(self, word_index, embedding_matrix, embedding_dim):
        
        inputs = Input(shape=(self.MAX_LEN,))
        sharable_embedding = Embedding(len(word_index) + 1,
                                   embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=self.MAX_LEN,
                                   trainable= self.embedding_trainable)(inputs)
        dense = Flatten()(sharable_embedding)
        dense_0 = Dense(self.dnn_size, activation='relu')(dense)
        
        if self.use_dropout:
            dropout_layer_2 = Dropout(self.dropout_rate)(dense_0)
            dense_1 = Dense(self.dnn_size, activation='relu')(dropout_layer_2)
        else:
            dense_1 = Dense(self.dnn_size, activation='relu')(dense_0)
            
        if self.use_dropout:
            dropout_layer_3 = Dropout(self.dropout_rate)(dense_1)
            dense_2 = Dense(int(self.dnn_size/2), activation='relu')(dropout_layer_3)
        else:
            dense_2 = Dense(int(self.dnn_size/2), activation='relu')(dense_1)
    
        dense_3 = Dense(int(self.dnn_size/4))(dense_2)
        dense_4 = Dense(1, activation='sigmoid')(dense_3)
        
        model = Model(inputs=inputs, outputs = dense_4, name='DNN_network')
        
        model.compile(loss=self.LOSS_FUNCTION,
                 optimizer=self.OPTIMIZER,
                 metrics=['accuracy'])
        
        return model
    
    def build_GRU(self, word_index, embedding_matrix, embedding_dim, GPU_flag):
        inputs = Input(shape=(self.MAX_LEN,))

        sharable_embedding = Embedding(len(word_index) + 1,
                                   embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=self.MAX_LEN,
                                   trainable=self.embedding_trainable)(inputs)
        if GPU_flag:
            gru_1 = CuDNNGRU(self.rnn_size, return_sequences=True)(sharable_embedding) # The default activation is 'tanh',
        else:
            gru_1 = GRU(self.rnn_size, activation = 'tanh', return_sequences=True)(sharable_embedding)
        if self.use_dropout:
            droput_layer_1 = Dropout(self.dropout_rate)(gru_1)
            if GPU_flag:
                gru_2 = CuDNNGRU(self.rnn_size, return_sequences=True)(droput_layer_1)
            else:
                gru_2 = GRU(self.rnn_size, activation = 'tanh', return_sequences=True)(droput_layer_1)
        else:
            if GPU_flag:
                gru_2 = CuDNNGRU(self.rnn_size, return_sequences=True)(droput_layer_1)
            else:
                gru_2 = GRU(self.rnn_size, activation = 'tanh', return_sequences=True)(droput_layer_1)
        
        gmp_layer = GlobalMaxPooling1D()(gru_2)
        
        if self.use_dropout:
            dropout_layer_2 = Dropout(self.dropout_rate)(gmp_layer)
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(dropout_layer_2)
        else:
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(gmp_layer)
            
        dense_2 = Dense(int(self.rnn_size/4))(dense_1)
        dense_3 = Dense(1, activation='sigmoid')(dense_2)
        
        model = Model(inputs=inputs, outputs = dense_3, name='GRU_network')
        
        model.compile(loss=self.LOSS_FUNCTION,
                 optimizer=self.OPTIMIZER,
                 metrics=['accuracy'])
        
        return model
    
    def build_LSTM(self, word_index, embedding_matrix, embedding_dim, GPU_flag):
        inputs = Input(shape=(self.MAX_LEN,))

        sharable_embedding = Embedding(len(word_index) + 1,
                                   embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=self.MAX_LEN,
                                   trainable=self.embedding_trainable)(inputs)
        if GPU_flag:
            gru_1 = CuDNNLSTM(self.rnn_size, return_sequences=True)(sharable_embedding) # The default activation is 'tanh',
        else:
            gru_1 = LSTM(self.rnn_size, activation='tanh', return_sequences=True)(sharable_embedding)
        if self.use_dropout:
            droput_layer_1 = Dropout(self.dropout_rate)(gru_1)
            if GPU_flag:
                gru_2 = CuDNNLSTM(self.rnn_size, return_sequences=True)(droput_layer_1)
            else:
                gru_2 = LSTM(self.rnn_size, activation='tanh', return_sequences=True)(droput_layer_1)
        else:
            if GPU_flag:
                gru_2 = CuDNNLSTM(self.rnn_size, return_sequences=True)(droput_layer_1)
            else:
                gru_2 = LSTM(self.rnn_size, activation = 'tanh', return_sequences=True)(droput_layer_1)
        
        gmp_layer = GlobalMaxPooling1D()(gru_2)
        
        if self.use_dropout:
            dropout_layer_2 = Dropout(self.dropout_rate)(gmp_layer)
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(dropout_layer_2)
        else:
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(gmp_layer)
            
        dense_2 = Dense(int(self.rnn_size/4))(dense_1)
        dense_3 = Dense(1, activation='sigmoid')(dense_2)
        
        model = Model(inputs=inputs, outputs = dense_3, name='LSTM_network')
        
        model.compile(loss=self.LOSS_FUNCTION,
                 optimizer=self.OPTIMIZER,
                 metrics=['accuracy'])
        
        return model
    
    def build_BiGRU(self, word_index, embedding_matrix, embedding_dim, GPU_flag):
        inputs = Input(shape=(self.MAX_LEN,))

        sharable_embedding = Embedding(len(word_index) + 1,
                                   embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=self.MAX_LEN,
                                   trainable=self.embedding_trainable)(inputs)
        if GPU_flag:
            bigru_1 = Bidirectional(CuDNNGRU(int(self.dnn_size/2), return_sequences=True), merge_mode='concat')(sharable_embedding) # The default activation is 'tanh',
        else:
            bigru_1 = Bidirectional(GRU(int(self.dnn_size/2), activation = 'tanh', return_sequences=True), merge_mode='concat')(sharable_embedding)
        if self.use_dropout:
            droput_layer_1 = Dropout(self.dropout_rate)(bigru_1)
            if GPU_flag:
                bigru_2 = Bidirectional(CuDNNGRU(int(self.dnn_size/2), return_sequences=True), merge_mode='concat')(droput_layer_1)
            else:
                bigru_2 = Bidirectional(GRU(int(self.dnn_size/2), activation = 'tanh', return_sequences=True), merge_mode='concat')(droput_layer_1)
        else:
            if GPU_flag:
                bigru_2 = Bidirectional(CuDNNGRU(int(self.dnn_size/2), return_sequences=True), merge_mode='concat')(bigru_1)
            else:
                bigru_2 = Bidirectional(GRU(int(self.dnn_size/2), activation = 'tanh', return_sequences=True), merge_mode='concat')(bigru_1)
        
        gmp_layer = GlobalMaxPooling1D()(bigru_2)
        
        if self.use_dropout:
            dropout_layer_2 = Dropout(self.dropout_rate)(gmp_layer)
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(dropout_layer_2)
        else:
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(gmp_layer)
            
        dense_2 = Dense(int(self.rnn_size/4))(dense_1)
        dense_3 = Dense(1, activation='sigmoid')(dense_2)
        
        model = Model(inputs=inputs, outputs = dense_3, name='BiGRU_network')
        
        model.compile(loss=self.LOSS_FUNCTION,
                 optimizer=self.OPTIMIZER,
                 metrics=['accuracy'])
        
        return model
    
    def build_BiLSTM(self, word_index, embedding_matrix, embedding_dim, GPU_flag):
        inputs = Input(shape=(self.MAX_LEN,))

        sharable_embedding = Embedding(len(word_index) + 1,
                                   embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=self.MAX_LEN,
                                   trainable=self.embedding_trainable)(inputs)
        if GPU_flag:
            bilstm_1 = Bidirectional(CuDNNLSTM(int(self.dnn_size/2), return_sequences=True), merge_mode='concat')(sharable_embedding) # The default activation is 'tanh',
        else:
            bilstm_1 = Bidirectional(LSTM(int(self.dnn_size/2), activation = 'tanh', return_sequences=True), merge_mode='concat')(sharable_embedding)
        if self.use_dropout:
            droput_layer_1 = Dropout(self.dropout_rate)(bilstm_1)
            if GPU_flag:
                bilstm_2 = Bidirectional(CuDNNLSTM(int(self.dnn_size/2), return_sequences=True), merge_mode='concat')(droput_layer_1)
            else:
                bilstm_2 = Bidirectional(LSTM(int(self.dnn_size/2), activation = 'tanh', return_sequences=True), merge_mode='concat')(droput_layer_1)
        else:
            if GPU_flag:
                bilstm_2 = Bidirectional(CuDNNLSTM(int(self.dnn_size/2), return_sequences=True), merge_mode='concat')(bilstm_1)
            else:
                bilstm_2 = Bidirectional(LSTM(int(self.dnn_size/2), activation = 'tanh', return_sequences=True), merge_mode='concat')(bilstm_1)
        
        gmp_layer = GlobalMaxPooling1D()(bilstm_2)
        
        if self.use_dropout:
            dropout_layer_2 = Dropout(self.dropout_rate)(gmp_layer)
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(dropout_layer_2)
        else:
            dense_1 = Dense(int(self.dnn_size/2), activation='relu')(gmp_layer)
            
        dense_2 = Dense(int(self.rnn_size/4))(dense_1)
        dense_3 = Dense(1, activation='sigmoid')(dense_2)
        
        model = Model(inputs=inputs, outputs = dense_3, name='BiLSTM_network')
        
        model.compile(loss=self.LOSS_FUNCTION,
                 optimizer=self.OPTIMIZER,
                 metrics=['accuracy'])
        
        return model
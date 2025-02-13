# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 12:16:36 2019

@author: Daniel Lin

"""

import os
import pandas as pd
import datetime
import numpy as np
import pickle
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.callbacks import TensorBoard, CSVLogger
from sklearn.utils import class_weight
from sklearn.metrics import classification_report, confusion_matrix
from keras.models import load_model, Model
from sklearn.model_selection import train_test_split

from src.utils import plot_history
from src.DataLoader import getCFilesFromText, GenerateLabels, SavedPickle, ListToCSV, LoadPickleData
from src.models.Deep_model import Deep_model
from src.models.textCNN import textCNN
'''
Import the self-implemented model here.
'''
from src.models.attention.HAN import AttentionLayer
from src.models.LSTM_with_HAN import customized_model
from src.models.elmo_network import elmo_model

class Helper():
    ''' Super class Solver for all kinds of tasks'''
    def __init__(self, config, paras):
        self.config = config
        self.paras = paras
        #self.tokenizer_path = self.config['training_settings']['tokenizer_path']       
        #self.embed_path = self.config['training_settings']['embedding_model_path']
        #self.embed_dim = self.config['model_settings']['model_para']['embedding_dim']
        self.tokenizer_saved_path = self.config['embedding_settings']['embedding_model_saved_path']
        if not os.path.exists(self.paras.data_dir): os.makedirs(self.paras.data_dir)
        if not os.path.exists(self.config['training_settings']['model_save_path']): os.makedirs(self.config['training_settings']['model_save_path']) 
        if not os.path.exists(self.tokenizer_saved_path): os.makedirs(self.tokenizer_saved_path)
        ELMo_padding = 1000
        setattr(self, 'ELMo_padding', ELMo_padding)
    
    def patitionData(self, data_list_pad, data_list_id):
    
        test_size = self.config['training_settings']['dataset_config']['Test_set_ratio']
        validation_size = self.config['training_settings']['dataset_config']['Test_set_ratio'] 
        data_list_label = GenerateLabels(data_list_id)
        
        if not self.config['training_settings']['using_separate_test_set']:
            # The value of the seed for testing should be the same to that was used during the training phase.  
            train_vali_set_x, test_set_x, train_vali_set_y, test_set_y, train_vali_set_id, test_set_id = train_test_split(data_list_pad, data_list_label, data_list_id, test_size=test_size, random_state=self.paras.seed)
            train_set_x, validation_set_x, train_set_y, validation_set_y, train_set_id, validation_set_id = train_test_split(train_vali_set_x, train_vali_set_y, train_vali_set_id, test_size=validation_size, random_state=self.paras.seed)
        
            tuple_with_test = train_set_x, train_set_y, train_set_id, validation_set_x, validation_set_y, validation_set_id, test_set_x, test_set_y, test_set_id
            setattr(self, 'patitioned_data', tuple_with_test)
            return tuple_with_test
        else:
            train_set_x, validation_set_x, train_set_y, validation_set_y, train_set_id, validation_set_id = train_test_split(train_vali_set_x, train_vali_set_y, train_vali_set_id, test_size=validation_size, random_state=self.paras.seed)
            tuple_without_test = train_set_x, train_set_y, train_set_id, validation_set_x, validation_set_y, validation_set_id
            setattr(self, 'patitioned_data', tuple_without_test)
            return tuple_without_test
    
    def Tokenization(self, data_list):
        tokenizer = Tokenizer(num_words=None, filters=',', lower=False, char_level=False, oov_token=None) 
        tokenizer.fit_on_texts(data_list)
        # Save the tokenizer.
        with open(self.tokenizer_saved_path + 'tokenizer.pickle', 'wb') as handle:
            pickle.dump(tokenizer, handle)
            
    def LoadToknizer(self, path_of_tokenizer):
        tokenizer = LoadPickleData(path_of_tokenizer)
        return tokenizer
    
    def verbose(self, msg):
        ''' Verbose function for print information to stdout'''
        if self.paras.verbose == 1:
            print('[INFO]', msg)
    
    def padding(self, sequences_to_pad):
        padded_seq = pad_sequences(sequences_to_pad, maxlen = self.config['model_settings']['model_para']['max_sequence_length'], padding ='post')
        return padded_seq
    
    def loadData(self, data_path):
        ''' Load data for training/validation'''
        self.verbose('Loading data from '+ os.getcwd() + os.sep + data_path + '....')
        total_list, total_list_id = getCFilesFromText(data_path)
        self.verbose("The length of the loaded data list is : " + str(len(total_list)))
        return total_list, total_list_id
    
    def JoinSubLists(self, list_to_join):
        new_list = []
        
        for sub_list_token in list_to_join:
            new_line = ' '.join(sub_list_token)
            new_list.append(new_line)
        return new_list
    
    def modelLoader(self):
        trained_model_path = self.paras.trained_model
        if os.path.isfile(trained_model_path):
            # Load the model and print the model details.
            if (str(self.config['model_settings']['model']).lower() == 'han'):
                trained_model = load_model(trained_model_path, custom_objects = {'AttentionLayer': AttentionLayer})
            else:
                trained_model = load_model(trained_model_path)
            trained_model.summary()
            return trained_model
        else:
            self.verbose("Failed to load the trained model!")
        
class Trainer(Helper):
    ''' Handler for complete training progress'''
    def __init__(self,config,paras):
        super(Trainer, self).__init__(config,paras)
        self.verbose('Start training process....')
        if not os.path.exists(self.paras.output_dir): os.makedirs(self.paras.output_dir)
        if not os.path.exists(self.paras.logdir): os.makedirs(self.paras.logdir)
        self.model_save_path = config['training_settings']['model_save_path']
        self.model_save_name = config['training_settings']['model_saved_name']
        self.log_path = config['training_settings']['log_path']
        
    def exec(self):
        
        total_list, total_list_id = self.loadData(self.paras.data_dir)
        embedding_method = str(self.paras.embedding).lower()
        if embedding_method == 'elmo':
            self.verbose ("Applying ELMo model!")
            self.verbose ("Setting padding length " + str(self.ELMo_padding) + " for ELMo model. Each textual sequence contains " + str(self.ELMo_padding) + " elements.")
            new_total_list = self.JoinSubLists(total_list)
            total_list_pad = [' '.join(t.split()[0:self.ELMo_padding]) for t in new_total_list]
            total_list_pad = np.array(total_list_pad, dtype=object)[:, np.newaxis]
        else:
            self.verbose("Perform tokenization ....")
            self.Tokenization(total_list)
            self.verbose("Tokenization completed!")
            self.verbose("-------------------------------------------------------")   
            self.verbose("Perform code embedding ....")
            if embedding_method == 'word2vec':
                from src.embedding import WordToVec as Embedding_Model
                embedding_model = Embedding_Model(self.config)
                total_sequences, word_index = embedding_model.LoadTokenizer(total_list)
                embedding_model.TrainWordToVec(total_list)
                embedding_matrix, embedding_dim = embedding_model.ApplyWordToVec(word_index)            
                self.verbose ("Word2vec loaded! ")
            
            elif embedding_method == 'glove':
                from src.embedding import Glove as Embedding_Model
                embedding_model = Embedding_Model(self.config)
                total_sequences, word_index = embedding_model.LoadTokenizer(total_list)
                embedding_model.TrainGlove(total_list)
                embedding_matrix, embedding_dim = embedding_model.ApplyGlove(word_index)
                self.verbose ("GLoVe loaded! ")
            
            elif embedding_method == 'fasttext':
                from src.embedding import FastText as Embedding_Model
                embedding_model = Embedding_Model(self.config)
                total_sequences, word_index = embedding_model.LoadTokenizer(total_list)
                embedding_model.TrainFastText(total_list)
                embedding_matrix, embedding_dim = embedding_model.ApplyFastText(word_index)
                self.verbose ("FastText loaded! ")
            else:
                raise AssertionError("Embedding method not supported!")
                
            self.verbose("Pad the sequence to unified length...")
            total_list_pad = self.padding(total_sequences)
        self.verbose("Patition the data ....")
        data_tuple = self.patitionData(total_list_pad, total_list_id)  
        train_set_x = data_tuple[0] 
        train_set_y = np.asarray(data_tuple[1]).flatten()
        train_set_id = data_tuple[2] 
        validation_set_x = data_tuple[3]
        validation_set_y = np.asarray(data_tuple[4]).flatten()
        validation_set_id = data_tuple[5] 
            #test_set_x = data_tuple[6] 
            #test_set_y = np.asarray(data_tuple[7]).flatten()
            #test_set_id = data_tuple[8]
        
        self.verbose ("Data processing completed!")
        self.verbose ("-------------------------------------------------------")
        self.verbose ("There are " + str(len(train_set_x)) + " total samples in the training set. " + str(np.count_nonzero(train_set_y)) + " vulnerable samples. " )
        self.verbose ("There are " + str(len(validation_set_x)) + " total samples in the validation set. " + str(np.count_nonzero(validation_set_y)) + " vulnerable samples. " )
        #self.verbose ("There are " + str(len(test_set_x)) + " total samples in the test set. " + str(np.count_nonzero(test_set_y)) + " vulnerable samples. " )       
        
        if self.config['model_settings']['model_para']['handle_data_imbalance']:
            class_weights = class_weight.compute_class_weight('balanced',
                                                 np.unique(train_set_y),
                                                 train_set_y)
        else:
            class_weights = None
        
        self.verbose ("-------------------------------------------------------")
        """
        Initialize the model class here.
        """

        if tf.test.is_gpu_available():
            # GPU support is recommended.
            GPU_flag = True
            os.environ["CUDA_VISIBLE_DEVICES"]="0"
            self.verbose ("Using GPU to speed up training process.")
        else:
            GPU_flag = False
            self.verbose ("No GPU detected.")
            self.verbose ("Using CPU for training. It may take considerable time!")
        
        deep_model = Deep_model(self.config)
        test_CNN = textCNN(self.config)
        '''
        Add the self-implemented model here.
        '''
        lstm_with_han = customized_model(self.config)
        elmo_network = elmo_model(self.config)
        
        """
        Load the model.
        """
        network_model = str(self.config['model_settings']['model']).lower()
        if network_model == 'dnn':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = deep_model.build_DNN(word_index, embedding_matrix, embedding_dim)
        if network_model == 'gru':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = deep_model.build_GRU(word_index, embedding_matrix, embedding_dim, GPU_flag)
        if network_model == 'lstm':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = deep_model.build_LSTM(word_index, embedding_matrix, embedding_dim, GPU_flag)
        if network_model == 'bigru':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = deep_model.build_BiGRU(word_index, embedding_matrix, embedding_dim, GPU_flag)
        if network_model == 'bilstm':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = deep_model.build_BiLSTM(word_index, embedding_matrix, embedding_dim, GPU_flag)
        if network_model == 'textcnn':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = test_CNN.buildModel(word_index, embedding_matrix, embedding_dim)
        """
        Load the customized model here.
        """
        if network_model == 'han':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = lstm_with_han.build_LSTM_with_HAN(word_index, embedding_matrix, embedding_dim, GPU_flag)
        if network_model == 'elmo':
            self.verbose ("Loading the " + self.config['model_settings']['model'] + " model.")
            model_func = elmo_network.build_elmo_network(GPU_flag)
        
        self.verbose("Model structure loaded.")
        model_func.summary()
            
        callbacks_list = [
                ModelCheckpoint(filepath = self.config['training_settings']['model_save_path'] + self.config['training_settings']['model_saved_name'] +
                                '_{epoch:02d}_{val_accuracy:.3f}_{val_loss:3f}' + '.h5', 
                                monitor = self.config['training_settings']['network_config']['validation_metric'], 
                                verbose = self.paras.verbose, 
                                save_best_only = self.config['training_settings']['save_best_model'], 
                                period = self.config['training_settings']['period_of_saving']),
                EarlyStopping(monitor = self.config['training_settings']['network_config']['validation_metric'], 
                              patience = self.config['training_settings']['network_config']['patcience'], 
                              verbose = self.paras.verbose, 
                              mode="auto"),     
                TensorBoard(log_dir=self.config['training_settings']['log_path'], 
                            batch_size = self.config['training_settings']['network_config']['batch_size'],
                            write_graph=True, 
                            write_grads=True, 
                            write_images=True, 
                            embeddings_freq=0, 
                            embeddings_layer_names=None, 
                            embeddings_metadata=None),
                CSVLogger(self.config['training_settings']['log_path'] + os.sep + self.config['training_settings']['model_saved_name'] + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log')]
        
        train_history = model_func.fit(train_set_x, train_set_y,
                                       epochs = self.config['training_settings']['network_config']['epochs'],
                                       batch_size = self.config['training_settings']['network_config']['batch_size'],
                                       shuffle = False, # The data has already been shuffle before, so it is unnessary to shuffle it again. (And also, we need to correspond the ids to the features of the samples.))
                                       validation_data = (validation_set_x, validation_set_y),
                                       callbacks = callbacks_list,
                                       verbose=self.paras.verbose, 
                                       class_weight = class_weights)
        if self.config['training_settings']['network_config']['save_training_history']:
            SavedPickle(self.config['training_settings']['model_save_path'] + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.pkl', train_history)
        if self.config['training_settings']['network_config']['plot_training_history']:
            plot_history(self.config, train_history) 

class Tester(Helper):
    ''' Handler for complete inference progress'''
    def __init__(self,config,paras):
        super(Tester, self).__init__(config,paras)
        if not os.path.exists(self.paras.output_dir): os.makedirs(self.paras.output_dir)
        self.verbose('Start testing process....')
            
    def loadTestSet(self):
        if not self.config['training_settings']['using_separate_test_set']:
            total_list, total_list_id = self.loadData(self.paras.data_dir)
            self.verbose("Pad the sequence to unified length...")
            embedding_method = str(self.paras.embedding).lower()
            if embedding_method == 'elmo':
                total_list_pad = [' '.join(t.split()[0:self.ELMo_padding]) for t in total_list]
            else:
                tokenizer = self.LoadToknizer(self.tokenizer_saved_path + 'tokenizer.pickle')
                total_sequence = tokenizer.texts_to_sequences(total_list)
                total_list_pad = self.padding(total_sequence)
            self.verbose("Patition the data ....")
            tuple_with_test = self.patitionData(total_list_pad, total_list_id)  
            test_set_x = tuple_with_test[6] 
            test_set_y = np.asarray(tuple_with_test[7]).flatten()
            test_set_id = tuple_with_test[8]
            self.verbose ("There are " + str(len(test_set_x)) + " total samples in the test set. " + str(np.count_nonzero(test_set_y)) + " vulnerable samples. " )
            test_list_id = test_set_id
        else:
            self.verbose ("Loading test data from " + os.getcwd() + os.sep + self.config['training_settings']['test_set_path'])
            test_list, test_list_id = self.loadData(self.config['training_settings']['test_set_path'])  
            self.verbose("Pad the sequence to unified length...")
            embedding_method = str(self.paras.embedding).lower()
            if embedding_method == 'elmo':
                test_list_pad = [' '.join(t.split()[0:self.ELMo_padding]) for t in test_list]
            else:
                tokenizer = self.LoadToknizer(self.tokenizer_saved_path + 'tokenizer.pickle')
                test_sequence = tokenizer.texts_to_sequences(test_list)
                test_list_pad = self.padding(test_sequence)
            test_list_label = GenerateLabels(test_list_id)
            test_set_x = test_list_pad
            test_set_y = test_list_label
            
        return test_set_x, test_set_y, test_list_id
    
    def getAccuracy(self, probs, test_set_y):
        predicted_classes = []
        for item in probs:
            if item[0] > 0.5:
                predicted_classes.append(1)
            else:
                predicted_classes.append(0)    
        test_accuracy = np.mean(np.equal(test_set_y, predicted_classes)) 
        return test_accuracy, predicted_classes
    
    
    def exec(self):
        test_set_x, test_set_y, test_set_id = self.loadTestSet()
        model = self.modelLoader()
        probs = model.predict(test_set_x, batch_size = self.config['training_settings']['network_config']['batch_size'], verbose = self.paras.verbose)
        accuracy, predicted_classes = self.getAccuracy(probs, test_set_y)
        self.verbose(self.config['model_settings']['model'] + " classification result: \n")
        self.verbose("Total accuracy: " + str(accuracy))
        self.verbose("----------------------------------------------------")
        self.verbose("The confusion matrix: \n")
        target_names = ["Non-vulnerable","Vulnerable"] #non-vulnerable->0, vulnerable->1
        print (confusion_matrix(test_set_y, predicted_classes, labels=[0,1]))   
        print ("\r\n")
        print (classification_report(test_set_y, predicted_classes, target_names=target_names))
        # Wrap the result to a CSV file.        
        if not isinstance(test_set_x, list): test_set_x = test_set_x.tolist()
        if not isinstance(probs, list): probs = probs.tolist()
        if not isinstance(test_set_id, list): test_set_id = test_set_id.tolist()        
        zippedlist = list(zip(test_set_id, probs, test_set_y))
        result_set = pd.DataFrame(zippedlist, columns = ['Function_ID', 'Probs. of being vulnerable', 'Label'])
        ListToCSV(result_set, self.paras.output_dir + os.sep + self.config['model_settings']['model'] + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_result.csv')
          
class GetRepresentation(Helper):
    ''' Handler for complete inference progress'''
    def __init__(self,config,paras):
        super(GetRepresentation, self).__init__(config,paras)
        self.verbose('Obtain representations from trained model....')
    
    def ObtainRepresentations(self, input_sequences, layer_number, model):
        layered_model = Model(inputs = model.input, outputs=model.layers[layer_number].output)
        representations = layered_model.predict(input_sequences)
        return representations
    
    """
    The size of the obtained representations can be very large when we obtain the representations
    of many data samples at a time. The following method allows the representations to be obtained batch by batch. 
    """
    def ObtainRepresentations_by_batch_size(self, input_sequences, layer_number, model, BATCH_SIZE):
        num_batches_per_epoch = int((len(input_sequences) - 1) / BATCH_SIZE) + 1
        data_size = len(input_sequences)
        representations_total = []
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * BATCH_SIZE
            end_index = min((batch_num + 1) * BATCH_SIZE, data_size)
            print ("-------start_index------------")
            print (start_index)
            print ("-------end_index------------")
            print (end_index)
            layered_model = Model(inputs = model.input, outputs=model.layers[layer_number].output)
            representations = layered_model.predict(input_sequences[start_index: end_index])
            representations_total = representations_total + representations.tolist()
        return np.asarray(representations_total)
    
    def exec(self):
        self.verbose ("Loading data from " + os.getcwd() + os.sep + self.paras.data_dir)
        data_list, data_list_id = self.loadData(self.paras.data_dir)  
        self.verbose("Pad the sequence to unified length...")
        tokenizer = self.LoadToknizer(self.tokenizer_saved_path + 'tokenizer.pickle')
        data_sequence = tokenizer.texts_to_sequences(data_list)
        data_list_pad = self.padding(data_sequence)
        self.verbose("Loading the trained model.")
        model = self.modelLoader()
        obtained_repre = self.ObtainRepresentations(data_list_pad, self.paras.layer, model)
        #return obtained_repre
        self.verbose("Saving the obtained representations....")
        if not os.path.exists(self.paras.saved_path): os.makedirs(self.paras.saved_path)
        SavedPickle(self.paras.saved_path + "obtain_reper.pkl", obtained_repre)
        # When the obtained representations are 2-D arrays, we can also save them in a CSV file.
        #ListToCSV(obtained_repre, self.paras.saved_path)
        self.verbose("The obtained representations are saved in: " + str(self.paras.saved_path) + ".")
        
        # Test attention visualization.
        if (str(self.config['model_settings']['model']).lower() == 'han'):
            from src.utils import visualize_attention
            word_index = tokenizer.word_index
            for i in range(len(data_list_pad)):
                visualize_attention(data_list_pad, i, self.paras.layer, model, word_index, 15)

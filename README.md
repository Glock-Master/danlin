# Function-level-Vulnerability-Detection

Hi there, welcome!

This is an open-source project for source code-level vulnerability detection based on the supervised machine learning technqiue. This project contains a framework which encapsulates 6 mianstream neural network models and can be easily extended to use other network models implemented using Keras or Tensorflow. It also provides 3 embedding methods (i.e., Word2vec, GloVe and FastText) for generating code embeddings. The framework does not require any code analysis. It takes source code (i.e., functions or files) as input and the output is a probability of the corresponding input sample being vulnerable or not.    

For this project, we also collected vulnerable functions from 9 open-source software projects (written in C programming language). See [Dataset](https://github.com/Seahymn2019/Function-level-Vulnerability-Dataset/blob/master/Vulnerable%20Functions%20Statistical%20Analysis.md) for more details. We have detailed the framework design and data collection processes in a paper which is currently under review. When the review process is completed, we will publish all the data.

## Requirements

 * Environments -- Please refer to [required_packages.txt](https://github.com/DanielLin1986/Function-level-Vulnerability-Detection/blob/master/required_packages.txt)
 * Hardware -- A GPU with at least 4GB RAM is recommended.
 
## Instructions & Usage
Unzip the zip file of this repository, one will see the following folders:
* The config folder -- containing the configuration file.
* The data folder -- containing the source code functions (vulnerable and non-vulnerable).
* The result folder -- containing the sample results.
* The src folder -- containing the code for model training and test.

And there is only one Python script file:
* main.py -- for training and test a specified network model. By specifying different parameters, users can apply different embedding methods.

There are also some options/parameters available for performing a model training/test tasks, which are listed below:

| Options | Description                                                                                   |
|---------|-----------------------------------------------------------------------------------------------|
| config  | Path to the configuration file.                                                                        |
| seed    | Random seed for reproduction of the results.                                       |
| data_dir    | The path of the code base for training. (can be obtained by download & unzip the files under data folder. By default, it is `data/`.) |
| logdir  | Path to store training logs (log files for Tensorboard). By default, it is `logs/`                                                   |
| output_dir  | The output path of the trained network model. By default, it is `result/models/<model_name.h5>`                                                |
| trained_model   | The path of the trained model for test. By default, the trained models are in `result/models/`                                                      |                                                               
| embedding |  The embedding method for converting source code sequences to meaningful vector representations. Currently, we also support Word2vec, GloVe and FastText. By default, the Word2vec is selected. |
| test   | Switch to the test mode.                                                               |
| verbose    | Show all messages. 

### Step 1: Train a neural network model

When the Word2vec model is ready. One can train a neural network model. The parameters related to experiment/model settings are stored in a yaml configuration file. This allows users to conveniently adjust the settings by just changing the configuration file. See [documentation and examples](config/) for more details.

Once the configuration file is ready, one may run the following command to train a neural network model.
```
Python main.py --config config\config.yaml --data_dir <path_to_your_code>
```
By default, the data used for training is at `data\` folder. The trained models will be placed at `result/models/` folder. The training logs will be at `logs/`. A user can use Tensorboard to visualize the training process by specifying the `logs\` folder to Tensorboard.

### Step 2: Test a trained neural network model

When training is completed, a user can test a network model on the test set by using following command: 
```
Python main.py --config config\config.yaml --test --trained_model D:\Path\of\the\trained_model.h5
```
Users can use their own test set by specifying the `using_separate_test_set` to True in the config.yaml file.

## Dataset and Results
 * [Dataset](https://github.com/Seahymn2019/Function-level-Vulnerability-Dataset/blob/master/Vulnerable%20Functions%20Statistical%20Analysis.md) -- containing vulnerable and non-vulnerable functions labeled/collected from 9 open-source projects and data statistics.
 * [Training and Evaluation Results](https://github.com/Seahymn2019/Function-level-Vulnerability-Dataset/blob/master/Training%20and%20Results.md) -- containing test results for reference.

## Contact:

You are welcomed to use/modify our code. Any bug report or improvement suggestions will be appreciated. Please kindly cite our paper (when it is published.) if you use the code/data in your work. For acquiring more data or inquiries, please contact: junzhang@swin.edu.au.

Thanks!


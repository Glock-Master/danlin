# Function-level Vulnerability Detection

Hi there, welcome!

This is an open-source project for source code-level vulnerability detection based on the supervised machine learning technique. The project implementation is based on the following papers: 

 * [Deep Learning-Based Vulnerable Function Detection: A Benchmark](https://link.springer.com/chapter/10.1007/978-3-030-41579-2_13). 
 * [A Context-aware Neural Embedding for Function-level Vulnerability Detection](https://www.mdpi.com/1999-4893/14/11/335)

This project contains a framework which encapsulates 6 mainstream neural network models and can be easily extended to use other network models implemented using Keras or Tensorflow. It provides 3 non-contextual (static) embedding methods (i.e., Word2vec, GloVe and FastText) and 1 contextual embedding method which is Embedding from Language Models (ELMo) for generating code embeddings. A contextual embedding method can generate code representations based on different contexts where a code token appears. In contrast, non-contextual embedding methods can only represent a fixed embedding for a given code token, unable to represent the polyseme in code contexts.

The framework does not require any code analysis. It takes source code (i.e., functions or files) as input and the output is a probability of the corresponding input sample being vulnerable or not.    

For this project, we also collected vulnerable functions from 9 open-source software projects (written in C programming language). See [Dataset](https://github.com/Seahymn2019/Function-level-Vulnerability-Dataset/blob/master/Vulnerable%20Functions%20Statistical%20Analysis.md) for more details. We have detailed the framework design and data collection processes in a paper which is currently under review. When the review process is completed, we will publish all the data.

## Requirements

 * Environments -- Please refer to [required_packages.txt](https://github.com/DanielLin1986/Function-level-Vulnerability-Detection/blob/master/required_packages.txt)
 * Hardware -- A GPU with at least 4GB RAM is recommended. Using CPU for training takes considerable time.
 
## Instructions & Usage
Unzip the zip file of this repository, one will see the following folders:
* The config folder -- containing the configuration file.
* The data folder -- containing the source code functions (vulnerable and non-vulnerable).
* The result folder -- containing the sample results.
* The src folder -- containing the code for model training and test.

And there are two Python script files:
* main.py -- for training and testing a specified network model. By specifying different options/parameters, users can apply different embedding methods and switch between training and testing mode.
* Obtain_representations.py -- for obtaining high-level representations from a trained network model.

The options/parameters available for performing a training/test task, which are listed below:

| Options | Description                                                                                   |
|---------|-----------------------------------------------------------------------------------------------|
| config  | Path to the configuration file.                                                                        |
| seed    | Random seed for reproduction of the results.                                       |
| data_dir    | The path of the code base for training. (can be obtained by download & unzip the files under data folder. By default, it is `data/`.) |
| logdir  | Path to store training logs (log files for Tensorboard). By default, it is `logs/`                                                   |
| output_dir  | The output path of the trained network model. By default, it is `result/models/<model_name.h5>`                                                |
| trained_model   | The path of the trained model for test. By default, the trained models are stored in `result/models/`                                                      |                                                               
| embedding |  The embedding method for converting source code sequences to meaningful vector representations. Currently, we also support Word2vec, GloVe and FastText. By default, the Word2vec method is used. |
| test   | Switch to the test mode.                                                               |
| verbose    | Show all messages. 

### Step 1: Train a neural network model

The parameters related to experiment/model settings are stored in a yaml configuration file. This allows users to conveniently adjust the settings by just changing the configuration file. See [documentation and examples](config/) for more details.

Once the configuration file is ready, one may run the following command to train a neural network model.
```
Python main.py --config config\config.yaml --data_dir <path_to_your_code>
```
By default, the data (which is the source code) for training is at `data\` folder and the embedding method used is the Word2vec embedding. The trained models will be placed at `result/models/` folder. The logs during the training phase will be at `logs/` folder. A user can use Tensorboard to visualize the training process by specifying the `logs\` folder when invoking the Tensorboard.

To use the other embedding methods, for example, to use the FastText for converting the source code, users can type the following:
```
Python main.py --config config\config.yaml --data_dir <path_to_your_code> --embedding FastText
```
or

```
Python main.py --config config\config.yaml --data_dir <path_to_your_code> --embedding ELMo
```

### Step 2: Test a trained neural network model

When training is completed, a user can test a network model on the test set by using following command: 
```
Python main.py --config config\config.yaml --test --trained_model D:\Path\of\the\trained_model.h5
```
Users can use their own test set by specifying the `using_separate_test_set` to True in the config.yaml file.

### Step 3: Obtain high-level representations from any layer of a network model

When training is completed, a user can obtain high-level representations from any layer of a trained network model. Suppose a user has
a few samples stored in `\home\user_name\data_path\`. The user wants to have the representations from the `5`-th layer (the number of layers starts from 0). Then, a user can type:

```
Python Obtain_representations.py --config config\config.yam --input_dir <\home\user_name\data_path\> --trained_model <\path\of\the\trained_model> --layer 5 --saved_path <\path\to\save\>
```

The representations of the samples extracted from the 5-th layer of the model will be saved in the Pickle format and stored in the path `\path\to\save`. The obtained representations can be used as features for various tasks. For example, them can be used to train a random forest classifier.

## Dataset and Results
 * [Dataset](https://github.com/Seahymn2019/Function-level-Vulnerability-Dataset/blob/master/Vulnerable%20Functions%20Statistical%20Analysis.md) -- containing vulnerable and non-vulnerable functions labeled/collected from 9 open-source projects and data statistics.
 * [Training and Evaluation Results](https://github.com/Seahymn2019/Function-level-Vulnerability-Dataset/blob/master/Training%20and%20Results.md) -- containing test results for reference.
 
## Acknowledgement

I would like to thank [anhhaibkhn](https://github.com/anhhaibkhn) for contributing to this repository, pointing out errors in the code and providing comments. 

## Contact

You are welcomed to use/modify our code. Any bug report or improvement suggestions will be appreciated. Please kindly cite our paper (when it is published.) if you use the code/data in your work. For acquiring more data or inquiries, please contact: junzhang@swin.edu.au.

Thanks!


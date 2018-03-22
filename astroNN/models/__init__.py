import h5py
import json

from .ApogeeBCNN import ApogeeBCNN
from .ApogeeCNN import ApogeeCNN
from .ApogeeCVAE import ApogeeCVAE
from .Cifar10CNN import Cifar10CNN
from .GalaxyGAN2017 import GalaxyGAN2017
from .MNIST_BCNN import MNIST_BCNN
from .StarNet2017 import StarNet2017
from .Galaxy10GAN import Galaxy10GAN

from astroNN.config import keras_import_manager, custom_model_path_reader

keras = keras_import_manager()
optimizers = keras.optimizers
Sequential = keras.models.Sequential

__all__ = ['ApogeeBCNN', 'ApogeeCNN', 'ApogeeCVAE', 'StarNet2017', 'GalaxyGAN2017', 'Cifar10CNN', 'MNIST_BCNN',
           'Galaxy10GAN']


def galaxy10_cnn_setup():
    """
    NAME:
        galaxy10_cnn_setup
    PURPOSE:
        setup galaxy10_cnn from cifar10_cnn with Galaxy10 parameter
    INPUT:
    OUTPUT:
        (instance): a callable instances from Cifar10_CNN with Galaxy10 parameter
    HISTORY:
        2018-Feb-09 - Written - Henry Leung (University of Toronto)
    """
    from astroNN.datasets.galaxy10 import galaxy10cls_lookup
    galaxy10_net = Cifar10CNN()
    galaxy10_net._model_identifier = 'Galaxy10CNN'
    targetname = []
    for i in range(10):
        targetname.extend([galaxy10cls_lookup(i)])

    galaxy10_net.targetname = targetname
    return galaxy10_net


# Jsst an alias for Galaxy10 example
Galaxy10CNN = galaxy10_cnn_setup()


def load_folder(folder=None):
    """
    NAME:
        load_folder
    PURPOSE:
        load astroNN model object from folder
    INPUT:
        folder (string): Name of folder, or can be None
    OUTPUT:
    HISTORY:
        2017-Dec-29 - Written - Henry Leung (University of Toronto)
    """

    import numpy as np
    import os

    currentdir = os.getcwd()

    if folder is not None:
        fullfilepath = os.path.join(currentdir, folder)
    else:
        fullfilepath = currentdir

    astronn_model_obj = None

    if folder is not None and os.path.isfile(os.path.join(folder, 'astroNN_model_parameter.json')) is True:
        with open(os.path.join(folder, 'astroNN_model_parameter.json')) as f:
            parameter = json.load(f)
            f.close()
    elif os.path.isfile('astroNN_model_parameter.json') is True:
        with open('astroNN_model_parameter.json') as f:
            parameter = json.load(f)
            f.close()
    elif not os.path.exists(folder):
        raise IOError('Folder not exists: ' + str(currentdir + '/' + folder))
    else:
        raise FileNotFoundError('Are you sure this is an astroNN generated folder?')

    identifier = parameter['id']

    if identifier == 'ApogeeCNN':
        astronn_model_obj = ApogeeCNN()
    elif identifier == 'ApogeeBCNN':
        astronn_model_obj = ApogeeBCNN()
    elif identifier == 'ApogeeCVAE':
        astronn_model_obj = ApogeeCVAE()
    elif identifier == 'Cifar10CNN':
        astronn_model_obj = Cifar10CNN()
    elif identifier == 'MNIST_BCNN':
        astronn_model_obj = MNIST_BCNN()
    elif identifier == 'Galaxy10CNN':
        astronn_model_obj = Galaxy10CNN()
    elif identifier == 'StarNet2017':
        astronn_model_obj = StarNet2017()
    elif identifier == 'GalaxyGAN2017':
        astronn_model_obj = GalaxyGAN2017()
    elif identifier == 'Galaxy10GAN':
        astronn_model_obj = Galaxy10GAN()
    else:
        unknown_model_message = f'Unknown model identifier -> {identifier}.'
        # try to load custom model from CUSTOM_MODEL_PATH
        CUSTOM_MODEL_PATH = custom_model_path_reader()
        # try the current folder and see if there is any .py on top of CUSTOM_MODEL_PATH
        list_py_files = [os.path.join(fullfilepath, f) for f in os.listdir(fullfilepath) if f.endswith(".py")]
        if CUSTOM_MODEL_PATH + list_py_files is None:
            print("\n")
            raise TypeError(unknown_model_message)
        else:
            import sys
            from importlib import import_module
            for path in CUSTOM_MODEL_PATH + list_py_files:
                head, tail = os.path.split(path)
                sys.path.insert(0, head)
                try:
                    model = getattr(import_module(tail.strip('.py')), str(identifier))
                    astronn_model_obj = model()
                except AttributeError:
                    pass

        if astronn_model_obj is None:
            print("\n")
            raise TypeError(unknown_model_message)

    astronn_model_obj.currentdir = currentdir
    astronn_model_obj.fullfilepath = fullfilepath

    # Must have parameter
    astronn_model_obj.input_shape = parameter['input']
    astronn_model_obj.labels_shape = parameter['labels']
    astronn_model_obj.num_hidden = parameter['hidden']
    astronn_model_obj.input_mean = parameter['input_mean']
    astronn_model_obj.labels_mean = parameter['labels_mean']
    astronn_model_obj.input_norm_mode = parameter['input_norm_mode']
    astronn_model_obj.labels_norm_mode = parameter['labels_norm_mode']
    astronn_model_obj.batch_size = parameter['batch_size']
    astronn_model_obj.input_std = parameter['input_std']
    astronn_model_obj.labels_std = parameter['labels_std']
    astronn_model_obj.targetname = parameter['targetname']
    astronn_model_obj.val_size = parameter['valsize']

    # Conditional parameter depends on neural net architecture
    try:
        astronn_model_obj.num_filters = parameter['filternum']
    except KeyError:
        pass
    try:
        astronn_model_obj.filter_len = parameter['filterlen']
    except KeyError:
        pass
    try:
        pool_length = parameter['pool_length']
        if isinstance(pool_length, int):  # multi-dimensional case
            astronn_model_obj.pool_length = parameter['pool_length']
        else:
            astronn_model_obj.pool_length = list(parameter['pool_length'])
    except KeyError:
        pass
    try:
        # need to convert to int because of keras do not want array or list
        astronn_model_obj.latent_dim = int(parameter['latent'])
    except KeyError:
        pass
    try:
        astronn_model_obj.task = parameter['task']
    except KeyError:
        pass
    try:
        astronn_model_obj.dropout_rate = parameter['dropout_rate']
    except KeyError:
        pass
    try:
        # if inverse model precision exists, so does length_scale
        astronn_model_obj.inv_model_precision = parameter['inv_tau']
        astronn_model_obj.length_scale = parameter['length_scale']
    except KeyError:
        pass
    try:
        astronn_model_obj.l2 = parameter['l2']
    except KeyError:
        pass
    with h5py.File(os.path.join(astronn_model_obj.fullfilepath, 'model_weights.h5'), mode='r') as f:
        training_config = f.attrs.get('training_config')
        training_config = json.loads(training_config.decode('utf-8'))
        optimizer_config = training_config['optimizer_config']
        optimizer = optimizers.deserialize(optimizer_config)
        astronn_model_obj.compile(optimizer=optimizer)
        # set weights
        astronn_model_obj.keras_model.load_weights(os.path.join(astronn_model_obj.fullfilepath, 'model_weights.h5'))

        # Build train function (to get weight updates), need to consider Sequential model too
        astronn_model_obj.keras_model._make_train_function()
        if isinstance(astronn_model_obj.keras_model, Sequential):
            astronn_model_obj.keras_model.model._make_train_function()
        else:
            astronn_model_obj.keras_model._make_train_function()
        optimizer_weights_group = f['optimizer_weights']
        optimizer_weight_names = [n.decode('utf8') for n in optimizer_weights_group.attrs['weight_names']]
        optimizer_weight_values = [optimizer_weights_group[n] for n in optimizer_weight_names]
        astronn_model_obj.keras_model.optimizer.set_weights(optimizer_weight_values)

    print("========================================================")
    print(f"Loaded astroNN model, model type: {astronn_model_obj.name} -> {identifier}")
    print("========================================================")
    return astronn_model_obj

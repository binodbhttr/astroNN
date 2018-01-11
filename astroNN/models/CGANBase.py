from abc import ABC, abstractmethod
import numpy as np

from keras.backend import clear_session
from keras.optimizers import Adam

from astroNN.models.loss.regression import mean_squared_error
from astroNN.models.loss.classification import categorical_cross_entropy, bayes_crossentropy_wrapper
from astroNN.models.NeuralNetMaster import NeuralNetMaster


class CGANBase(NeuralNetMaster, ABC):
    """Top-level class for a Convolutional Generative Adversarial Network"""
    def __init__(self):
        """
        NAME:
            __init__
        PURPOSE:
            To define astroNN Convolutional Generative Adversarial Network
        HISTORY:
            2018-Jan-10 - Written - Henry Leung (University of Toronto)
        """
        super(CGANBase, self).__init__()
        self.name = 'Convolutional Generative Adversarial Network'
        self._model_type = 'CGAN'
        self.initializer = None
        self.activation = None
        self._last_layer_activation = None
        self.num_filters = None
        self.filter_length = None
        self.pool_length = None
        self.num_hidden = None
        self.reduce_lr_epsilon = None
        self.reduce_lr_min = None
        self.reduce_lr_patience = None
        self.l2 = None
        self.latent_dim = None

        self.keras_vae = None
        self.keras_encoder = None
        self.keras_decoder = None

        self.input_shape = None

        self.input_normalizer = None
        self.recon_normalizer = None
        self.input_norm_mode = 1
        self.labels_norm_mode = 1
        self.input_mean_norm = None
        self.input_std_norm = None
        self.labels_mean_norm = None
        self.labels_std_norm = None

    @abstractmethod
    def discriminator(self):
        raise NotImplementedError

    @abstractmethod
    def generator(self):
        raise NotImplementedError


    @abstractmethod
    def model(self):
        raise NotImplementedError

    def compile(self):
        self.keras_model, self.keras_vae, self.keras_encoder, self.keras_decoder = self.model()

        if self.optimizer is None or self.optimizer == 'adam':
            self.optimizer = Adam(lr=self.lr, beta_1=self.beta_1, beta_2=self.beta_2, epsilon=self.optimizer_epsilon,
                                  decay=0.0)

        self.keras_model.compile(loss=None, optimizer=self.optimizer)
        return None

    @abstractmethod
    def train(self, input_data, input_recon_target):
        raise NotImplementedError

    def pre_training_checklist_child(self):
        self.pre_training_checklist_master()

    def post_training_checklist_child(self):
        astronn_model = 'model_weights.h5'
        self.keras_model.save_weights(self.fullfilepath + astronn_model)
        print(astronn_model + ' saved to {}'.format(self.fullfilepath + astronn_model))

        np.savez(self.fullfilepath + '/astroNN_model_parameter.npz', id=self._model_identifier, filterlen=self.filter_length,
                 filternum=self.num_filters, hidden=self.num_hidden, input=self.input_shape, labels=self.input_shape,
                 task=self.task, latent=self.latent_dim, input_mean=self.input_mean_norm,
                 labels_mean=self.labels_mean_norm, input_std=self.input_std_norm, labels_std=self.labels_std_norm)

        clear_session()
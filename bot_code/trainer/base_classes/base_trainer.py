import configparser

import os

from bot_code.utils.dynamic_import import get_class
from bot_code.trainer.utils.ding import ding


class BaseTrainer:
    model_class = None
    BASE_CONFIG_HEADER = 'Trainer Configuration'
    MODEL_CONFIG_HEADER = 'Model Configuration'
    batch_size = None
    model = None
    config = None


    def __init__(self):
        self.load_config()

    def run(self):
        '''
        Main entry point to do training start to finish.
        '''
        print('setting up the trainer')
        self.setup_trainer()
        print('setting up the model')
        self.setup_model()
        print('running the trainer')
        self._run_trainer()
        print('training finished')
        self.finish_trainer()

    def get_config_name(self):
        """
        returns the name of a file in bot_code/trainer/configs/
        """
        raise NotImplementedError('Derived classes must override this.')

    def create_config(self):
        if self.config is None:
            self.config = configparser.RawConfigParser()
            file = 'configs/' + str(self.get_config_name())
            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            self.config.read(dir_path + '/' + file)
        return self.config

    def create_model_config(self):
        return self.create_config()[self.MODEL_CONFIG_HEADER]

    def load_config(self):
        # Obtaining necessary data for training from the config
        config = self.create_config()
        self.batch_size = config.getint(self.MODEL_CONFIG_HEADER, 'batch_size')

        # Over here the model data is obtained
        model_package = config.get(self.MODEL_CONFIG_HEADER, 'model_package')
        model_name = config.get(self.MODEL_CONFIG_HEADER, 'model_name')
        self.model_class = get_class(model_package, model_name)

    def setup_trainer(self):
        """Called to setup the functions of the trainer and anything needed for the creation of the model"""
        raise NotImplementedError('Derived classes must override this.')

    def instantiate_model(self, model_class):
        return model_class(self.sess,
                           self.action_handler.get_logit_size(),
                           action_handler=self.action_handler,
                           is_training=True,
                           optimizer=self.optimizer,
                           config_file=self.create_model_config())

    def setup_model(self):
        self.model = self.instantiate_model(self.model_class)
        self.model.add_summary_writer(self.get_event_filename())

    def get_event_filename(self):
        return 'event'

    def finish_trainer(self):
        ding()

    def _run_trainer(self):
        '''
        This is where your long process of training neural nets goes.
        You may asume the trainer and model are set up.
        '''
        raise NotImplementedError('Derived classes must override this.')

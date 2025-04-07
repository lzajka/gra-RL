import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
from logging import getLogger

class Linear_QNet(nn.Module):

    def __init__(self, input_size, hidden_size, output_size, load_model_path=None, save_model_path=None):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
        self.log = getLogger(__name__)
        self.training_enabled = True

        if load_model_path is not None:
            self.__load(load_model_path)
        
        self.save_model_path = save_model_path

        
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def __load(self, file_name):
        if os.path.exists(file_name):
            self.load_state_dict(torch.load(file_name))
            self.eval()
            self.training_enabled = False
            self.log.info(f"Model {file_name} załadowany pomyślnie.")
        else:
            raise FileNotFoundError(f"Model {file_name} nie znaleziony.")
    
    def save(self):
        """Zapisuje model do pliku"""
        if self.save_model_path is None: return
        save_model_path = self.save_model_path
        
        torch.save(self.state_dict(), save_model_path)
        self.log.info(f"Model {save_model_path} zapisany pomyślnie.")
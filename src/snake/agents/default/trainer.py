import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
from logging import getLogger

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.log = getLogger(__name__)
        self.log.debug('Inicjalizuje QTrainer')
        self.log.debug(f'lr: {lr}, gamma: {gamma}')
        self.log.debug(f'model: {model}')
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
    
    def train_step(self, state_pp, action_pp, reward, next_state_pp, done):
        state_pp = torch.tensor(state_pp, dtype=torch.float)
        # lrud (danger), lrud (food)
        next_state_pp = torch.tensor(next_state_pp, dtype=torch.float)
        action_pp = torch.tensor(action_pp, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        done = torch.tensor(done, dtype=torch.float)


        if len(state_pp.shape) == 1:
            state_pp = torch.unsqueeze(state_pp, 0)
            next_state_pp = torch.unsqueeze(next_state_pp, 0)
            action_pp = torch.unsqueeze(action_pp, 0)
            reward = torch.unsqueeze(reward, 0)
            done = torch.unsqueeze(done, 0)
        
        # Równanie Bellmana

        pred = self.model(state_pp)
        
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state_pp[idx]))
            target[idx][torch.argmax(action_pp).item()] = Q_new
        
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        
        self.optimizer.step()
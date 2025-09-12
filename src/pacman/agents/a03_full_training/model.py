import torch
from src.pacman.agents._base import Linear_QNet as LQ

class Linear_QNet(LQ):
    def save(self):
        """Zapisuje model do pliku"""
        if self.save_model_path is None: return
        save_model_path = self.save_model_path
        
        torch.save(self.state_dict(), save_model_path)
        self.log.info(f"Model {save_model_path} zapisany pomyślnie.")


import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from typing import Dict, Any, Tuple
import logging

class Generator(nn.Module):
    def __init__(self, latent_dim: int, output_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Linear(256, output_dim),
            nn.Sigmoid()
        )

    def forward(self, z):
        return self.net(z)

class Discriminator(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

class FairGANGenerator:
    """
    FairGAN-based generator for synthetic data generation.
    Note: This is an optional generator with lower interpretability, 
    used primarily for comparison against the controlled approach.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.latent_dim = config.get("latent_dim", 64)
        self.epochs = config.get("epochs", 50)
        self.batch_size = config.get("batch_size", 256)
        self.lr = config.get("learning_rate", 0.0002)
        
        self.generator = None
        self.discriminator = None
        self.preprocessor = None
        
        # Categorical and numerical columns
        from schema import CANDIDATE_ID, SKILLS, YEARS_EXPERIENCE, EDUCATION_LEVEL, LOCATION, PREFERRED_WORK_MODE, GENDER, RACE, SUITABILITY_SCORE
        self.num_cols = [SKILLS, YEARS_EXPERIENCE, SUITABILITY_SCORE]
        self.cat_cols = [EDUCATION_LEVEL, LOCATION, PREFERRED_WORK_MODE, GENDER, RACE]
        self.features = self.num_cols + self.cat_cols

    def fit(self, df: pd.DataFrame):
        logging.info("Training FairGAN Generator...")
        
        # Prepare data
        self.preprocessor = ColumnTransformer([
            ("num", StandardScaler(), self.num_cols),
            ("cat", OneHotEncoder(sparse_output=False, handle_unknown="ignore"), self.cat_cols)
        ])
        
        X = self.preprocessor.fit_transform(df[self.features])
        input_dim = X.shape[1]
        
        self.generator = Generator(self.latent_dim, input_dim)
        self.discriminator = Discriminator(input_dim)
        
        criterion = nn.BCELoss()
        opt_g = optim.Adam(self.generator.parameters(), lr=self.lr)
        opt_d = optim.Adam(self.discriminator.parameters(), lr=self.lr)
        
        X_tensor = torch.FloatTensor(X)
        dataset = torch.utils.data.TensorDataset(X_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        # Simplified training loop
        for epoch in range(self.epochs):
            for batch in dataloader:
                real_data = batch[0]
                b_size = real_data.size(0)
                
                # Train Discriminator
                opt_d.zero_grad()
                real_labels = torch.ones(b_size, 1)
                fake_labels = torch.zeros(b_size, 1)
                
                out_real = self.discriminator(real_data)
                loss_real = criterion(out_real, real_labels)
                
                z = torch.randn(b_size, self.latent_dim)
                fake_data = self.generator(z)
                out_fake = self.discriminator(fake_data.detach())
                loss_fake = criterion(out_fake, fake_labels)
                
                loss_d = loss_real + loss_fake
                loss_d.backward()
                opt_d.step()
                
                # Train Generator
                opt_g.zero_grad()
                out_fake_g = self.discriminator(fake_data)
                loss_g = criterion(out_fake_g, real_labels) # We want to fool D
                
                loss_g.backward()
                opt_g.step()

        logging.info("FairGAN training completed.")

    def generate(self, n_samples: int) -> pd.DataFrame:
        logging.info(f"Generating {n_samples} samples using FairGAN...")
        self.generator.eval()
        with torch.no_grad():
            z = torch.randn(n_samples, self.latent_dim)
            fake_data = self.generator(z)
            
            # Inverse transform
            # Note: This is a simplified inverse transform. A real GAN would handle 
            # reversing one-hot encoding robustly, but for this comparison generator,
            # we provide a best-effort inverse transform.
            df_fake = pd.DataFrame(self.preprocessor.inverse_transform(fake_data.numpy()), columns=self.features)
            
            from schema import CANDIDATE_ID
            df_fake[CANDIDATE_ID] = [f"GAN_{i:05d}" for i in range(n_samples)]
            
            return df_fake
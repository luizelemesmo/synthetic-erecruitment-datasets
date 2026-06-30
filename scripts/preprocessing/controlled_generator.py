import numpy as np
import pandas as pd
from typing import Dict, Any

from schema import (
    CANDIDATE_ID, SKILLS, YEARS_EXPERIENCE, EDUCATION_LEVEL,
    LOCATION, PREFERRED_WORK_MODE, GENDER, RACE, SUITABILITY_SCORE,
    WORK_MODES, GENDERS, RACES, EDUCATION_LEVELS, LOCATIONS
)

class ControlledGenerator:
    """
    Generator for synthetic e-recruitment data with controlled distributions.
    Allows generating 'biased', 'debiased', and 'extreme_bias' datasets based on configuration.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the generator with a given configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.config = config

    def generate(self, n_samples: int, mode: str) -> pd.DataFrame:
        """
        Generates the synthetic dataset.

        Args:
            n_samples (int): Number of samples to generate.
            mode (str): The bias scenario ('biased', 'debiased', 'extreme_bias').

        Returns:
            pd.DataFrame: The generated dataset.
        """
        df = pd.DataFrame()
        df[CANDIDATE_ID] = [f"CAND_{i:05d}" for i in range(n_samples)]

        # Generate non-sensitive features
        dist_cfg = self.config["distributions"]
        
        df[YEARS_EXPERIENCE] = np.clip(
            np.random.normal(dist_cfg["years_experience"]["mean"], dist_cfg["years_experience"]["std"], n_samples),
            dist_cfg["years_experience"]["min"],
            dist_cfg["years_experience"]["max"]
        ).round(1)

        df[SKILLS] = np.clip(
            np.random.normal(dist_cfg["skills"]["mean"], dist_cfg["skills"]["std"], n_samples),
            dist_cfg["skills"]["min"],
            dist_cfg["skills"]["max"]
        ).round(0)

        df[EDUCATION_LEVEL] = np.random.choice(EDUCATION_LEVELS, size=n_samples, p=dist_cfg["education_level_probs"])
        df[LOCATION] = np.random.choice(LOCATIONS, size=n_samples, p=dist_cfg["location_probs"])
        df[PREFERRED_WORK_MODE] = np.random.choice(WORK_MODES, size=n_samples, p=dist_cfg["work_mode_probs"])

        # Generate sensitive attributes
        sens_cfg = self.config["sensitive_probs"]
        
        if mode == "debiased":
            # In debiased mode, we force uniform distributions for sensitive attributes
            gender_probs = [1/len(GENDERS)] * len(GENDERS)
            race_probs = [1/len(RACES)] * len(RACES)
        else:
            gender_probs = sens_cfg["gender"]
            race_probs = sens_cfg["race"]

        df[GENDER] = np.random.choice(GENDERS, size=n_samples, p=gender_probs)
        df[RACE] = np.random.choice(RACES, size=n_samples, p=race_probs)

        # Calculate suitability score based on objective criteria
        base_score = (
            (df[YEARS_EXPERIENCE] / dist_cfg["years_experience"]["max"]) * 0.4 +
            (df[SKILLS] / dist_cfg["skills"]["max"]) * 0.4
        )
        
        ed_mapping = {"Ensino Médio": 0.1, "Bacharelado": 0.15, "Mestrado": 0.2, "Doutorado": 0.25}
        ed_score = df[EDUCATION_LEVEL].map(ed_mapping)
        base_score += ed_score

        # Add bias if mode is biased or extreme_bias
        if mode in ["biased", "extreme_bias"]:
            if mode == "extreme_bias" and "extreme_bias_effects" in self.config:
                bias_cfg = self.config["extreme_bias_effects"]
            else:
                bias_cfg = self.config["bias_effects"]
            
            gender_bias = df[GENDER].map(bias_cfg["gender"]).fillna(0)
            race_bias = df[RACE].map(bias_cfg["race"]).fillna(0)
            location_bias = df[LOCATION].map(bias_cfg["location"]).fillna(0)
            
            base_score += gender_bias + race_bias + location_bias

        # Add random noise
        noise = np.random.normal(0, self.config.get("noise_std", 0.1), n_samples)
        final_score = np.clip(base_score + noise, 0, 1)

        df[SUITABILITY_SCORE] = final_score

        return df
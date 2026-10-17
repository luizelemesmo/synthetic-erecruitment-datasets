from typing import List

# Features
CANDIDATE_ID = "id"
SKILLS = "skills" # number of skills or one-hot
YEARS_EXPERIENCE = "years_experience"
EDUCATION_LEVEL = "education_level"
LOCATION = "location"
PREFERRED_WORK_MODE = "preferred_work_mode"

# Sensitive Attributes
GENDER = "gender"
RACE = "race"

# Target Proxy
SUITABILITY_SCORE = "suitability_score"

# Categories
WORK_MODES = ["Presencial", "Híbrido", "Remoto"]
GENDERS = ["Masculino", "Feminino", "Não-binário"]
RACES = ["Branca", "Preta", "Parda", "Amarela", "Indígena"]
EDUCATION_LEVELS = ["Ensino Médio", "Bacharelado", "Mestrado", "Doutorado"]
LOCATIONS = ["Capitais", "Região Metropolitana", "Interior"]

def get_feature_columns() -> List[str]:
    """Returns the list of all feature columns in the generated dataset."""
    return [
        CANDIDATE_ID,
        SKILLS,
        YEARS_EXPERIENCE,
        EDUCATION_LEVEL,
        LOCATION,
        PREFERRED_WORK_MODE,
        GENDER,
        RACE,
        SUITABILITY_SCORE
    ]
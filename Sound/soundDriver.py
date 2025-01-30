import pygame
import sys
from pathlib import Path

#Dynamically get file paths
current_file = Path(__file__) # Path to this file
project_root = current_file.parent.parent # Path to Automated-Survival-Detection-Vehicle
sys.path.insert(0, str(project_root))

# Initialize pygame mixer
pygame.mixer.init()

# Load and play the MP3 file
pygame.mixer.music.load(project_root/"Sound/LifeCheck.mp3")
pygame.mixer.music.play()

# Keep the script running while the music plays
while pygame.mixer.music.get_busy():
    continue

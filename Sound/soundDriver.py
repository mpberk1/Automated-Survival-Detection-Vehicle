import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Load and play the MP3 file
pygame.mixer.music.load("/home/seed/490/Automated-Survival-Detection-Vehicle/Sound/LifeCheck.mp3")
pygame.mixer.music.play()

# Keep the script running while the music plays
while pygame.mixer.music.get_busy():
    continue

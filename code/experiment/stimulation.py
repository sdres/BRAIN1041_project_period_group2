"""Stimulation protocol for main experiment"""


import numpy as np
import pandas as pd
import soundfile as sf
import sounddevice as sd
from psychopy import sound, core, prefs, logging, event, visual, gui, monitors
from psychopy.hardware import emulator, keyboard
import time
import os


# Set stimulus parameters
base_freq = 2000
dur = 2  # In seconds
freq = 2000  # In Hz
sr = 48000  # sample rate (Hz)

# Define function that we will use to set the sound file on eah trial
def set_sound(freq, dur, sr):
    # Generate the time array
    t = np.linspace(0, dur, int(sr * dur), False)
    # Generate the sine wave
    sine_wave = np.sin(2 * np.pi * freq * t) * 0.5 # Increased amplitude
    # Normalize to 16-bit range
    audio = sine_wave * 32767 / np.max(np.abs(sine_wave))
    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    return audio



# Load a keyboard to enable abortion.
defaultKeyboard = keyboard.Keyboard()


# Set monitor information - CHECK WITH MPI:
distance_monitor = 99  # [99] in scanner
width_monitor = 30  # [30] in scanner
pix_width = 1920.0  # [1024.0] at Maastricht
pix_height = 1200.0  # [768.0] at Maastricht

moni = monitors.Monitor('testMonitor', width=width_monitor, distance=distance_monitor)
moni.setSizePix([pix_width, pix_height])  # [1920.0, 1080.0] in psychoph lab

# Get current date and time
date_now = time.strftime("%Y-%m-%d_%H.%M.%S")

background_color = [-0.5, -0.5, -0.5]  # from -1 (black) to 1 (white)

# Set screen:
win = visual.Window(size=(pix_width, pix_height),
                    screen=0,
                    winType='pyglet',  # winType : None, ‘pyglet’, ‘pygame’
                    allowGUI=False,
                    allowStencil=False,
                    fullscr=True,  # for psychoph lab: fullscr = True
                    monitor=moni,
                    color=background_color,
                    colorSpace='rgb',
                    units='deg',
                    blendMode='avg'
                    )


# Set initial text
instruction_text = visual.TextStim(
    win=win,
    color='white',
    height=0.5,
    text='Testing the stimulation setup. Press space'
)

end_text = visual.TextStim(
    win=win,
    color='white',
    height=0.5,
    text='Thats it.'
)


eval_text = visual.TextStim(
    win=win,
    color='white',
    height=0.5,
    text='Was the second frequency higher or lower than the first?\nPress 1 for higher or 2 for lower'
)


# Set baseline frequency sound
base_sound = set_sound(base_freq, dur, sr)



test_time = core.Clock()

# ================================================
# Actual testing

instruction_text.draw()
win.flip()

event.waitKeys(
    keyList=["space"],
    timeStamped=False
    )

# Start of experiment HERE
run_experiment = True

# Set starting frequency
curr_freq = 1000

while run_experiment:

    # Start of trial

    # Set current frequency (based on previous trial)
    curr_sound = set_sound(curr_freq, dur, sr)

    sd.play(base_sound, sr)
    core.wait(2)
    sd.play(curr_sound, sr)
    core.wait(2)

    for keys in event.getKeys():
        if keys in ['1']:
            # Freq was perceived to be higher
            logging.data('Key1 pressed')
            # Evaluate answer
            if curr_freq > base_freq:  # Answer correct
                logging.data('Answer correct')
                curr_freq -= (curr_freq/100) * 10  # Decreasing test frequency by 10 percent

        if curr_freq < base_freq:  # Answer NOT correct
            logging.data('Answer correct')
            curr_freq += (curr_freq / 100) * 10  # Increasing test frequency by 10 percent

        if keys in ['2']:
            # Freq was perceived to be lower
            logging.data('Key2 pressed')
            # Evaluate answer
            if curr_freq < base_freq:  # Answer correct
                logging.data('Answer correct')
                curr_freq += (curr_freq/100) * 10  # Increasing test frequency by 10 percent

            if curr_freq > base_freq:  # Answer NOT correct
                logging.data('Answer correct')
                curr_freq -= (curr_freq / 100) * 10  # Decreasing test frequency by 10 percent

end_text.draw()
win.flip()

core.wait(5)
win.close()
core.quit()

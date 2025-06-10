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
base_freq = 2000  # Frequency of the base stimulus in Hz
dur = 2  # Duration in seconds
sr = 48000  # sample rate (Hz)

# Define function that we will use to set the sound file on each trial
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


curr_path = os.getcwd()


# Presets for participant input
expInfo = {'participant': 'sub-0x',
           'run': 'run-0x',  # Put in run number of participant
           'type': ['upper', 'lower']  # Select whether we start low or high to define upper/ lower threshold
           }

# Load a GUI in which the preset parameters can be changed.
dlg = gui.DlgFromDict(dictionary=expInfo,
                      sortKeys=False,
                      title='test'
                      )

if dlg.OK == False:
    core.quit()  # Abort if user pressed cancel


# =============================================================================
# Prepare logfile

# Name and create specific subject folder for output
sub_folder_name = f"{curr_path}/misc/stim/{expInfo['participant']}"
if not os.path.isdir(sub_folder_name):
    os.makedirs(sub_folder_name)

# Define a name so the log-file so it can be attributed to subject/run
logfile_name = (f"{sub_folder_name}/{expInfo['participant']}_{expInfo['run']}_thresh-{expInfo['type']}_stimulation")

# Save a log file and set level for msg to be received
logfile = logging.LogFile(f'{logfile_name}.log', level=logging.INFO)

# Set console to receive warnings
logging.console.setLevel(logging.WARNING)

# Set monitor information - CHECK WITH MPI:
distance_monitor = 99  # [99] in scanner
width_monitor = 30  # [30] in scanner
pix_width = 1920.0  # [1024.0] at Maastricht
pix_height = 1200.0  # [768.0] at Maastricht

# Log monitor info
logfile.write('MonitorDistance=' + str(distance_monitor) + 'cm' + '\n')
logfile.write('MonitorWidth=' + str(width_monitor) + 'cm' + '\n')
logfile.write('PixelWidth=' + str(pix_width) + '\n')
logfile.write('PixelHeight=' + str(pix_height) + '\n')

# Set monitor presets
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


# Fixation dot - center [black]
fixation_dot = visual.Circle(
    win,
    autoLog=False,
    name='dotFix',
    units='deg',
    radius=0.075,
    fillColor=[0.0, 0.0, 0.0],
    lineColor=[0.0, 0.0, 0.0],
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

# Set prompt for participant after the trial
eval_text = visual.TextStim(
    win=win,
    color='white',
    height=0.5,
    text='Was the second frequency higher or lower than the first?\nPress 1 for higher or 2 for lower'
)

# Set baseline frequency sound
base_sound = set_sound(base_freq, dur, sr)

# Set starting frequency for test stimulus
if expInfo['type'] == 'upper':
    curr_freq = 3000
if expInfo['type'] == 'lower':
    curr_freq = 1000

logfile.write(f'Starting with frequency {curr_freq}')

test_time = core.Clock()

# ================================================
# Actual testing

logging.data(
    'StartOfRun '
    + str(expInfo['participant'])
    + '_'
    + str(expInfo['run'])
    )

instruction_text.draw()
win.flip()

event.waitKeys(
    keyList=["space"],
    timeStamped=False
    )

# Start of experiment HERE
run_experiment = True

trial_counter = 1
responses = []
logfile.write(f'\nBase frequency: {base_freq}\n')

while run_experiment:
    fixation_dot.draw()
    win.flip()

    # Start of trial
    logfile.write(f'\nTrial #{trial_counter}\n')
    logfile.write(f'Test frequency: {curr_freq}\n')

    # Set current frequency
    curr_sound = set_sound(curr_freq, dur, sr)

    sd.play(base_sound, sr)
    core.wait(2)
    sd.play(curr_sound, sr)
    core.wait(2)

    eval_text.draw()
    win.flip()
    core.wait(4)

    for keys in event.getKeys():

        # ====================================
        # Evaluate keys for upper threshold
        if expInfo['type'] == 'upper':
            if keys in ['1']:
                # Freq was perceived to be higher
                logfile.write('Key1 pressed\n')
                # Evaluate answer
                if curr_freq > base_freq:  # Answer correct
                    logfile.write('Answer correct\n')
                    curr_freq -= (curr_freq/100) * 10  # Decreasing test frequency by 10 percent
                    responses.append(1) # 1 for correct answer
                if curr_freq < base_freq:  # Answer NOT correct
                    logfile.write('Answer incorrect\n')
                    curr_freq += (curr_freq / 100) * 10  # Increasing test frequency by 10 percent
                    responses.append(0)  # 0 for incorrect answer

            if keys in ['2']:
                # Second frequency was perceived to be lower
                logfile.write('Key2 pressed\n')
                # Evaluate answer
                if curr_freq < base_freq:  # Answer correct
                    logfile.write('Answer correct\n')
                    curr_freq -= (curr_freq/100) * 10  # Decreasing test frequency by 10 percent
                    responses.append(1)

                if curr_freq > base_freq:  # Answer NOT correct
                    logfile.write('Answer incorrect\n')
                    curr_freq += (curr_freq / 100) * 10  # Increasing test frequency by 10 percent
                    responses.append(0)

        # ====================================
        # Evaluate keys for lower threshold
        if expInfo['type'] == 'lower':
            if keys in ['2']:
                # Freq was perceived to be higher
                logfile.write('Key1 pressed\n')
                # Evaluate answer
                if curr_freq > base_freq:  # Answer correct
                    logfile.write('Answer correct\n')
                    curr_freq -= (curr_freq / 100) * 10  # Decreasing test frequency by 10 percent
                    responses.append(1)
                if curr_freq < base_freq:  # Answer NOT correct
                    logfile.write('Answer incorrect\n')
                    curr_freq += (curr_freq / 100) * 10  # Increasing test frequency by 10 percent
                    responses.append(0)

            if keys in ['1']:
                # Second frequency was perceived to be lower
                logfile.write('Key2 pressed\n')
                # Evaluate answer
                if curr_freq < base_freq:  # Answer correct
                    logfile.write('Answer correct\n')
                    curr_freq -= (curr_freq / 100) * 10  # Decreasing test frequency by 10 percent
                    responses.append(1)

                if curr_freq > base_freq:  # Answer NOT correct
                    logfile.write('Answer incorrect\n')
                    curr_freq += (curr_freq / 100) * 10  # Increasing test frequency by 10 percent
                    responses.append(0)



        # Add break when after 8 trials no two consecutive trials had the same direction
        if len(responses) > 8:

            last_8 = responses[-8:]

            # Check for any two consecutive correct responses
            termination_counter = 0
            for i in range(len(last_8) - 1):
                if last_8[i] == 1 and last_8[i + 1] == 1:
                    termination_counter += 1
            if termination_counter < 1:
                run_experiment = False
                logfile.write('Not two consecutive correct responses in 8 trials')
                logfile.write('ending experiment')

        trial_counter += 1


    for keys in event.getKeys():
        if keys[0] in ['escape', 'q']:
            win.close()
            core.quit()


end_text.draw()
win.flip()

core.wait(5)
win.close()
core.quit()

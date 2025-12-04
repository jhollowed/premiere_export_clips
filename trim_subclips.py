import os
import re
import pdb
import glob
import math
import subprocess
import numpy as np

# ------ paths ------
pdir          = '/Users/joe/Movies/footage/Castleton/project/'
INPUT_FOLDER  = f'{pdir}motion_blurred_clips'       # folder with original clips
OUTPUT_FOLDER = f'{pdir}motion_blurred_final_clips' # output folder

# ------ video splitting config -------
SUB_CLIP_LENGTH = 5         # in seconds
OVERLAP         = 3         # in frames
VIDEO_CODEC     = 'libx264'
CRF             = 16
PRESET          = 'ultrafast'

dry = False

# -----------------------------------
# ------- helper functions ----------

def get_clip_duration(file_path):
    result = subprocess.run(['ffprobe', '-v', 'error', 
                             '-show_entries', 'format=duration', 
                             '-of', 'default=noprint_wrappers=1:nokey=1', 
                             file_path],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                             text=True)
    return float(result.stdout.strip())

def get_clip_fps(file_path):
    result = subprocess.run(['ffprobe', '-v', 'error', 
                             '-select_streams', 'v:0', 
                             '-show_entries', 'stream=avg_frame_rate',
                             '-of', 'default=noprint_wrappers=1:nokey=1', 
                             file_path],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                             text=True)
    return float(eval(result.stdout.strip()))

def trim_clip(file_path, overwrite=False):
    # trim the first OVERLAP frames off of the input clip
    
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    extension = os.path.splitext(file_name)[1]
    duration  = get_clip_duration(file_path)

    fps          = get_clip_fps(file_path)
    print(f'trimming first {OVERLAP} frames from {file_name}')
    
    start_time  = OVERLAP/fps
    clip_length = duration - start_time
    
    output_name = f'{base_name}_trimmed.mp4'
    output_path = os.path.join(OUTPUT_FOLDER, output_name)
    if(len(glob.glob(output_path)) > 0 and not overwrite):
        print(f'sub-clip {output_name} already exists; skipping')
        return

    cmd = ['ffmpeg', '-y',
           '-ss', f'{start_time:.8f}',
           '-i', file_path,
           '-t', f'{clip_length:.8f}',
           '-c:v', VIDEO_CODEC,
           '-crf', str(CRF),
           '-preset', PRESET,
           '-c:a', 'aac',
           output_path]
    if(not dry):
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f'ffmpeg failed with return code {e.errorcode}')
            print(e.stderr.decode())
            raise

# -----------------------------------------------
# ----------- preprocess all clips --------------
print('=== Preprocessing clips for AE ===')
overwrite=False

all_clips = sorted(glob.glob(f'{INPUT_FOLDER}/*.mp4'))
for i,clip in enumerate(all_clips):
    print(f'-------- processing clip {i+1}/{len(all_clips)}', end='\r')
    clip_name = clip.split('/')[-1]
    if('')
    if(clip_name.count('_') == 1):
        if(not dry):
            if(len(glob.glob(f'{OUTPUT_FOLDER}/{clip_name}')) == 0 or overwrite):
                os.symlink(clip, f'{OUTPUT_FOLDER}/{clip_name}')
    else:
        trim_clip(clip)



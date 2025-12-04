import os
import re
import pdb
import glob
import math
import subprocess
import numpy as np

# ------ paths ------
pdir               = '/Users/joe/Movies/footage/Castleton/project/'
INPUT_FOLDER       = f'{pdir}timeline_clips'       # folder with original clips
AE_READY_FOLDER    = f'{pdir}ae_ready_clips'     # intermediate folder for longs clips to be split
cdir               = '/Users/joe/repos/export_all_timeline_clips_premiere'
                     '/Contents/MacOS/After Effects'

# ------ video splitting config -------
SUB_CLIP_LENGTH = 5         # in seconds
OVERLAP         = 3         # in frames
VIDEO_CODEC     = 'libx264'
CRF             = 18
PRESET          = 'ultrafast'

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

def split_clip(file_path, overwrite=False):
    
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    extension = os.path.splitext(file_name)[1]
    duration  = get_clip_duration(file_path)
    # only split clips longer than SUB_CLIP_LENGTH
    # if shorter, then copy a symlink of the clip to the ae-ready dir
    if(duration <= SUB_CLIP_LENGTH):
        symlink_path = f'{AE_READY_FOLDER}/{base_name}_000{extension}'
        if not os.path.exists(symlink_path or overwrite):
            os.symlink(file_path, symlink_path)
        return
    
    fps          = get_clip_fps(file_path)
    num_subclips = math.ceil(duration / SUB_CLIP_LENGTH)
    print(f'clip {base_name} is {duration} s long; splitting into {num_subclips} subclips')
    
    for i in range(num_subclips):
        start_time = SUB_CLIP_LENGTH * i
        
        # add overlap to all sub-clips after the first
        if(i>0):
            start_time  -= OVERLAP/fps
            clip_length += OVERLAP/fps
        else:
            clip_length = SUB_CLIP_LENGTH
        clip_length = min(clip_length, duration - start_time)
        if clip_length <= 0:
            break
        
        output_name = f'{base_name}_{i:03d}.mp4'
        output_path = os.path.join(AE_READY_FOLDER, output_name)
        if(len(glob.glob(output_path)) > 0 and not overwrite):
            print(f'sub-clip {output_name} already exists; skipping')
            continue

        cmd = ['ffmpeg', '-y',
               '-ss', f'{start_time:.8f}',
               '-i', file_path,
               '-t', f'{clip_length:.8f}',
               '-c:v', VIDEO_CODEC,
               '-crf', str(CRF),
               '-preset', PRESET,
               '-c:a', 'aac',
               output_path]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f'ffmpeg failed with return code {e.errorcode}')
            print(e.stderr.decode())
            raise


# -----------------------------------------------
# ----------- preprocess all clips --------------
print('=== Preprocessing clips for AE ===')

all_clips = sorted(glob.glob(f'{INPUT_FOLDER}/*.mp4'))
for i,clip in enumerate(all_clips):
    print(f'-------- processing clip {i+1}/{len(all_clips)}', end='\r')
    split_clip(clip)



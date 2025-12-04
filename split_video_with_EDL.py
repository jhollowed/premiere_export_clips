import os
import re
import pdb
import glob
import subprocess
import numpy as np
from pathlib import Path

# ------ config ------
pdir          = '/Users/joe/Movies/footage/Castleton/project'
EDL_FILE      = f'{pdir}/Castleton_v1_30fps.edl'
FULL_VIDEO    = f'{pdir}/Castleton_v1_30fps.mp4'
OUTPUT_FOLDER    = f'{pdir}/timeline_clips'
OUTPUT_FORMAT = 'mp4'
FPS           = 30 # FPS of input video and EDL must match

overwrite = False

Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
cuts    = []
cuts_tc = []

def tc_to_seconds(tc):
    #Convert timecode HH:MM:SS:FF to seconds
    hh, mm, ss, ff = map(int, tc.split(":"))
    return (hh*3600 + mm*60 + ss + ff/FPS)

# ---------- parse EDL ----------
print(f'parsing EDL...')
with open(EDL_FILE, 'r') as f:
    for line in f:
        line = line.split()
        if (len(line) == 8):
            src_in, src_out, rec_in, rec_out = line[-4:]
            cuts_tc.append((rec_in, rec_out))
            cuts.append((tc_to_seconds(rec_in), tc_to_seconds(rec_out)))
cuts_sort = np.argsort([c[0] for c in cuts])
cuts      = np.array(cuts)[cuts_sort]
cuts_tc   = np.array(cuts_tc)[cuts_sort]
print(f'found {len(cuts)} cuts')

# ---------- cut input video using ffmpeg -------------
for i in range(len(cuts)):
    start, end = cuts[i][:]
    start_tc, end_tc = cuts_tc[i][:]
    duration = end - start
    out_name = f'clip_{str(i).zfill(4)}.{OUTPUT_FORMAT}'
    out_path = f'{OUTPUT_FOLDER}/{out_name}'
   
    
    if(len(glob.glob(out_path)) > 0 and not overwrite):
        print(f'file {out_name} exists; skipping')
        continue

    # get pix_fmt of input video
    cmd = ['ffprobe',
           '-v', 'error',
           '-select_streams', 'v:0',
           '-show_entries', 'stream=pix_fmt',
           '-of', 'default=nw=1:nk=1', 
           FULL_VIDEO]
    pix_fmt = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    cmd = ['ffmpeg',
           '-y',
           '-accurate_seek', 
           '-avoid_negative_ts', 'make_zero',
           '-ss', f'{start:.8f}',
           '-t', f'{duration:.8f}',
           '-i', FULL_VIDEO,
           '-c:v', 'libx264',
           '-preset', 'ultrafast',
           '-crf', '18', 
           '-pix_fmt', pix_fmt,
           '-c:a', 'copy',
           out_path]

    print(f'Exporting {out_name}  ({start_tc} → {end_tc})')
    #print(cmd)
    subprocess.run(cmd)

print('Done. All clips exported.')


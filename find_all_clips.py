import os
import re
import subprocess
from pathlib import Path

# --------------------
# CONFIG
# --------------------
EDL_FILE = "sequence.edl"            # Path to your exported EDL
FULL_VIDEO = "full_render.mov"       # Path to the full exported timeline video
OUTPUT_DIR = "clips"                 # Directory to save cut clips
OUTPUT_FORMAT = "mov"                # e.g., mov, mp4, etc.
PADDING = 3                          # 001, 002, 003…
FFMPEG_PATH = "ffmpeg"               # Change if ffmpeg isn't in PATH
# --------------------

Path(OUTPUT_DIR).mkdir(exist_ok=True)

timecode_re = re.compile(
    r'^\s*\d+\s+.+\s+V\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s*$'
)

def tc_to_seconds(tc):
    """Convert timecode HH:MM:SS:FF to seconds."""
    hh, mm, ss, ff = map(int, tc.split(":"))
    return hh * 3600 + mm * 60 + ss + ff / 24.0  # Assuming 24fps EDL
    # If your sequence is NOT 24fps, change the divisor accordingly!


cuts = []

# --------------------
# PARSE THE EDL
# --------------------
with open(EDL_FILE, "r") as f:
    for line in f:
        m = timecode_re.match(line)
        if m:
            reel, src_in, src_out, rec_in = m.groups()
            # rec_in = timeline start
            # rec_out must be obtained next line or interpreted as difference
            # But in CMX3600, rec_in and rec_out are in positions 3 and 4
            rec_out = src_out  # No — we MUST actually decode positions:

            # Correct parsing: positions 3 and 4 are record in/out
            # The regex groups:
            # group1 = source in
            # group2 = source out
            # group3 = record in  (timeline)
            # group4 = record out (timeline)
            src_in_tc = m.group(1)
            src_out_tc = m.group(2)
            rec_in_tc = m.group(3)
            rec_out_tc = m.group(4)

            cuts.append((rec_in_tc, rec_out_tc))

# Sort by timeline order (rec_in time)
cuts.sort(key=lambda c: tc_to_seconds(c[0]))

# --------------------
# CUT USING FFMPEG
# --------------------
for idx, (start_tc, end_tc) in enumerate(cuts, start=1):
    start_sec = tc_to_seconds(start_tc)
    end_sec = tc_to_seconds(end_tc)
    duration = end_sec - start_sec

    out_name = f"clip_{str(idx).zfill(PADDING)}.{OUTPUT_FORMAT}"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", FULL_VIDEO,
        "-ss", str(start_sec),
        "-t", str(duration),
        "-c", "copy",
        out_path
    ]

    print(f"Exporting {out_name}  ({start_tc} → {end_tc})")
    subprocess.run(cmd)

print("Done! All clips exported.")


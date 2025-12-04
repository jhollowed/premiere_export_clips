Use case:

You're editing a long video in Premiere, and realize that you forgot your ND filters. Every single clip needs motion blur added. The only way to convincingly do this is with AE's Pixel Motion Blur (PMB). So you need to export every clip from Premiere, and send them to AE for blurring. However, you also have basically no space left on your computer, and AE's PMB generates a massive cache for even a few seconds of high-resolution video. Here is the solution:

### Step 1:

    python ./split_video_with_EDL.py

Takes a single, long video and an accompanying EDL from premiere, and splits the video into individual clips, aligning with cuts in Premiere. This is necessary since it's basically impossible to natively export every clip from a timeline in Premiere, with effects and in/out points retained

By default, all clips from this step will be output to the location `OUTPUT_FOLDER` specified in the script.

### Step 2: 

    python ./split_long_clips.py

For any clips generated in Step 1 that are longer than 5 seconds, chop it up into segments of 5 seconds or less. Clips of this length will generate manageable cache sized when PMB is applied in AE

By default, all clips from this step will be output to the location `AE_READY_FOLDER` specified in the script. Any clips that are not long enough to require splitting are only symlinked to this folder. 

### Step 3:

We now need to prepare the AE environment. The script `apply pmb.jsx` works by being manually run on an existing project, which has a single clip in a composition with PMB applied and configured. The script renders one single clip from Step 2, then clears the cache, replaces the clip with the next one, and repeats. The PMB effect is retained in this process, and never needs to be touched again by the user or the script.The script makes several assumptions, including a composition name, source file name, and output module template name. 

In AE, create a new project, and a new composition called `MainComp`. Import one of the clips from Step 2, and name it `SOURCE`. Drag the clip into the timeline, and match the composition settings to the clip source. Apple the Pixel Motion Blur effect to the clip, and adjust all of the effect settings as desired. The effect with these settings will be applied to all clips.

Next, create a template Output Module. This is the easiest way for the script to set render settings, since a template module can be referenced by name. Go to

    Edit > Templates > Output Module...

In the `Settings` panel, click `New...`, and create the Output Module as desired. The name of the module must match the name specified in `apply_pmb.jsx`. As clones from this repo, the name is set to "CastletonMP4". Either match this name in AE, or update the name in `apply_pmb.jsx`.

Finally, export the clip. Choose your preferred Render Settings, and set the Output Module to the created template (`CastletonMP4` as default). Ensure that the render outputs as expected. The export location set here is where all of the batched clips wil go.

With this confirmed, we are ready to start the batch process. Do

    File > Scripts > Run Script File...

and select 

    apply_pmb.jsx

If everything was done correctly, you should be able to watch each clip be rendered one by one in AE.

### Step 4

When long clips are split into sub-clips in Step 2, the python script pads the beginning of each sub-clip (after the first) with 3 frames borrowed from the end of the previous sub-clip. This is done to preent artifacts in the motion blur applied at the start of each sub-clip (since PMB depends on the previous nighboring frames). These padded frames now need to be removed from the final output clips. Do

    python ./trim_subclips.py

By default, all clips from this step will be output to the location `OUTPUT_FOLDER` specified in the script. Any clips that did not need to have padded frames removed are only symlinked to this folder.

### Caveats

This code may not work out of the box, depending on your use case. It is configured to ingest MP4 clips with a framerate of 30 fps, and output MP4s. If using a different file format, or a different framerate, the source code will be modified.

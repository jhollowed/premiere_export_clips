// ================================
// Batch Render PMB with Imported Clips
// ================================

var outputFolder = new Folder("/Users/joe/Movies/footage/Castleton/project/motion_blurred_clips");
if (!outputFolder.exists) {
    outputFolder.create();
}

// ===== GET TEMPLATE COMP =====
var templateCompName = "MainComp";
var templateComp = null;
for (var i = 1; i <= app.project.numItems; i++) {
    var item = app.project.item(i);
    if ((item instanceof CompItem) && item.name === templateCompName) {
        templateComp = item;
        break;
    }
}

if (!templateComp) {
    alert("Template comp not found: " + templateCompName);
    throw new Error("Template comp not found");
}

// ===== GET ALL FOOTAGE ITEMS =====
var footageClips = [];
for (var i = 1; i <= app.project.numItems; i++) {
    var item = app.project.item(i);
    if ((item instanceof FootageItem) && item.mainSource.file) {
        footageClips.push(item);
    }
}

if (footageClips.length === 0) {
    alert("No imported footage found in project!");
    throw new Error("No imported footage found");
}

// ===== PROCESS EACH CLIP =====
for (var c = 0; c < footageClips.length; c++) {
    var clipItem = footageClips[c];

    var outputFileName = clipItem.name.replace(/\.[^\.]+$/, "") + ".mov";
    var outFile = new File(outputFolder.fsName + "/" + outputFileName);

    // Skip if output already exists
    if (outFile.exists) {
        $.writeln("Skipping existing render: " + outputFileName);
        continue;
    }

    // Duplicate template comp
    var newComp = templateComp.duplicate();
    newComp.name = clipItem.name.replace(/\.[^\.]+$/, "");

    // Replace placeholder layer (assumes layer 1) with the FootageItem
    var layer = newComp.layer(1);
    layer.replaceSource(clipItem, false);

    // Adjust comp and layer duration to match clip
    var clipDuration = clipItem.duration;
    newComp.duration = clipDuration;
    newComp.workAreaStart = 0;
    newComp.workAreaDuration = clipDuration;
    layer.inPoint = 0;
    layer.outPoint = clipDuration;

    // Add to Render Queue
    var rqItem = app.project.renderQueue.items.add(newComp);

    // Clone Render Settings from template comp
    var templateRQItem = templateComp.renderQueueItem;
    if (templateRQItem) {
        rqItem.renderSettings = templateRQItem.renderSettings;
    }

    // Force Output Module to ProRes422LT template
    try {
        rqItem.outputModule(1).applyTemplate("CastletonMP4");
    } catch (e) {
        alert("Output Module template 'CastletonMP4' not found! Please create it in AE first.");
        newComp.remove();
        throw new Error("Output Module template missing");
    }

    // Set output file
    rqItem.outputModule(1).file = outFile;

    // Render this comp
    app.project.renderQueue.render();

    // Purge memory + cache
    app.purge(PurgeTarget.ALL_CACHES);

    // Remove comp after rendering
    newComp.remove();
}

alert("All clips rendered with Pixel Motion Blur");


# Phosphene Experiments

Tracking experiments to optimize video quality and features.

## Experiment Log

| # | Experiment | Setting | Result | Notes |
|---|-----------|---------|--------|-------|
| 1 | Audio cues in prompt | Add sound descriptions | ✅ Yes | Audio generated (AAC, -41.8 dB mean) |
| 2 | No music checkbox | Enable ambient-only | ⏳ Pending | |
| 3 | HDR mode | Enable HDR | ⏳ Pending | |
| 4 | Balanced quality | Upgrade from Quick | ⏳ Pending | |
| 5 | CFG scale 2.0 | Lower than default 3.0 | ⏳ Pending | |
| 6 | CFG scale 4.0 | Higher than default 3.0 | ⏳ Pending | |
| 7 | Teacache 1.0 | Lower threshold | ⏳ Pending | |
| 8 | Teacache 2.5 | Higher threshold | ⏳ Pending | |
| 9 | Enhance prompt | Enable AI enhancement | ⏳ Pending | |
| 10 | Audio → Video mode | Audio-driven generation | ⏳ Pending | |

## Experiments

### Experiment 1: Audio Cues in Prompt

**Hypothesis:** Adding sound descriptions to the prompt will generate ambient audio with the video.

**Current:** No audio cues in prompt.

**New prompt:**
```
Medium shot at eye level. A young woman with long dark wavy hair sits at a wooden table, hands in her hair, head bowed in frustration. A laptop glows in front of her. Bright diffused light streams through a large white window behind her. The camera slowly pushes in. Soft keyboard typing, quiet sighs, distant traffic hum. Warm indoor tones, film grain. Frustration, exhaustion.
```

**Result:** ✅ Audio generated successfully (AAC, -41.8 dB mean, -18.3 dB max). Adding audio cues to the prompt activates LTX's audio generation.

**Key insight:** The prompt text field says: "Describe the scene AND the sound" — audio cues must be part of the prompt string, not a separate parameter.

---

### Experiment 2: No Music Checkbox

**Hypothesis:** Enabling "No music" will produce ambient-only audio without any musical score.

**Settings:**
```bash
-d "enhance=False"  # Prompt augmented with: 'Audio: voice and ambient sounds only, no music, no soundtrack, no score.'
```

**Result:** Pending

---

### Experiment 3: HDR Mode

**Hypothesis:** HDR will improve dynamic range and color depth.

**Settings:**
```bash
-d "hdr=True"
```

**Result:** Pending

---

### Experiment 4: Balanced Quality

**Hypothesis:** Balanced quality will produce better output than Quick with acceptable time increase.

**Settings:**
```bash
-d "quality=balanced"
```

**Result:** Pending

---

### Experiment 5: CFG Scale 2.0

**Hypothesis:** Lower CFG will give the model more creative freedom.

**Settings:**
```bash
-d "cfg_scale=2.0"
```

**Result:** Pending

---

### Experiment 6: CFG Scale 4.0

**Hypothesis:** Higher CFG will make the output follow the prompt more closely.

**Settings:**
```bash
-d "cfg_scale=4.0"
```

**Result:** Pending

---

### Experiment 7: Teacache Threshold 1.0

**Hypothesis:** Lower teacache threshold will improve quality at the cost of speed.

**Settings:**
```bash
-d "teacache_thresh=1.0"
```

**Result:** Pending

---

### Experiment 8: Teacache Threshold 2.5

**Hypothesis:** Higher teacache threshold will speed up generation with slight quality trade-off.

**Settings:**
```bash
-d "teacache_thresh=2.5"
```

**Result:** Pending

---

### Experiment 9: Enhance Prompt

**Hypothesis:** AI prompt enhancement will improve the generated video.

**Settings:**
```bash
-d "enhance=True"
```

**Result:** Pending

---

### Experiment 10: Audio → Video Mode

**Hypothesis:** Audio-driven generation will create videos synchronized to audio.

**Settings:**
- Upload audio file (WAV/MP3/M4A/FLAC)
- Optional reference image
- Aspect ratio and duration settings

**Result:** Pending

---

## Baseline

**Current best settings (proven):**
```bash
mode=i2v
quality=quick
upscale=off
video_skip_step=1
audio_skip_step=1
cfg_scale=3.0
teacache_thresh=1.8
hdr=False
enhance=False
```

**Reference image requirements:**
- Bright, well-lit scenes
- Indoor settings
- Clear human subjects
- Warm color tones

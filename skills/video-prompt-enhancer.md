---
name: video-prompt-enhancer
version: 1.0.0
description: Enhances prompts for AI video generation (LTX, Runway, Kling, Sora). Transforms bare-minimum descriptions into cinematic, professional-quality video prompts. Activates when user asks to improve, enhance, or write a video generation prompt.
tags: [video, prompting, ltx, cinematography, media-production]
related_skills: [prompt-engineering]
---

## Role

You are a senior AI video prompt engineer. Your job is to transform simple scene descriptions into rich, cinematic prompts that produce professional-quality video output.

## The 6-Element Framework

Every LTX/video prompt should contain these 6 elements, woven into **one flowing paragraph** (not bullet points):

### 1. Shot & Camera
Define the framing, camera movement, and end position.

**Shot scale:**
| Term | Description |
|------|-------------|
| Extreme close-up (ECU) | Fills frame with detail (eye, texture) |
| Close-up | Face or single object fills frame |
| Medium close-up | Head and shoulders |
| Medium shot | Waist up |
| Medium wide shot | Knees up, subject in context |
| Wide shot | Entire body with environment |
| Extreme wide shot | Subject small within vast environment |
| Establishing shot | Sets the scene |

**Camera movement:**
| Movement | Description | Best For |
|----------|-------------|----------|
| Static / tripod-locked | No movement | Dialogue, tension |
| Slow dolly in | Camera pushes forward | Intimacy, focus |
| Dolly out / pull back | Camera moves backward | Reveal, context |
| Pan left/right | Camera rotates horizontally | Follow action |
| Tilt up/down | Camera rotates vertically | Reveal scale |
| Tracking shot | Camera follows subject | Action, movement |
| Crane up/down | Camera rises/descends | Epic reveals |
| Handheld / shaky | Organic movement | Documentary, tension |
| Gimbal / steadicam | Smooth following | Flowing movement |
| Whip pan | Fast horizontal rotation | Energy, transitions |
| Orbit / arc | Camera circles subject | Drama, product |

**Lens/focal length:**
| Focal Length | Effect | Use Case |
|--------------|--------|----------|
| 16-24mm wide-angle | Exaggerated depth, dramatic | Landscapes, architecture |
| 35-50mm normal | Natural human perspective | General, documentary |
| 85mm portrait | Compressed, intimate | Portraits, interviews |
| 100mm+ telephoto | Highly compressed, isolated | Sports, wildlife |
| Macro | Extreme detail | Nature, textures |

### 2. Scene & Setting
Describe the environment with sensory details:

**Lighting quality:**
- Soft / diffused — gentle wrapping light
- Hard / direct — sharp shadows, high contrast
- Volumetric — visible light rays through fog/dust
- Dappled — light filtered through leaves
- Specular — bright highlights on reflective surfaces

**Light direction:**
- Front lighting — flat, even
- Side lighting — dramatic, reveals texture
- Backlighting — silhouettes, rim light
- Rembrandt lighting — 45° angle, triangle of light on cheek
- Butterfly / Paramount — overhead frontal

**Natural light conditions:**
- Golden hour — warm, low-angle sun
- Blue hour — cool twilight
- Overcast — soft, even
- Harsh midday — high contrast
- Candlelight — warm, flickering, intimate

**Atmosphere:**
- Fog, mist, haze, dust particles, smoke
- Rain, snow, steam, breath visible in cold

**Color palette:**
- Warm amber tones, cool blues, desaturated grays
- Film noir palette, pastel, jewel-toned, earthy

### 3. Subject & Character
Define with physical details, not abstract labels:

**Include:**
- Age and appearance: "A woman in her mid-30s with short dark hair"
- Clothing: "Wearing a yellow raincoat and rubber boots"
- Physical characteristics: "Tall and lean with angular features"
- Body language: "Her shoulders slump, head tilting downward"

**Rule:** Show emotion through physical cues, not labels.
- ❌ "She looks sad"
- ✅ "Her eyes lower, jaw tightens, she turns away"

### 4. Action (Present Tense)
Describe actions as a natural sequence from beginning to end:

**Rules:**
- Use present tense: "walks," "turns," "reaches"
- Describe in sequence: "She lifts the cup, brings it to her lips, then pauses"
- Include small details: "His fingers drum against the table"
- Show cause and effect: "The door swings open, revealing..."

**Connectors:** "as," "then," "while," "before," "after," "when"

### 5. Visual Style
Color science, textures, film characteristics:

**Style keywords:**
- Cinematic, documentary, film noir, arthouse
- Kodak Portra, ARRI Alexa, Sony FX3, RED Komodo
- Film grain, shallow depth of field, bokeh
- Desaturated, high contrast, warm tones

### 6. Audio (for models that support it)
Ambient sound, music, dialogue:

**Audio elements:**
- Ambient: "Distant traffic hum," "birds chirping"
- SFX: "Footsteps echoing on tile," "glass shattering"
- Music: "Soft piano melody," "melancholic strings"
- Dialogue: Use quotation marks: "Hello," she calls out
- Voice quality: "In a raspy whisper," "with a thick accent"

## Prompt Templates

### Therapy/Psychiatry Session
```
[Shot: Medium shot, slightly low angle] A [therapist/psychiatrist] sits in [setting details], [lighting]. The [therapist/patient] [action verb] [specific physical action]. [Camera movement]. [Atmosphere details]. [Visual style]. [Mood word].
```

**Example (enhanced):**
```
Medium shot from a slightly low angle. A psychiatrist in her early 40s sits in a leather chair, legs crossed, listening intently with her head tilted slightly. Warm afternoon sunlight streams through large windows behind her, casting soft golden shadows across the room lined with leather-bound books. The camera slowly pushes in, settling on a close-up of her face as she nods thoughtfully. Soft bokeh, warm amber tones, shallow depth of field. The faint sound of a clock ticking fills the quiet room. Intimate, contemplative.
```

### Portrait Video
```
[Shot type] of [subject with physical details], [clothing], [action with body language]. [Setting with lighting]. [Camera movement ending position]. [Color palette and style]. [Mood word].
```

**Example:**
```
Close-up at eye level. A contemplative psychiatrist in her mid-30s sits in a warm office, fingers steepled beneath her chin. Natural window light from the left illuminates her face, creating soft shadows on the right side. The camera holds perfectly still. Warm earth tones, leather chair visible in soft focus behind her. Film grain, shallow depth of field, 85mm portrait lens. Thoughtful, serene.
```

### Nature/Documentary
```
[Shot type], [lens description]. [Subject action in nature]. [Environment details with light]. [Camera holds/moves]. [Color palette]. [Audio description]. [Mood].
```

**Example:**
```
Extreme close-up, macro lens feel. A monarch butterfly lands on a milkweed leaf, wings slowly opening and closing. Morning dew glistens on the leaf surface. Camera holds perfectly still. Rich saturated greens and vivid orange. Natural diffused daylight filtering through the canopy. The ambient sound of distant birds and buzzing insects. Serene, detailed.
```

## Enhancement Process

When given a bare-minimum prompt, apply this transformation:

**Input:** `A therapy session`

**Step 1 — Add shot/camera:**
`Medium shot, eye level. A therapy session.`

**Step 2 — Add scene/setting:**
`Medium shot, eye level. A therapy session in a warmly lit office with bookshelves and a leather couch. Soft afternoon light.`

**Step 3 — Add subject details:**
`Medium shot, eye level. A psychiatrist in her 40s sits across from a patient on a leather couch. She holds a notebook, pen poised. Warm office with bookshelves. Soft afternoon light through windows.`

**Step 4 — Add action/body language:**
`Medium shot, eye level. A psychiatrist in her 40s sits across from a patient, notebook in hand. She leans forward slightly, eyes focused on the patient as they speak. The patient's hands gesture expressively. Warm office with bookshelves. Soft afternoon light through windows.`

**Step 5 — Add camera movement:**
`Medium shot, eye level. A psychiatrist in her 40s sits across from a patient, notebook in hand. She leans forward slightly, eyes focused as they speak. The patient's hands gesture expressively. Warm office with bookshelves. Soft afternoon light. Camera slowly pushes in, settling on the psychiatrist's face.`

**Step 6 — Add style/mood:**
`Medium shot, eye level. A psychiatrist in her 40s sits across from a patient, notebook in hand. She leans forward slightly, eyes focused as they speak. The patient's hands gesture expressively. Warm office with leather-bound bookshelves. Soft golden afternoon light through large windows. Camera slowly pushes in, settling on a close-up of the psychiatrist's face. Shallow depth of field, warm amber tones, film grain. Intimate, contemplative.`

## Anti-Patterns (What to Avoid)

| ❌ Don't | ✅ Do Instead |
|---------|-------------|
| "She looks sad" | "Her eyes lower, jaw tightens, she turns away" |
| "A person is happy" | "Her eyes light up, mouth curves into a wide smile" |
| Bullet points | One flowing paragraph |
| Past tense ("walked") | Present tense ("walks") |
| Emotional labels | Physical cues and body language |
| "Make the camera move" | "The camera slowly pushes in" |
| Overloaded scenes | One primary subject, one clear action |
| Conflicting lighting | Commit to one lighting setup |
| Vague ("a nice room") | Specific ("warm office with leather chairs and bookshelves") |

## Phosphene-Specific Settings

When generating with Phosphene's LTX model, always use Image → Video mode (`mode=i2v`) to avoid text artifacts. Key parameters:

```bash
-d "mode=i2v"
-d "video_skip_step=1"
-d "audio_skip_step=1"
-d "upscale=off"
```

See `IMAGE_TO_VIDEO_WORKFLOW.md` for complete workflow.

## Prompt Length Guidelines

| Duration | Prompt Length | Sentences |
|----------|---------------|-----------|
| 1-2s | Short | 2-3 sentences |
| 3-5s | Medium | 4-6 sentences |
| 5-10s | Long | 6-8 sentences |
| 10s+ | Extended | 8+ sentences with scene progression |

## Reference Files

| File | Use When |
|------|----------|
| `references/camera-vocabulary.md` | Need full camera movement reference |
| `references/lighting-keywords.md` | Need lighting terminology |
| `references/style-keywords.md` | Need visual style vocabulary |

## Sources

- LTX-2.3 Official Prompt Guide (ltx.io)
- Film Fun Academy LTX-Video Prompting Guide
- Vidzy AI Prompt Keywords Cheat Sheet
- Community best practices from r/StableDiffusion
- Prompt-Master by nidhinjs (7.9k+ stars)

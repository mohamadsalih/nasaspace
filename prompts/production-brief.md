# ORBIT – generation prompts

Paste-ready prompts for a text-to-video model, a voice actor or TTS voice, and a
music generator. Shot ids match `build.py`; save each result under the path shown.

Generate every shot **without any on-screen text, subtitles, logos or watermarks**.
The ORBIT name, zone captions, end card and Arabic subtitles are added by `build.py`,
so they are always spelled correctly.

## Shared blocks

Append **STYLE** to every video prompt. Append **BUILDING** to every shot that shows
the exterior (s3, s6), and use one approved still of the building as the image
reference for both, so the architecture stays identical.

**STYLE**
> Ultra-realistic cinematic footage, science-documentary look combined with a premium
> commercial. 16:9, 4K, 24 fps, anamorphic lens character, shallow depth of field,
> smooth stabilised camera movement. Colour palette: deep navy blue, cosmic black,
> glowing electric blue, clean white, subtle purple accents. Cinematic lighting,
> realistic reflections, light atmospheric haze. Natural-looking people of diverse
> ages and backgrounds with correct faces and hands. No text, no signage lettering,
> no logos, no agency insignia, no watermark.

**BUILDING**
> The ORBIT space center: a realistic, buildable contemporary science-museum campus
> on Earth. A low white central dome ringed by a single sweeping elevated circular
> walkway of glass and brushed aluminium, like a planetary ring, with two curved
> glass exhibition wings and a landscaped entrance plaza with reflecting pools.
> Thin lines of electric-blue architectural lighting trace the ring. Set in open
> landscape under a wide sky. Achievable present-day architecture, not an alien city,
> no floating structures.

**NEGATIVE**
> text, captions, subtitles, logos, NASA insignia, watermark, distorted faces,
> malformed hands, extra fingers, unreadable signs, cartoon style, alien city,
> floating buildings, fantasy architecture, lens dirt, flicker, jump cuts

## Shots

Minimum lengths include the 0.5 s crossfade tail (`python3 build.py --list`).
Longer clips are trimmed from the start.

| File | Slot | Min length | Prompt |
|---|---|---|---|
| `clips/s1.mp4` | 0–8 s | 8.5 s | Breathtaking view of Earth from orbit against distant galaxies, bright stars and a soft purple-blue nebula. The camera glides slowly toward Earth, sunlight breaking over the curved horizon and lighting the thin blue atmosphere. Slow push-in, awe-inspiring. |
| `clips/s2.mp4` | 8–15 s | 7.5 s | Interior of an ordinary school classroom and a traditional museum hall: students and a family look at framed space photographs, a static planet poster and a simple glass display case. Curious faces, flat neutral lighting, slow lateral dolly. Toward the end a cool electric-blue glow begins to rise across the room. |
| `clips/s3.mp4` | 15–23 s | 8.5 s | Spectacular sweeping aerial reveal at golden hour: the camera rises over a ridge and arcs around the entire building, revealing it in full. Leave calm sky in the upper-centre of frame for a title. + BUILDING |
| `clips/s4a.mp4` | 23–26.4 s | 3.9 s | Inside a dark dome hall, visitors and children walk among large realistic 3D planet models suspended in the air, an interactive solar-system display and cosmic projections on the walls. Slow forward tracking shot. |
| `clips/s4b.mp4` | 26.4–29.8 s | 3.9 s | Inside a realistic full-scale space-station module mock-up: white panelled interior, equipment racks, a round window showing Earth. A guide in a plain blue flight suit shows students an interactive console. Gentle floating camera move. |
| `clips/s4c.mp4` | 29.8–33.2 s | 3.9 s | A large indoor simulated lunar surface: grey regolith, craters, low hard sidelight, black sky backdrop with Earth. A family in visitor jackets walks across it leaving footprints. Low tracking shot. |
| `clips/s4d.mp4` | 33.2–36.6 s | 3.9 s | A vast indoor Mars environment: red rocky terrain, dusty orange light, a realistic exploration rover. Students follow a guide across the terrain. Wide crane shot moving forward. |
| `clips/s4e.mp4` | 36.6–40 s | 3.9 s | A dark control-room-style gallery with a huge curved screen showing satellite imagery of Earth, cloud systems and city lights; visitors point at glowing data visualisations. Slow pull-back. |
| `clips/s5a.mp4` | 40–45 s | 5.5 s | Children and teenagers wearing VR headsets reach out with delight in a softly lit blue room, while beside them a family uses a large interactive touchscreen showing a rotating planet. Close, warm, handheld-smooth camera, genuine excitement. |
| `clips/s5b.mp4` | 45–50 s | 5.5 s | An immersive 360° projection room: a group of students stands surrounded by a projected galaxy, a girl touches a holographic-style augmented-reality planet model, faces lit in blue and white, expressions of wonder. Slow orbiting camera. |
| `clips/s6.mp4` | 50–60 s | 10 s | Magnificent wide night shot of the complete building, illuminated in elegant blue and white, students and families walking across the plaza toward the entrance. From second 4 the camera tilts slowly upward, leaving the building, into a clear star-filled sky and holds on the stars for the final 4 seconds. + BUILDING |

## Narration

One professional English male voice: deep, rich, mature and authoritative, cinematic
documentary delivery, clear American or neutral international pronunciation, measured
pace with natural pauses, inspiring but not theatrical. Record dry (no music, no reverb)
at 48 kHz.

Deliver one file per line as `audio/vo/01.wav` … `08.wav`; the build places each at its
start time, which keeps the Arabic subtitles in sync. (A single 60 s take as
`audio/voiceover.wav` also works, but must then match the timings itself.)

| File | Starts | Must fit in | Line |
|---|---|---|---|
| `01` | 1.5 s | 5.7 s | Have you ever imagined exploring the universe without ever leaving Earth? |
| `02` | 8.3 s | 6.4 s | Despite incredible advances in space science, exploring the universe remains out of reach for many. |
| `03` | 15.6 s | 6.8 s | Introducing ORBIT — a new destination where education meets the extraordinary world of space exploration. |
| `04` | 23.4 s | 6.2 s | From discovering distant planets to experiencing life aboard a space station, |
| `05` | 30.4 s | 5.8 s | from walking on the Moon to exploring the mysteries of Mars. |
| `06` | 39.4 s | 5.8 s | Through immersive technology and interactive experiences, we transform scientific knowledge into unforgettable adventures. |
| `07` | 46.4 s | 8.8 s | Our mission is not just to teach people about space, but to inspire the next generation to become part of its future. |
| `08` | 56.0 s | 3.6 s | ORBIT — bringing the universe closer to everyone. |

## Music

Save as `audio/music.wav`, 60 s or longer, instrumental only.

> Inspiring cinematic orchestral score, exactly 60 seconds, instrumental. 0–8 s: soft,
> mysterious opening with airy space ambience and a low sustained pad. 8–15 s: gentle
> piano and warm strings, subtle futuristic electronic textures. 15–23 s: powerful but
> elegant orchestral swell with brass and a deep cinematic hit at 15 s. 23–50 s:
> flowing, uplifting momentum with light pulsing synths and strings. 50–60 s: broad,
> emotional, memorable resolution ending on a sustained final chord. Hopeful and
> prestigious, no aggressive percussion, no vocals, no action-trailer intensity.

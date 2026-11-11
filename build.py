#!/usr/bin/env python3
"""Assemble the 60-second ORBIT promo from scene clips, narration and music.

Single source of truth for the timeline: edit SHOTS / CUES here, then re-run.
Missing clips are replaced by labelled placeholders so the edit can be
previewed before all footage exists. Requires only ffmpeg (with libass).
"""
import argparse
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DURATION = 60.0
FPS = 24
XFADE = 0.5  # crossfade length; each clip must cover its slot plus this tail

# (id, start, end, storyboard title, on-screen zone label or None)
SHOTS = [
    ("s1", 0.0, 8.0, "THE WONDER OF SPACE", None),
    ("s2", 8.0, 15.0, "THE PROBLEM", None),
    ("s3", 15.0, 23.0, "INTRODUCING ORBIT", None),
    ("s4a", 23.0, 26.4, "SOLAR SYSTEM ZONE", "SOLAR SYSTEM ZONE"),
    ("s4b", 26.4, 29.8, "SPACE STATION ZONE", "SPACE STATION ZONE"),
    ("s4c", 29.8, 33.2, "MOON EXPLORATION ZONE", "MOON EXPLORATION ZONE"),
    ("s4d", 33.2, 36.6, "MARS EXPLORATION ZONE", "MARS EXPLORATION ZONE"),
    ("s4e", 36.6, 40.0, "EARTH OBSERVATION ZONE", "EARTH OBSERVATION ZONE"),
    ("s5a", 40.0, 45.0, "TECHNOLOGY MEETS EDUCATION 1", None),
    ("s5b", 45.0, 50.0, "TECHNOLOGY MEETS EDUCATION 2", None),
    ("s6", 50.0, 60.0, "THE VISION AND FINAL BRANDING", None),
]

# (start, end, English narration, Arabic subtitle lines)
CUES = [
    (1.5, 7.2,
     "Have you ever imagined exploring the universe without ever leaving Earth?",
     ["هل تخيلت يوماً أن تستكشف الكون دون أن تغادر الأرض؟"]),
    (8.3, 14.7,
     "Despite incredible advances in space science, exploring the universe "
     "remains out of reach for many.",
     ["رغم التطور الهائل في علوم الفضاء،",
      "لا يزال استكشاف الكون بعيد المنال بالنسبة للكثيرين."]),
    (15.6, 22.4,
     "Introducing ORBIT — a new destination where education meets the "
     "extraordinary world of space exploration.",
     ["نقدم لكم ORBIT، وجهة جديدة",
      "يلتقي فيها التعليم بعالم استكشاف الفضاء المذهل."]),
    (23.4, 29.6,
     "From discovering distant planets to experiencing life aboard a space station,",
     ["من اكتشاف الكواكب البعيدة",
      "إلى تجربة الحياة داخل المحطات الفضائية،"]),
    (30.4, 36.2,
     "from walking on the Moon to exploring the mysteries of Mars.",
     ["ومن السير على سطح القمر",
      "إلى استكشاف أسرار المريخ."]),
    (39.4, 45.2,
     "Through immersive technology and interactive experiences, we transform "
     "scientific knowledge into unforgettable adventures.",
     ["من خلال التكنولوجيا الغامرة والتجارب التفاعلية،",
      "نحول المعرفة العلمية إلى مغامرات لا تُنسى."]),
    (46.4, 55.2,
     "Our mission is not just to teach people about space, but to inspire the "
     "next generation to become part of its future.",
     ["مهمتنا ليست فقط تعليم الناس عن الفضاء،",
      "بل إلهام الجيل القادم ليكون جزءاً من مستقبله."]),
    (56.0, 59.6,
     "ORBIT — bringing the universe closer to everyone.",
     ["ORBIT — نجعل الكون أقرب إلى الجميع."]),
]

TITLE = "ORBIT"
SUBTITLE = "EDUCATIONAL & TOURISM SPACE CENTER"
TAGLINE = "BRINGING THE UNIVERSE CLOSER TO EVERYONE."

VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm")
AUDIO_EXT = (".wav", ".mp3", ".m4a", ".flac", ".aac")
# Forces right-to-left base direction on lines that start with Latin text.
RLM = "\u200f"


def find(stem, exts):
    for ext in exts:
        p = ROOT / (stem + ext)
        if p.exists():
            return p
    return None


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def slot_length(i):
    _, start, end, _, _ = SHOTS[i]
    return end - start + (XFADE if i < len(SHOTS) - 1 else 0.0)


# ---------------------------------------------------------------- subtitles

def srt_time(t):
    ms = round(t * 1000)
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60,
                                    ms // 1000 % 60, ms % 1000)


def ass_time(t):
    cs = round(t * 100)
    return "%d:%02d:%02d.%02d" % (cs // 360000, cs // 6000 % 60,
                                  cs // 100 % 60, cs % 100)


def write_srt(path, arabic):
    blocks = []
    for n, (start, end, en, ar) in enumerate(CUES, 1):
        text = "\n".join(RLM + line for line in ar) if arabic else en
        blocks.append("%d\n%s --> %s\n%s\n" % (n, srt_time(start), srt_time(end), text))
    path.write_text("\n".join(blocks), encoding="utf-8")


def ellipse(rx, ry):
    """ASS vector drawing of an ellipse (four Béziers), origin at top-left."""
    k = 0.5523
    pts = [(rx, 0), (rx, ry * k), (rx * k, ry), (0, ry),
           (-rx * k, ry), (-rx, ry * k), (-rx, 0),
           (-rx, -ry * k), (-rx * k, -ry), (0, -ry),
           (rx * k, -ry), (rx, -ry * k), (rx, 0)]
    p = ["%d %d" % (round(x + rx), round(y + ry)) for x, y in pts]
    return "m %s b %s b %s b %s b %s" % (
        p[0], " ".join(p[1:4]), " ".join(p[4:7]), " ".join(p[7:10]), " ".join(p[10:13]))


def logo_events(cx, cy, start, end, fade):
    """Orbit mark: a planet with a tilted ring passing behind and in front."""
    rx, ry, tilt, core, moon = 330, 112, 20, 78, 20
    a = math.radians(tilt)
    dx, dy = math.cos(a), -math.sin(a)      # ring major axis on screen
    px, py = math.sin(a), math.cos(a)       # towards the viewer-side half
    far = 2000
    front = [(cx - far * dx, cy - far * dy), (cx + far * dx, cy + far * dy),
             (cx + far * (dx + px), cy + far * (dy + py)),
             (cx - far * (dx - px), cy - far * (dy - py))]
    clip = "m %d %d l %s" % (front[0][0], front[0][1],
                             " ".join("%d %d" % pt for pt in front[1:]))
    t = math.radians(38)
    mx, my = rx * math.cos(t), ry * math.sin(t)
    moon_x = cx + mx * math.cos(a) + my * math.sin(a)
    moon_y = cy - mx * math.sin(a) + my * math.cos(a)
    ring = ("{\\an5\\pos(%d,%d)\\frz%d\\1a&HFF&\\bord5\\shad0\\3c&HFFA93D&\\blur1%s%s\\p1}"
            + ellipse(rx, ry))
    disc = "{\\an5\\pos(%d,%d)\\bord0\\shad0\\1c&H%s&\\blur1%s\\p1}%s"
    ev = "Dialogue: %d,%s,%s,Brand,,0,0,0,,%s"
    s, e = ass_time(start), ass_time(end)
    return [
        ev % (0, s, e, ring % (cx, cy, tilt, fade, "")),
        ev % (1, s, e, disc % (cx, cy, "FFFFFF", fade, ellipse(core, core))),
        ev % (2, s, e, ring % (cx, cy, tilt, fade, "\\clip(%s)" % clip)),
        ev % (3, s, e, disc % (moon_x, moon_y, "FF7B9B", fade, ellipse(moon, moon))),
    ]


def write_ass(path, with_subs=True):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,IBM Plex Sans Arabic Medium,88,&H00FFFFFF,&H00FFFFFF,&H50100803,&H78000000,0,0,0,0,100,100,0,0,1,4,3,2,400,400,180,-1
Style: Brand,Michroma,60,&H00FFFFFF,&H00FFFFFF,&H64281205,&H78000000,0,0,0,0,100,100,0,0,1,2,4,5,0,0,0,1
Style: Zone,Michroma,44,&H00FFFFFF,&H00FFFFFF,&H64281205,&H78000000,0,0,0,0,100,100,10,0,1,2,3,7,220,220,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    brand = "Dialogue: 5,%s,%s,Brand,,0,0,0,,{\\pos(%d,%d)\\fs%d\\fsp%d%s}%s"

    def text(start, end, y, size, spacing, extra, s):
        # \fsp also pads the last glyph, so shift right by half to stay centred
        ev.append(brand % (ass_time(start), ass_time(end), 1920 + spacing // 2, y,
                           size, spacing, extra, s))

    # Scene 3: name reveal over the aerial shot
    text(17.4, 22.6, 800, 230, 70, "\\fad(900,500)\\blur0.6", TITLE)
    text(18.0, 22.6, 990, 58, 16, "\\fad(900,500)", SUBTITLE)

    # Scene 4: zone captions
    for _, start, end, _, label in SHOTS:
        if label:
            ev.append("Dialogue: 4,%s,%s,Zone,,0,0,0,,{\\fad(350,350)\\1c&HFFA93D&}—  {\\1c&HFFFFFF&}%s"
                      % (ass_time(start + XFADE), ass_time(end), label))

    # Scene 6: end card
    ev += logo_events(1920, 600, 55.0, DURATION, "\\fad(1000,0)")
    text(55.4, DURATION, 940, 200, 64, "\\fad(1000,0)\\blur0.6", TITLE)
    text(55.8, DURATION, 1105, 56, 16, "\\fad(1000,0)", SUBTITLE)
    text(56.4, DURATION, 1250, 50, 10, "\\fad(1000,0)\\1c&HFFA93D&", TAGLINE)

    if with_subs:
        for start, end, _, ar in CUES:
            ev.append("Dialogue: 9,%s,%s,Sub,,0,0,0,,{\\fad(180,180)\\blur0.8}%s"
                      % (ass_time(start), ass_time(end),
                         "\\N".join(RLM + line for line in ar)))
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ------------------------------------------------------------------- ffmpeg

def build(args):
    width, height = (1920, 1080) if args.preview else (3840, 2160)
    sub_dir = ROOT / "subtitles"
    sub_dir.mkdir(exist_ok=True)
    write_srt(sub_dir / "orbit_ar.srt", arabic=True)
    write_srt(sub_dir / "orbit_en.srt", arabic=False)
    write_ass(sub_dir / "orbit_burnin.ass", with_subs=True)
    write_ass(sub_dir / "orbit_branding_only.ass", with_subs=False)
    if args.subs_only:
        return 0
    overlay = "orbit_branding_only.ass" if args.no_subs else "orbit_burnin.ass"

    inputs, graph, warnings = [], [], []

    def add_input(*opts):
        inputs.extend(opts)
        return (len([o for o in inputs if o == "-i"]) - 1)

    # --- video: normalise each shot, then chain crossfades at the cut points
    for i, (sid, start, end, title, _) in enumerate(SHOTS):
        need = slot_length(i)
        clip = find("clips/" + sid, VIDEO_EXT)
        norm = ("fps=%d,scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,"
                "setsar=1,tpad=stop_mode=clone:stop_duration=%g,trim=duration=%g,"
                "setpts=PTS-STARTPTS,format=yuv420p" % (FPS, width, height, width, height,
                                                        need, need))
        if clip:
            have = probe_duration(clip)
            if have + 0.05 < need:
                warnings.append("%s is %.2fs, needs %.2fs: last frame will be held"
                                % (clip.relative_to(ROOT), have, need))
            n = add_input("-i", str(clip.relative_to(ROOT)))
            graph.append("[%d:v]%s[v%d]" % (n, norm, i))
        else:
            warnings.append("clips/%s.mp4 missing (%.2fs needed): using placeholder" % (sid, need))
            n = add_input("-f", "lavfi", "-i",
                          "gradients=s=640x360:c0=0x02040f:c1=0x0b1d4d:c2=0x241250:"
                          "nb_colors=3:speed=0.008:seed=%d:r=%d:d=%g" % (i + 1, FPS, need))
            label = "PLACEHOLDER %s - %s" % (sid, title)
            graph.append("[%d:v]%s,drawtext=fontfile=assets/fonts/Michroma-Regular.ttf:"
                         "text='%s':fontcolor=white@0.3:fontsize=h/34:x=(w-tw)/2:y=h*0.68[v%d]"
                         % (n, norm, label, i))
    prev = "v0"
    for i in range(1, len(SHOTS)):
        out = "x%d" % i
        graph.append("[%s][v%d]xfade=transition=fade:duration=%g:offset=%g[%s]"
                     % (prev, i, XFADE, SHOTS[i][1], out))
        prev = out
    graph.append("[%s]ass=subtitles/%s:fontsdir=assets/fonts,"
                 "fade=t=in:st=0:d=1.2,fade=t=out:st=%g:d=0.5,format=yuv420p[vout]"
                 % (prev, overlay, DURATION - 0.5))

    # --- narration: one file per cue (kept in sync by construction) or one full take
    vo_parts = []
    for n, (start, end, _, _) in enumerate(CUES, 1):
        f = find("audio/vo/%02d" % n, AUDIO_EXT)
        if f:
            d = probe_duration(f)
            limit = (CUES[n][0] if n < len(CUES) else DURATION) - start
            if d > limit:
                warnings.append("%s is %.2fs but only %.2fs is free before the next line"
                                % (f.relative_to(ROOT), d, limit))
            k = add_input("-i", str(f.relative_to(ROOT)))
            graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,"
                         "adelay=%d:all=1[vo%d]" % (k, round(start * 1000), n))
            vo_parts.append("[vo%d]" % n)
    full_vo = find("audio/voiceover", AUDIO_EXT)
    if vo_parts:
        if len(vo_parts) < len(CUES):
            warnings.append("only %d of %d narration lines found in audio/vo/"
                            % (len(vo_parts), len(CUES)))
        graph.append("%samix=inputs=%d:normalize=0[vo]" % ("".join(vo_parts), len(vo_parts)))
    elif full_vo:
        k = add_input("-i", str(full_vo.relative_to(ROOT)))
        graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo[vo]" % k)
    else:
        warnings.append("no narration found (audio/vo/01..08 or audio/voiceover.*): silent")
        k = add_input("-f", "lavfi", "-t", str(DURATION), "-i",
                      "anullsrc=r=48000:cl=stereo")
        graph.append("[%d:a]anull[vo]" % k)

    # --- music: kept under the voice and ducked further while it speaks
    music = find("audio/music", AUDIO_EXT)
    if music:
        k = add_input("-i", str(music.relative_to(ROOT)))
        graph.append("[vo]asplit[vomix][vokey]")
        graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%g,"
                     "afade=t=in:st=0:d=1.5,afade=t=out:st=%g:d=2.5[mus]"
                     % (k, args.music_volume, DURATION - 2.5))
        graph.append("[mus][vokey]sidechaincompress=threshold=0.02:ratio=6:"
                     "attack=120:release=700[duck]")
        graph.append("[vomix][duck]amix=inputs=2:normalize=0[mix]")
    else:
        warnings.append("no audio/music.* found: no music bed")
        graph.append("[vo]anull[mix]")
    graph.append("[mix]alimiter=limit=0.95,apad,atrim=duration=%g[aout]" % DURATION)

    out = ROOT / "out" / ("orbit_promo_preview.mp4" if args.preview else "orbit_promo_4k.mp4")
    out.parent.mkdir(exist_ok=True)
    codec = (["-preset", "veryfast", "-crf", "23"] if args.preview
             else ["-preset", "medium", "-crf", "17"])
    cmd = (["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y"] + inputs +
           ["-filter_complex", ";".join(graph), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264"] + codec +
           ["-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(int(DURATION * FPS)),
            "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out)])
    for w in warnings:
        print("warning:", w, file=sys.stderr)
    code = subprocess.run(cmd, cwd=ROOT).returncode
    if code == 0:
        print("wrote %s (%dx%d, %.3fs)" % (out.relative_to(ROOT), width, height,
                                           probe_duration(out)))
    return code


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--preview", action="store_true", help="fast 1080p render")
    ap.add_argument("--no-subs", action="store_true",
                    help="burn in branding only; use subtitles/orbit_ar.srt as a sidecar")
    ap.add_argument("--subs-only", action="store_true",
                    help="regenerate the subtitle files and exit")
    ap.add_argument("--list", action="store_true", help="print the clip checklist and exit")
    ap.add_argument("--music-volume", type=float, default=0.35)
    args = ap.parse_args()
    if args.list:
        for i, (sid, start, end, title, _) in enumerate(SHOTS):
            print("clips/%-4s %5.1f-%5.1fs  min length %.1fs  %s"
                  % (sid, start, end, slot_length(i), title))
        return 0
    return build(args)


if __name__ == "__main__":
    sys.exit(main())

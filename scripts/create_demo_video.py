from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "video_demo"
FRAMES_DIR = OUT_DIR / "frames"
DEFAULT_OUT = OUT_DIR / "cellforge_ai_demo_silent.mp4"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], font_obj, fill: str, width: int, line_gap: int = 10) -> int:
    x, y = xy
    chars = max(18, int(width / (font_obj.size * 0.55)))
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            y += font_obj.size + line_gap
            continue
        for line in wrap(paragraph, chars):
            draw.text((x, y), line, font=font_obj, fill=fill)
            y += font_obj.size + line_gap
    return y


def render_slide(index: int, title: str, subtitle: str, bullets: list[str], footer: str, accent: str = "#18a058") -> Path:
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), "#0b1020")
    draw = ImageDraw.Draw(img)

    # Background bands.
    draw.rectangle((0, 0, width, height), fill="#0b1020")
    draw.rectangle((0, 0, width, 92), fill="#101827")
    draw.rectangle((0, height - 86, width, height), fill="#101827")
    draw.rectangle((0, 92, 18, height - 86), fill=accent)
    draw.ellipse((1420, 105, 2050, 735), fill="#10253a")
    draw.ellipse((1510, 190, 1940, 620), fill="#0f3231")

    title_font = font(62, bold=True)
    subtitle_font = font(34)
    bullet_font = font(36)
    small_font = font(25)
    label_font = font(28, bold=True)

    draw.text((72, 24), "CellForge AI", font=label_font, fill="#d1fae5")
    draw.text((1550, 25), f"Demo slide {index:02d}", font=small_font, fill="#a7f3d0")
    draw.text((88, 150), title, font=title_font, fill="#f8fafc")
    y = draw_wrapped(draw, subtitle, (92, 245), subtitle_font, "#cbd5e1", 1280, line_gap=12)
    y += 42

    for bullet in bullets:
        draw.ellipse((100, y + 12, 122, y + 34), fill=accent)
        y = draw_wrapped(draw, bullet, (145, y), bullet_font, "#f8fafc", 1320, line_gap=12)
        y += 22

    draw.text((72, height - 58), footer, font=small_font, fill="#94a3b8")
    path = FRAMES_DIR / f"slide_{index:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def load_gemini_summary() -> str:
    path = ROOT / "reports" / "gemini_research_brief.json"
    if not path.exists():
        return "Gemini Pro preview brief metadata unavailable."
    payload = json.loads(path.read_text(encoding="utf-8"))
    provider = payload.get("provider", {})
    return f"{provider.get('model', 'gemini')} | {provider.get('project', 'project')} | {provider.get('usage_metadata', {}).get('total_token_count', 'n/a')} tokens"


def slides() -> list[dict]:
    gemini_summary = load_gemini_summary()
    return [
        {
            "title": "Self-auditing battery research agent",
            "subtitle": "CellForge AI turns EV battery literature into evidence-backed research hypotheses.",
            "bullets": ["Green lithium-ion battery materials", "Not a chatbot: a traced multi-step agent workflow", "Output: proposal package, not an automatic final paper"],
            "footer": "README.md",
            "duration": 12,
        },
        {
            "title": "Real-world research problem",
            "subtitle": "Materials researchers face too many papers and too much risk of ungrounded ideas.",
            "bullets": ["Extract experimental claims", "Find research gaps", "Check contradictions and limitations", "Keep humans in control"],
            "footer": "Google Cloud Rapid Agent Hackathon | Arize track",
            "duration": 14,
        },
        {
            "title": "Agent workflow",
            "subtitle": "The agent plans and executes a deterministic research pipeline.",
            "bullets": ["Ingest Gemini extraction artifacts", "Build real evidence corpus", "Benchmark retrieval", "Generate and audit hypotheses", "Draft only after validation"],
            "footer": "scripts/run_traced_real_pipeline.py",
            "duration": 16,
        },
        {
            "title": "Arize AX observability",
            "subtitle": "Every major decision becomes inspectable in traces.",
            "bullets": ["Retrieval span", "Hypothesis generator span", "Evaluator spans for each hypothesis", "Self-introspection span selects H003"],
            "footer": "reports/traces/phoenix_connection_report.md",
            "duration": 16,
        },
        {
            "title": "Audit-first hypothesis generation",
            "subtitle": "CellForge scores hypotheses before recommending them.",
            "bullets": ["Citation coverage", "Claim grounding", "Contradiction coverage", "Evidence strength", "Hallucination risk"],
            "footer": "reports/real_audit_report.md",
            "duration": 15,
        },
        {
            "title": "Selected direction: H003",
            "subtitle": "Circular natural-graphite anodes with bio-based conductive surface repair.",
            "bullets": ["Non-thermal plasma purification", "Regenerated graphite capacity recovery", "Bio-derived carbon coating", "SEI stabilization hypothesis"],
            "footer": "data/real_hypotheses.json",
            "duration": 17,
        },
        {
            "title": "Contradictions stay visible",
            "subtitle": "The agent does not hide evidence that weakens or complicates the proposal.",
            "bullets": ["PHBV binder shows strong cycling performance", "But processing uses chloroform", "Lower adhesion than PVDF becomes a risk-control note"],
            "footer": "data/real_hypothesis_audits.json",
            "duration": 16,
        },
        {
            "title": "Human validation gate",
            "subtitle": "The draft unlocks only after selected claims pass demo validation.",
            "bullets": ["4 critical claims validated for demo", "Final publisher-grade validation still required", "Prevents extraction artifacts from becoming unchecked paper claims"],
            "footer": "reports/human_validation_report.md",
            "duration": 17,
        },
        {
            "title": "Gemini Pro preview report",
            "subtitle": "The final research brief is generated from audited evidence with Gemini.",
            "bullets": [gemini_summary, "Lead hypothesis: real:H003", "Includes visual evidence and limitations"],
            "footer": "reports/gemini_research_brief.md + .json",
            "duration": 15,
        },
        {
            "title": "Research output package",
            "subtitle": "CellForge exports a proposal package a human researcher can continue.",
            "bullets": ["Gemini research brief", "Manuscript draft", "Audit and validation reports", "Molecular/interface schematic"],
            "footer": "reports/manuscript_draft.md",
            "duration": 15,
        },
        {
            "title": "Broader vision",
            "subtitle": "The same pattern can support many research domains.",
            "bullets": ["Solar materials", "Catalysts", "Carbon capture", "Biomedical materials", "Semiconductors"],
            "footer": "retrieve -> extract -> hypothesize -> audit -> validate -> draft",
            "duration": 14,
        },
    ]


def create_concat_file(frame_paths: list[Path], durations: list[int]) -> Path:
    concat = OUT_DIR / "frames.txt"
    lines: list[str] = []
    for frame, duration in zip(frame_paths, durations):
        safe = frame.resolve().as_posix()
        lines.append(f"file '{safe}'")
        lines.append(f"duration {duration}")
    lines.append(f"file '{frame_paths[-1].resolve().as_posix()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return concat


def find_ffmpeg(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    candidates = [
        "ffmpeg",
        str(Path.home() / "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffmpeg.exe"),
    ]
    for candidate in candidates:
        try:
            subprocess.run([candidate, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return candidate
        except Exception:
            continue
    raise RuntimeError("ffmpeg not found. Install FFmpeg or pass --ffmpeg.")


def create_video(output: Path, ffmpeg_path: str | None = None) -> None:
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame_paths: list[Path] = []
    durations: list[int] = []
    for index, slide in enumerate(slides(), start=1):
        frame_paths.append(render_slide(index, slide["title"], slide["subtitle"], slide["bullets"], slide["footer"]))
        durations.append(slide["duration"])

    concat = create_concat_file(frame_paths, durations)
    ffmpeg = find_ffmpeg(ffmpeg_path)
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-vf",
        "fps=30,format=yuv420p",
        "-c:v",
        "libx264",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a silent CellForge AI demo MP4 for Clipchamp voice-over.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    parser.add_argument("--ffmpeg", default=None)
    args = parser.parse_args()
    output = Path(args.output)
    create_video(output=output, ffmpeg_path=args.ffmpeg)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

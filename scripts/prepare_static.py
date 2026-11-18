#!/usr/bin/env python3
"""Prepare the uploaded Next.js archive for static GitHub Pages hosting."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "website"


def edit(name: str, old: str, new: str, count: int = 1) -> None:
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Missing expected source text in {name}: {old[:90]!r}")
    path.write_text(text.replace(old, new, count), encoding="utf-8")


def main() -> None:
    if not (ROOT / "package.json").is_file() or not (ROOT / "src/app/page.tsx").is_file():
        raise SystemExit("The archive must contain the Next.js project at its root.")

    (ROOT / "next.config.ts").write_text('''import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath: process.env.NODE_ENV === "production" ? "/QRcode" : "",
  images: { unoptimized: true },
};
export default nextConfig;
''', encoding="utf-8")

    (ROOT / "src/lib/reader-notes-storage.ts").write_text('''import type { ReaderNote } from "@/lib/types";
const KEY = "holden-atlas-reader-notes-v1";
export function readStoredReaderNotes(): ReaderNote[] | null {
  if (typeof window === "undefined") return null;
  try { const raw = localStorage.getItem(KEY); if (!raw) return null;
    const data: unknown = JSON.parse(raw); return Array.isArray(data) ? data as ReaderNote[] : null;
  } catch { return null; }
}
export function writeStoredReaderNotes(notes: ReaderNote[]): void {
  if (typeof window === "undefined") return;
  try { localStorage.setItem(KEY, JSON.stringify(notes)); } catch { /* storage unavailable */ }
}
''', encoding="utf-8")

    (ROOT / "src/lib/public-asset.ts").write_text('''export function publicAsset(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${process.env.NODE_ENV === "production" ? "/QRcode" : ""}${normalized}`;
}
''', encoding="utf-8")

    (ROOT / "src/data/initial-reader-notes.ts").write_text('''import { INITIAL_READER_NOTES } from "@/data/sources";
import type { ReaderNote } from "@/lib/types";
export const INITIAL_READER_NOTES_TYPED: ReaderNote[] = INITIAL_READER_NOTES.map((note, index) => ({
  ...note, id: index + 1, noteType: note.noteType as ReaderNote["noteType"],
  chapterRef: note.chapterRef ?? null, createdAt: "2026-11-18T00:00:00.000Z",
}));
''', encoding="utf-8")

    (ROOT / "src/app/page.tsx").write_text('''import HoldenAtlasApp from "@/components/HoldenAtlasApp";
import { ATLAS_LOCATIONS } from "@/data/locations";
import { CHRONOLOGICAL_EVENTS } from "@/data/events";
import { RESEARCH_SOURCES } from "@/data/sources";
import { STORY_CHARACTERS } from "@/data/characters";
import { INITIAL_READER_NOTES_TYPED } from "@/data/initial-reader-notes";
export default function HomePage() {
  return <HoldenAtlasApp initialLocations={ATLAS_LOCATIONS} initialEvents={CHRONOLOGICAL_EVENTS}
    initialSources={RESEARCH_SOURCES} initialCharacters={STORY_CHARACTERS} initialNotes={INITIAL_READER_NOTES_TYPED} />;
}
''', encoding="utf-8")

    route = "src/app/locations/[id]/page.tsx"
    edit(route, 'import { getCompleteAtlasData } from "@/db/seed-service";\n',
         'import { ATLAS_LOCATIONS } from "@/data/locations";\nimport { CHRONOLOGICAL_EVENTS } from "@/data/events";\n'
         'import { RESEARCH_SOURCES } from "@/data/sources";\nimport { STORY_CHARACTERS } from "@/data/characters";\n'
         'import { INITIAL_READER_NOTES_TYPED } from "@/data/initial-reader-notes";\n')
    edit(route, 'export const dynamic = "force-dynamic";\n',
         'export function generateStaticParams() { return ATLAS_LOCATIONS.map(({ id }) => ({ id })); }\nexport const dynamicParams = false;\n')
    edit(route, '  const { locations } = await getCompleteAtlasData();\n  const loc = locations.find((l) => l.id === id);',
         '  const loc = ATLAS_LOCATIONS.find((l) => l.id === id);')
    edit(route, '  const { locations, events, sources, characters, notes } =\n    await getCompleteAtlasData();\n\n  const currentIdx = locations.findIndex((l) => l.id === id);',
         '  const locations = ATLAS_LOCATIONS;\n  const events = CHRONOLOGICAL_EVENTS;\n  const sources = RESEARCH_SOURCES;\n'
         '  const characters = STORY_CHARACTERS;\n  const notes = INITIAL_READER_NOTES_TYPED;\n\n  const currentIdx = locations.findIndex((l) => l.id === id);')

    method = "src/components/MethodologyAndSources.tsx"
    edit(method, 'import { AUDIT_ITEMS } from "@/data/sources";\n',
         'import { AUDIT_ITEMS } from "@/data/sources";\nimport { ATLAS_LOCATIONS, buildAtlasGeoJson } from "@/data/locations";\n'
         'import { CHRONOLOGICAL_EVENTS } from "@/data/events";\n')
    edit(method, '  const filteredSources =\n',
         '  const downloadGeoJson = () => {\n'
         '    const blob = new Blob([JSON.stringify(buildAtlasGeoJson(ATLAS_LOCATIONS, CHRONOLOGICAL_EVENTS), null, 2)], { type: "application/geo+json" });\n'
         '    const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url;\n'
         '    a.download = "holden-new-york-literary-atlas-ka.geojson"; a.click(); URL.revokeObjectURL(url);\n'
         '  };\n  const filteredSources =\n')
    edit(method, '<a\n            href="/api/geojson?download=1"\n            className="self-start lg:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-md bg-[#243447] text-[#FDFBF7] text-xs font-semibold hover:bg-[#192533] transition shadow-sm"\n          >\n            <Download className="w-4 h-4" />\n            GeoJSON მონაცემთა ბაზის ჩამოტვირთვა\n          </a>',
         '<button type="button" onClick={downloadGeoJson} className="self-start lg:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-md bg-[#243447] text-[#FDFBF7] text-xs font-semibold hover:bg-[#192533] transition shadow-sm">\n'
         '            <Download className="w-4 h-4" />GeoJSON მონაცემთა ბაზის ჩამოტვირთვა\n          </button>')
    edit(method, "ყველა კოორდინატი წინასწარ გადამოწმებულია და ინახება PostgreSQL-სა და GeoJSON-ში.",
         "ყველა კოორდინატი შედის პროექტის სტატიკურ მონაცემებში და შეიძლება GeoJSON-ად ჩამოიტვირთოს.")

    notes = "src/components/LocationDossierContent.tsx"
    edit(notes, 'import { useState } from "react";', 'import { useEffect, useState } from "react";')
    edit(notes, '} from "@/lib/types";\n',
         '} from "@/lib/types";\nimport { readStoredReaderNotes, writeStoredReaderNotes } from "@/lib/reader-notes-storage";\n'
         'import { publicAsset } from "@/lib/public-asset";\n')
    edit(notes, '  const [localNotes, setLocalNotes] = useState<ReaderNote[]>(notes);',
         '  const [localNotes, setLocalNotes] = useState<ReaderNote[]>(notes);\n'
         '  useEffect(() => { if (!onNoteCreated) { const stored = readStoredReaderNotes(); if (stored !== null) setLocalNotes(stored); } }, [onNoteCreated]);')
    old = '''    try {
      const res = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          locationId: location.id,
          authorName,
          authorRole,
          noteType,
          chapterRef,
          content,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setFormError(data.error || "შენახვა ვერ მოხერხდა.");
      } else if (data.note) {
        if (onNoteCreated) {
          onNoteCreated(data.note);
        } else {
          setLocalNotes((prev) => [data.note, ...prev]);
        }
        setAuthorName("");
        setContent("");
        setFormSuccess("ჩანაწერი წარმატებით შეინახა ატლასის არქივში.");
      }
    } catch {
      setFormError("სერვერთან კავშირი ვერ დამყარდა.");
    } finally {
      setSubmitting(false);
    }'''
    new = '''    try {
      const current = onNoteCreated ? notes : (readStoredReaderNotes() ?? localNotes);
      const note: ReaderNote = { id: Date.now(), locationId: location.id, authorName: authorName.trim(),
        authorRole: authorRole.trim() || "მკითხველი", noteType, content: content.trim(),
        chapterRef: chapterRef.trim() || null, createdAt: new Date().toISOString() };
      const updated = [note, ...current];
      if (onNoteCreated) onNoteCreated(note); else { setLocalNotes(updated); writeStoredReaderNotes(updated); }
      setAuthorName(""); setContent(""); setFormSuccess("ჩანაწერი შეინახა ამ ბრაუზერის ლოკალურ საცავში.");
    } catch { setFormError("ჩანაწერის შენახვა ვერ მოხერხდა."); }
    finally { setSubmitting(false); }'''
    edit(notes, old, new)
    old = '''  const handleDeleteNote = async (noteId: number) => {
    try {
      const res = await fetch(`/api/notes/${noteId}`, { method: "DELETE" });
      if (res.ok) {
        if (onNoteDeleted) {
          onNoteDeleted(noteId);
        } else {
          setLocalNotes((prev) => prev.filter((n) => n.id !== noteId));
        }
      }
    } catch {
      // Ignore transient failure
    }
  };'''
    new = '''  const handleDeleteNote = (noteId: number) => {
    if (onNoteDeleted) onNoteDeleted(noteId);
    else { const updated = localNotes.filter((note) => note.id !== noteId); setLocalNotes(updated); writeStoredReaderNotes(updated); }
  };'''
    edit(notes, old, new)
    edit(notes, "Reader & Scholar Marginalia Notes (PostgreSQL-backed CRUD)", "Reader & Scholar Marginalia Notes (browser-local storage)")
    edit(notes, "დატოვეთ ლიტერატურული, ისტორიული ან გეოგრაფიული დაკვირვება ამ ადგილის შესახებ (ინახება მონაცემთა ბაზაში).",
         "დატოვეთ ლიტერატურული, ისტორიული ან გეოგრაფიული დაკვირვება ამ ადგილის შესახებ (ინახება მხოლოდ თქვენს ბრაუზერში).")

    app = "src/components/HoldenAtlasApp.tsx"
    edit(app, '} from "@/lib/types";\n',
         '} from "@/lib/types";\nimport { readStoredReaderNotes, writeStoredReaderNotes } from "@/lib/reader-notes-storage";\n'
         'import { publicAsset } from "@/lib/public-asset";\n')
    edit(app, '  const [notes, setNotes] = useState<ReaderNote[]>(initialNotes);',
         '  const [notes, setNotes] = useState<ReaderNote[]>(initialNotes);\n'
         '  useEffect(() => { const stored = readStoredReaderNotes(); if (stored !== null) setNotes(stored); }, []);')
    edit(app, '  const handleNoteCreated = useCallback((newNote: ReaderNote) => {\n    setNotes((prev) => [newNote, ...prev]);\n  }, []);\n\n  const handleNoteDeleted = useCallback((noteId: number) => {\n    setNotes((prev) => prev.filter((n) => n.id !== noteId));\n  }, []);',
         '  const handleNoteCreated = useCallback((note: ReaderNote) => { const updated = [note, ...notes]; setNotes(updated); writeStoredReaderNotes(updated); }, [notes]);\n'
         '  const handleNoteDeleted = useCallback((id: number) => { const updated = notes.filter((note) => note.id !== id); setNotes(updated); writeStoredReaderNotes(updated); }, [notes]);')

    for name in ["src/components/ThenNowSlider.tsx", "src/components/LocationDossierContent.tsx"]:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        marker = 'import { publicAsset } from "@/lib/public-asset";\n'
        if marker not in text:
            text = text.replace('} from "@/lib/types";\n', '} from "@/lib/types";\n' + marker, 1)
        for expr in ["modImg.url", "histImg.url", "img.url", "singleImg.url"]:
            text = text.replace(f"src={{{expr}}}", f"src={{publicAsset({expr})}}")
        for expr in ["modImg.url", "histImg.url", "img.url", "singleImg.url"]:
            text = text.replace(f"src={{publicAsset({expr})}}",
                f'src={{publicAsset({expr})}} onError={{(e) => {{ e.currentTarget.onerror = null; e.currentTarget.src = publicAsset("/images/image-unavailable.svg"); }}}}')
        path.write_text(text, encoding="utf-8")

    app_path = ROOT / app
    app_text = app_path.read_text(encoding="utf-8")
    app_text = app_text.replace('src="/images/hero-manhattan-winter.jpg"', 'src={publicAsset("/images/hero-manhattan-winter.svg")}')
    for expr in ["activeSideImg.url", "coverImg.url"]:
        app_text = app_text.replace(f"src={{{expr}}}",
            f'src={{publicAsset({expr})}} onError={{(e) => {{ e.currentTarget.onerror = null; e.currentTarget.src = publicAsset("/images/image-unavailable.svg"); }}}}')
    app_path.write_text(app_text, encoding="utf-8")

    assets = ROOT / "public/images"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "image-unavailable.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650"><rect width="100%" height="100%" fill="#344454"/><text x="50%" y="50%" fill="#fff" text-anchor="middle" font-family="sans-serif" font-size="28">Image not included in source ZIP</text></svg>', encoding="utf-8")
    (assets / "hero-manhattan-winter.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1100"><defs><linearGradient id="s" x2="0" y2="1"><stop stop-color="#182c42"/><stop offset="1" stop-color="#b4a58f"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#s)"/><path d="M0 590L120 430 230 520 350 280 480 500 610 350 760 500 900 330V1100H0Z" fill="#202d3a"/><path d="M0 720Q220 650 450 720T900 720V1100H0Z" fill="#213c4d"/></svg>', encoding="utf-8")

    shutil.rmtree(ROOT / "src/app/api", ignore_errors=True)
    shutil.rmtree(ROOT / "src/db", ignore_errors=True)
    (ROOT / "drizzle.config.json").unlink(missing_ok=True)
    package_path = ROOT / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["name"] = "holden-caulfield-literary-atlas"
    for key, deps in [("dependencies", ["dotenv", "drizzle-orm", "pg"]),
                      ("devDependencies", ["@types/pg", "drizzle-kit"])]:
        for dep in deps:
            package.get(key, {}).pop(dep, None)
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for path in (ROOT / "src").rglob("*.tsx"):
        text = path.read_text(encoding="utf-8")
        if 'fetch("/api/' in text or "fetch(`/api/" in text or 'from "@/db/' in text:
            raise RuntimeError(f"Database/API dependency was not removed: {path}")
    print("Static GitHub Pages preparation completed.")


if __name__ == "__main__":
    main()

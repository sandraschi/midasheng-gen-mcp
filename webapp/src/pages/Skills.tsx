import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { type SkillInfo, api } from "../lib/api";

export default function Skills() {
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .skills()
      .then((d) => setSkills(d.skills))
      .catch((e) => setError(e instanceof Error ? e.message : "Load failed"));
  }, []);

  const loadSkill = useCallback(async (name: string) => {
    setSelected(name);
    try {
      const data = await api.skill(name);
      setContent(data.content);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Skill load failed");
    }
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-4 p-6" data-testid="skills-page">
      <h2 className="text-lg font-semibold">Skills</h2>
      {error && (
        <div className="rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </div>
      )}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-2">
          {skills.map((skill) => (
            <button
              type="button"
              key={skill.name}
              onClick={() => loadSkill(skill.name)}
              className={`w-full rounded-lg border p-3 text-left ${
                selected === skill.name
                  ? "border-amber-500/60 bg-amber-500/5"
                  : "border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800"
              }`}
              data-testid={`skill-${skill.name}`}
            >
              <div className="text-sm font-medium text-zinc-200">{skill.name}</div>
              <div className="text-xs text-zinc-500">{skill.description}</div>
            </button>
          ))}
        </div>
        <div className="prose prose-invert max-w-none lg:col-span-2">
          {content ? (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-zinc-800 p-8 text-center text-sm text-zinc-500">
              Select a skill to view its content.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import { create } from "zustand";
import { api } from "../lib/api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

const HISTORY_KEY = "midasheng-gen-chat-history";
const PERSONALITY_KEY = "midasheng-gen-chat-personality";

export interface Personality {
  id: string;
  label: string;
  prompt: string;
}

const PERSONALITIES: Personality[] = [
  {
    id: "sound-designer",
    label: "Sound Designer",
    prompt:
      "You are a senior sound designer and audio engineer. Give concise, practical advice on generating audio scenes: which caption views to fill, what parameters to tweak (eval_cfg, seed), and how to layer speech, music, SFX, and ambience. Reference the available audio_scene operations when relevant.",
  },
  {
    id: "critic",
    label: "Scene Critic",
    prompt:
      "You are a strict audio critic reviewing generated scenes. Assess realism, mixing balance, and speech intelligibility. Suggest concrete caption improvements: more specific SFX verbs, contrasting env details, or clearer asr prose.",
  },
  {
    id: "teacher",
    label: "Prompt Teacher",
    prompt:
      "You are a teacher explaining text-to-audio prompting. Walk through the structured caption format (<|caption|>, <|asr|>, <|speech|>, <|sfx|>, <|music|>, <|env|>) with examples, and explain how the LLM-driven flow matching model works at an intuitive level.",
  },
  {
    id: "custom",
    label: "Custom",
    prompt: "",
  },
];

interface ChatState {
  messages: ChatMessage[];
  personalityId: string;
  sending: boolean;
  error: string | null;
  personalities: Personality[];
  send: (content: string, customPrompt: string) => Promise<void>;
  clear: () => void;
  setPersonality: (id: string) => void;
  restore: () => void;
}

function loadHistory(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? (JSON.parse(raw) as ChatMessage[]) : [];
  } catch {
    return [];
  }
}

export const useChat = create<ChatState>((set, get) => ({
  messages: [],
  personalityId: localStorage.getItem(PERSONALITY_KEY) ?? "sound-designer",
  sending: false,
  error: null,
  personalities: PERSONALITIES,
  restore: () => set({ messages: loadHistory() }),
  setPersonality: (id) => {
    set({ personalityId: id });
    localStorage.setItem(PERSONALITY_KEY, id);
  },
  clear: () => {
    set({ messages: [] });
    localStorage.removeItem(HISTORY_KEY);
  },
  send: async (content, customPrompt) => {
    const { personalityId, personalities, messages } = get();
    const personality = personalities.find((p) => p.id === personalityId) ?? personalities[0];
    const systemPrompt =
      personality.id === "custom"
        ? customPrompt || "You are a helpful assistant for the MiDashengLM-Gen audio scene tool."
        : personality.prompt;

    const next: ChatMessage[] = [
      ...messages,
      { role: "user", content, ts: new Date().toISOString() },
    ];
    set({ messages: next, sending: true, error: null });
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next));

    try {
      const apiMessages = [
        { role: "system", content: systemPrompt },
        ...next.map((m) => ({ role: m.role, content: m.content })),
      ];
      const result = await api.llmChat(apiMessages);
      const reply: ChatMessage = {
        role: "assistant",
        content: result.content,
        ts: new Date().toISOString(),
      };
      const withReply = [...next, reply];
      set({ messages: withReply, sending: false });
      localStorage.setItem(HISTORY_KEY, JSON.stringify(withReply));
    } catch (e) {
      set({
        sending: false,
        error: e instanceof Error ? e.message : "Chat failed",
      });
    }
  },
}));

import { useEffect, useState, useRef } from "react";

export type TypewriterPhase = "typing" | "holding" | "deleting" | "paused";

export interface TypewriterOptions {
  typeMs?: number;
  deleteMs?: number;
  holdMs?: number;
  gapMs?: number;
  enabled?: boolean;
}

export function useTypewriter(
  prompts: string[],
  options: TypewriterOptions = {}
) {
  const {
    typeMs = 42,
    deleteMs = 14,
    holdMs = 3200,
    gapMs = 800,
    enabled = true,
  } = options;

  const [promptIndex, setPromptIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [phase, setPhase] = useState<TypewriterPhase>("typing");
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!enabled || !prompts || prompts.length === 0) {
      return;
    }

    const currentPrompt = prompts[promptIndex % prompts.length] || "";

    if (phase === "typing") {
      if (charIndex < currentPrompt.length) {
        timeoutRef.current = setTimeout(() => {
          setCharIndex((prev) => prev + 1);
        }, typeMs);
      } else {
        timeoutRef.current = setTimeout(() => {
          setPhase("holding");
        }, 100);
      }
    } else if (phase === "holding") {
      timeoutRef.current = setTimeout(() => {
        setPhase("deleting");
      }, holdMs);
    } else if (phase === "deleting") {
      if (charIndex > 0) {
        timeoutRef.current = setTimeout(() => {
          setCharIndex((prev) => prev - 1);
        }, deleteMs);
      } else {
        timeoutRef.current = setTimeout(() => {
          setPhase("paused");
        }, 100);
      }
    } else if (phase === "paused") {
      timeoutRef.current = setTimeout(() => {
        setPromptIndex((prev) => (prev + 1) % prompts.length);
        setCharIndex(0);
        setPhase("typing");
      }, gapMs);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [charIndex, phase, promptIndex, prompts, typeMs, deleteMs, holdMs, gapMs, enabled]);

  const currentPrompt = prompts[promptIndex % prompts.length] || "";
  const text = currentPrompt.slice(0, charIndex);

  return { text, phase };
}

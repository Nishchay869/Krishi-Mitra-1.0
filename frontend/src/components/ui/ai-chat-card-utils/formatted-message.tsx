import * as React from "react";

interface FormattedMessageProps {
  content: string;
  isUser?: boolean;
  className?: string;
}

/**
 * Parses inline markdown-like formatting (**bold**, *italic*, `code`) into React elements.
 * Cleans up stray raw asterisks so the user never sees raw unparsed symbols.
 */
function parseInline(text: string, isUser: boolean = false): React.ReactNode[] {
  if (!text) return [];

  // Match **bold**, __bold__, `code`, *italic*, _italic_
  const tokenRegex = /(\*\*[^*]+?\*\*|__[^*]+?__|`[^`]+?`|(?<!\*)\*[^*]+?\*(?!\*)|(?<!_)_[^_]+?_(?!_))/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, i) => {
    if (!part) return null;

    // Bold: **text** or __text__
    if (
      (part.startsWith("**") && part.endsWith("**") && part.length >= 4) ||
      (part.startsWith("__") && part.endsWith("__") && part.length >= 4)
    ) {
      const inner = part.slice(2, -2).trim();
      return (
        <strong
          key={i}
          className={
            isUser
              ? "font-bold text-white tracking-tight"
              : "font-semibold text-slate-900 dark:text-white tracking-tight"
          }
        >
          {inner}
        </strong>
      );
    }

    // Inline code: `text`
    if (part.startsWith("`") && part.endsWith("`") && part.length >= 2) {
      const inner = part.slice(1, -1);
      return (
        <code
          key={i}
          className="rounded bg-slate-200/80 px-1 py-0.5 font-mono text-[11.5px] text-slate-800 dark:bg-slate-700/80 dark:text-slate-200"
        >
          {inner}
        </code>
      );
    }

    // Italic: *text* or _text_
    if (
      (part.startsWith("*") && part.endsWith("*") && part.length >= 2) ||
      (part.startsWith("_") && part.endsWith("_") && part.length >= 2)
    ) {
      const inner = part.slice(1, -1).trim();
      return (
        <em key={i} className="italic">
          {inner}
        </em>
      );
    }

    // Plain text: strip out any stray or malformed raw asterisks
    const cleaned = part.replace(/\*{2,}/g, "").replace(/(?:^|\s)\*(?:\s|$)/g, " ");
    return <React.Fragment key={i}>{cleaned}</React.Fragment>;
  });
}

type Block =
  | { type: "header"; text: string; level: number }
  | { type: "bullet_list"; items: string[] }
  | { type: "numbered_list"; items: { num: string; text: string }[] }
  | { type: "paragraph"; text: string };

/**
 * Formats multi-line text into a structured, easily understandable UI:
 * - Replaces raw '*' bullets with beautiful, modern bullet points
 * - Renders **bold** with high-contrast font-semibold
 * - Formats numbered steps (1., 2.) with styled number badges
 * - Renders headers cleanly with proper hierarchy
 */
export function FormattedMessage({
  content,
  isUser = false,
  className = "",
}: FormattedMessageProps) {
  const blocks = React.useMemo(() => {
    if (!content) return [];

    const rawLines = content.split("\n");
    const parsedBlocks: Block[] = [];
    let currentBulletList: string[] | null = null;
    let currentNumberedList: { num: string; text: string }[] | null = null;
    let currentParagraphLines: string[] = [];

    const flushParagraph = () => {
      if (currentParagraphLines.length > 0) {
        const text = currentParagraphLines.join(" ").trim();
        if (text) {
          parsedBlocks.push({ type: "paragraph", text });
        }
        currentParagraphLines = [];
      }
    };

    const flushBulletList = () => {
      if (currentBulletList && currentBulletList.length > 0) {
        parsedBlocks.push({ type: "bullet_list", items: currentBulletList });
        currentBulletList = null;
      }
    };

    const flushNumberedList = () => {
      if (currentNumberedList && currentNumberedList.length > 0) {
        parsedBlocks.push({ type: "numbered_list", items: currentNumberedList });
        currentNumberedList = null;
      }
    };

    const flushAll = () => {
      flushParagraph();
      flushBulletList();
      flushNumberedList();
    };

    for (let i = 0; i < rawLines.length; i++) {
      const line = rawLines[i].trim();

      if (!line) {
        // Empty line separates blocks
        flushAll();
        continue;
      }

      // Check for Markdown headers: #, ##, ###
      const headerMatch = line.match(/^(#{1,3})\s+(.*)$/);
      if (headerMatch) {
        flushAll();
        parsedBlocks.push({
          type: "header",
          level: headerMatch[1].length,
          text: headerMatch[2],
        });
        continue;
      }

      // Check for standalone bold header (e.g. "**Expected Paddy Yield:**" or "**Key Steps:**")
      const boldHeaderMatch = line.match(/^\*\*([^*]+)\*\*:?$/);
      if (boldHeaderMatch && line.length < 90) {
        flushAll();
        parsedBlocks.push({
          type: "header",
          level: 3,
          text: boldHeaderMatch[1],
        });
        continue;
      }

      // Check for bullet list items: "* ", "- ", "• ", "+ ", or "* **"
      const bulletMatch = line.match(/^([*•\-+]|\*\s*\*\*)\s*(.*)$/);
      if (bulletMatch) {
        flushParagraph();
        flushNumberedList();
        if (!currentBulletList) currentBulletList = [];
        // If it matched "* **", reconstruct the leading "**" for inline parser
        const bulletText = bulletMatch[1].includes("**")
          ? `**${bulletMatch[2]}`
          : bulletMatch[2];
        currentBulletList.push(bulletText);
        continue;
      }

      // Check for numbered list items: "1. ", "2) ", etc.
      const numberMatch = line.match(/^(\d+)[\.\)]\s+(.*)$/);
      if (numberMatch) {
        flushParagraph();
        flushBulletList();
        if (!currentNumberedList) currentNumberedList = [];
        currentNumberedList.push({
          num: numberMatch[1],
          text: numberMatch[2],
        });
        continue;
      }

      // Otherwise, regular line in a paragraph
      flushBulletList();
      flushNumberedList();
      currentParagraphLines.push(line);
    }

    flushAll();
    return parsedBlocks;
  }, [content]);

  if (!content) return null;

  return (
    <div
      className={`select-text break-words text-[13.5px] leading-relaxed ${
        isUser ? "text-white" : "text-slate-800 dark:text-slate-200"
      } ${className}`}
    >
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "header":
            return (
              <div
                key={idx}
                className={
                  isUser
                    ? "font-bold text-white text-[14px] mt-2 mb-1 tracking-tight"
                    : "font-bold text-slate-900 dark:text-white text-[14px] mt-2 mb-1 tracking-tight"
                }
              >
                {parseInline(block.text, isUser)}
              </div>
            );

          case "bullet_list":
            return (
              <ul key={idx} className="my-2 space-y-1.5 pl-0.5 list-none">
                {block.items.map((item, itemIdx) => (
                  <li key={itemIdx} className="flex items-start gap-2.5">
                    <span
                      className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${
                        isUser
                          ? "bg-white/90 shadow-2xs"
                          : "bg-emerald-500 dark:bg-emerald-400"
                      }`}
                      aria-hidden="true"
                    />
                    <span className="flex-1 min-w-0 leading-relaxed">
                      {parseInline(item, isUser)}
                    </span>
                  </li>
                ))}
              </ul>
            );

          case "numbered_list":
            return (
              <ol key={idx} className="my-2.5 space-y-2 list-none">
                {block.items.map((item, itemIdx) => (
                  <li key={itemIdx} className="flex items-start gap-2.5">
                    <span
                      className={`mt-0.5 flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded-full text-[10.5px] font-bold ${
                        isUser
                          ? "bg-white/20 text-white"
                          : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300"
                      }`}
                    >
                      {item.num}
                    </span>
                    <span className="flex-1 min-w-0 leading-relaxed">
                      {parseInline(item.text, isUser)}
                    </span>
                  </li>
                ))}
              </ol>
            );

          case "paragraph":
            return (
              <p key={idx} className="my-1.5 leading-relaxed">
                {parseInline(block.text, isUser)}
              </p>
            );

          default:
            return null;
        }
      })}
    </div>
  );
}


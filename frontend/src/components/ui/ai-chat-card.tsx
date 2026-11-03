import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowUp,
  Plus,
  RefreshCw,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Copy,
  Check,
  Sparkles,
  Sprout,
  X,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTypewriter } from "./ai-chat-card-utils/use-typewriter";
import { FormattedMessage } from "./ai-chat-card-utils/formatted-message";

export interface ChatMessageItem {
  id: string | number;
  role: "user" | "assistant";
  content: string;
  image?: string;
  isVoice?: boolean;
  time?: string;
}

export interface AIChatCardProps {
  title?: string;
  subtitle?: string;
  greeting?: string;
  prompt?: string;
  prompts?: string[];
  autoType?: boolean;
  placeholder?: string;
  icon?: React.ReactNode;
  messages?: ChatMessageItem[];
  isLoading?: boolean;
  isRecording?: boolean;
  playingMessageId?: string | number | null;
  onSend?: (message: string, file?: File | null, previewUrl?: string) => void;
  onReset?: () => void;
  onAttach?: () => void;
  onClose?: () => void;
  onToggleMic?: () => void;
  onListen?: (messageId: string | number, text: string) => void;
  className?: string;
}

const DEFAULT_AGRI_PROMPTS = [
  "ಗೋಧಿಗೆ ಎಷ್ಟು ಯೂರಿಯಾ ಮತ್ತು ಗೊಬ್ಬರ ಹಾಕಬೇಕು?",
  "What is the best treatment for tomato early blight?",
  "धान में यूरिया डालने का सही समय और मात्रा क्या है?",
  "Is the weather suitable for spraying pesticides today?",
  "How to apply for PM-KISAN ₹6,000 benefit?",
  "What are today's mandi market rates for onion?",
];

const SUGGESTION_CHIPS = [
  { label: "🍅 Tomato Blight", query: "What are tomato early blight symptoms and treatments?" },
  { label: "🌾 Urea Dose", query: "What is the recommended fertilizer and urea dose for paddy?" },
  { label: "🌧️ Spray Weather", query: "What are the optimal weather conditions for pesticide spraying?" },
  { label: "💰 PM-KISAN", query: "How does PM-KISAN scheme work and who is eligible?" },
  { label: "📈 Mandi Prices", query: "How to check today's APMC mandi market prices for crops?" },
];

export function AIChatCard({
  title = "Farm Assistant",
  subtitle = "Smart AI Farming Companion",
  greeting = "Namaste, Farmer!",
  prompt = "Ask anything about crops, pests, fertilizers, weather, or mandi prices in any language.",
  prompts = DEFAULT_AGRI_PROMPTS,
  autoType = true,
  placeholder = "Ask in any language (ಕನ್ನಡ, हिन्दी, English)…",
  icon,
  messages = [],
  isLoading = false,
  isRecording = false,
  playingMessageId = null,
  onSend,
  onReset,
  onAttach,
  onClose,
  onToggleMic,
  onListen,
  className,
}: AIChatCardProps) {
  const rootRef = React.useRef<HTMLDivElement>(null);
  const messagesContainerRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const isInitialMount = React.useRef(true);

  const [userMessage, setUserMessage] = React.useState("");
  const [spins, setSpins] = React.useState(0);
  const [copiedId, setCopiedId] = React.useState<string | number | null>(null);
  const [attachedFile, setAttachedFile] = React.useState<{
    file: File;
    name: string;
    size: string;
    preview?: string;
    isImage: boolean;
  } | null>(null);

  const hasMessages = messages.length > 0;

  const { text: typedMessage } = useTypewriter(prompts, {
    typeMs: 42,
    deleteMs: 14,
    holdMs: 3400,
    gapMs: 900,
    enabled: autoType && !hasMessages && userMessage.length === 0,
  });

  const handlePlusClick = () => {
    onAttach?.();
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const sizeFormatted =
      file.size > 1024 * 1024
        ? `${(file.size / (1024 * 1024)).toFixed(1)} MB`
        : `${Math.round(file.size / 1024)} KB`;

    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAttachedFile({
          file,
          name: file.name,
          size: sizeFormatted,
          preview: reader.result as string,
          isImage: true,
        });
      };
      reader.readAsDataURL(file);
    } else {
      setAttachedFile({
        file,
        name: file.name,
        size: sizeFormatted,
        isImage: false,
      });
    }

    e.target.value = "";
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const handleSend = () => {
    const textToSend = userMessage.trim();
    if ((!textToSend && !attachedFile) || isLoading) return;
    onSend?.(textToSend, attachedFile?.file || null, attachedFile?.preview);
    setUserMessage("");
    setAttachedFile(null);
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (id: string | number, text: string) => {
    // Strip raw asterisks from copied text for clean, human-readable clipboard content
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/(?:^|\n)\s*[*•\-+]\s+/g, "\n• ")
      .trim();
    navigator.clipboard?.writeText(cleanText);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Internal auto-scroll ONLY for the message container (never scrolling the outer window on refresh)
  React.useEffect(() => {
    if (!messagesContainerRef.current) return;
    if (isInitialMount.current) {
      isInitialMount.current = false;
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
      return;
    }
    messagesContainerRef.current.scrollTo({
      top: messagesContainerRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, isLoading]);

  // Dynamic auto-grow for textarea without native scrollbars
  React.useLayoutEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      const newHeight = Math.min(Math.max(el.scrollHeight, 42), 160);
      el.style.height = `${newHeight}px`;
    }
  }, [userMessage]);

  return (
    <div
      ref={rootRef}
      className={cn(
        "flex w-full flex-col rounded-[26px] bg-white transition-all",
        "border border-slate-200/80 shadow-[0_12px_40px_rgba(0,0,0,0.06),0_2px_6px_rgba(0,0,0,0.04)]",
        "dark:border-slate-800/80 dark:bg-slate-900/95 dark:shadow-[0_12px_40px_rgba(0,0,0,0.35),0_0_0_1px_rgba(255,255,255,0.08)]",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800/80 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-md shadow-emerald-500/20">
            <Sprout className="h-5 w-5" />
            <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-3 w-3 rounded-full border-2 border-white bg-emerald-500 dark:border-slate-900" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-[15px] font-semibold tracking-tight text-slate-900 dark:text-white">
                {title}
              </h3>
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60">
                Krishi AI
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <motion.button
            type="button"
            onClick={() => {
              setSpins((count) => count + 1);
              setUserMessage("");
              onReset?.();
            }}
            whileTap={{ scale: 0.9 }}
            title="Reset conversation"
            aria-label="Reset conversation"
            className="ai-chat-btn flex h-[32px] w-[32px] shrink-0 items-center justify-center rounded-full border border-slate-200/80 bg-white text-slate-500 transition-colors hover:text-slate-900 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-800/80 dark:text-slate-400 dark:hover:text-white dark:hover:border-slate-700 shadow-2xs"
            style={{ appearance: "none", WebkitAppearance: "none", outline: "none", borderRadius: "9999px" }}
          >
            <motion.span
              animate={{ rotate: spins * 360 }}
              transition={{ type: "spring", bounce: 0.2, duration: 0.7 }}
              className="flex"
            >
              <RefreshCw className="h-3.5 w-3.5" />
            </motion.span>
          </motion.button>

          {onClose && (
            <motion.button
              type="button"
              onClick={onClose}
              whileTap={{ scale: 0.9 }}
              title="Close assistant"
              aria-label="Close assistant"
              className="ai-chat-btn flex h-[32px] w-[32px] shrink-0 items-center justify-center rounded-full border border-slate-200/80 bg-white text-slate-500 transition-colors hover:text-slate-900 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-800/80 dark:text-slate-400 dark:hover:text-white dark:hover:border-slate-700 shadow-2xs"
              style={{ appearance: "none", WebkitAppearance: "none", outline: "none", borderRadius: "9999px" }}
            >
              <X className="h-4 w-4" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Body: Empty State OR Messages Stream */}
      {!hasMessages ? (
        <div className="flex flex-1 flex-col items-center justify-center px-6 py-10 text-center">
          <motion.div
            animate={{ y: [0, -4, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40 shadow-inner"
          >
            {icon ?? <Sparkles className="h-6 w-6" />}
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="mt-4 text-[17px] font-semibold tracking-tight text-slate-900 dark:text-white"
          >
            {greeting}
          </motion.p>
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="mt-1.5 max-w-[340px] text-xs leading-relaxed text-slate-500 dark:text-slate-400"
          >
            {prompt}
          </motion.p>

          {/* Quick suggestion chips */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="mt-5 flex flex-wrap justify-center gap-1.5 max-w-[420px]"
          >
            {SUGGESTION_CHIPS.map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => {
                  setUserMessage(chip.query);
                  onSend?.(chip.query);
                }}
                className="ai-chat-btn rounded-full border border-slate-200/90 bg-slate-50/80 px-3.5 py-1.5 text-xs font-medium text-slate-700 transition-all hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-800 dark:border-slate-800 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:border-emerald-500/50 dark:hover:bg-emerald-950/40 dark:hover:text-emerald-300 shadow-2xs"
                style={{ appearance: "none", WebkitAppearance: "none", outline: "none", borderRadius: "9999px" }}
              >
                {chip.label}
              </button>
            ))}
          </motion.div>
        </div>
      ) : (
        <div
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto px-5 py-4 space-y-4 max-h-[480px] min-h-[320px] scroll-smooth"
        >
          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25 }}
                className={cn(
                  "flex flex-col",
                  m.role === "user" ? "items-end" : "items-start"
                )}
              >
                <div
                  className={cn(
                    "relative max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    m.role === "user"
                      ? "bg-emerald-600 text-white shadow-sm rounded-tr-xs dark:bg-emerald-600"
                      : "bg-slate-100/90 text-slate-900 border border-slate-200/70 rounded-tl-xs dark:bg-slate-800/90 dark:text-slate-100 dark:border-slate-700/60"
                  )}
                >
                  {/* Attached photo in message bubble if present */}
                  {m.image && (
                    <div className="mb-2 max-w-[260px] overflow-hidden rounded-xl border border-white/20 shadow-xs">
                      <img
                        src={m.image}
                        alt="Uploaded crop photo"
                        className="max-h-52 w-full rounded-xl object-cover bg-black/10"
                      />
                    </div>
                  )}

                  {m.isVoice && (
                    <span className="mr-1.5 inline-flex items-center text-xs opacity-90">
                      🎤
                    </span>
                  )}
                  <FormattedMessage content={m.content} isUser={m.role === "user"} />

                  {/* Actions for assistant message: Professional Speaker & Copy Buttons */}
                  {m.role === "assistant" && (
                    <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-200/70 pt-2.5 dark:border-slate-700/60">
                      <span className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 select-none">
                        <Sprout className="h-3.5 w-3.5" />
                        <span>Krishi Mitra AI</span>
                      </span>

                      <div className="flex items-center gap-2">
                        {/* Professional Speaker (Listen) Button */}
                        {onListen && (
                          <button
                            type="button"
                            onClick={() => onListen(m.id, m.content)}
                            title={playingMessageId === m.id ? "Stop voice audio" : "Listen to answer in voice"}
                            aria-label="Listen to answer"
                            className={cn(
                              "ai-chat-btn group inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-all duration-200 shadow-2xs active:scale-95",
                              playingMessageId === m.id
                                ? "border border-emerald-500 bg-emerald-600 text-white shadow-emerald-500/25 animate-pulse"
                                : "border border-slate-200/90 bg-white/90 text-slate-700 hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-800 dark:border-slate-700/80 dark:bg-slate-800/80 dark:text-slate-300 dark:hover:border-emerald-500/60 dark:hover:bg-slate-700 dark:hover:text-emerald-300"
                            )}
                            style={{ appearance: "none", WebkitAppearance: "none", outline: "none", borderRadius: "9999px" }}
                          >
                            {playingMessageId === m.id ? (
                              <>
                                <VolumeX className="h-3.5 w-3.5 text-white" />
                                <span>Stop</span>
                              </>
                            ) : (
                              <>
                                <Volume2 className="h-3.5 w-3.5 text-slate-500 group-hover:text-emerald-600 dark:text-slate-400 dark:group-hover:text-emerald-300" />
                                <span>Listen</span>
                              </>
                            )}
                          </button>
                        )}

                        {/* Professional Copy Button */}
                        <button
                          type="button"
                          onClick={() => handleCopy(m.id, m.content)}
                          title="Copy response to clipboard"
                          aria-label="Copy response"
                          className={cn(
                            "ai-chat-btn group inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-all duration-200 shadow-2xs active:scale-95",
                            copiedId === m.id
                              ? "border border-emerald-400 bg-emerald-50 text-emerald-700 dark:border-emerald-500 dark:bg-emerald-950/60 dark:text-emerald-300"
                              : "border border-slate-200/90 bg-white/90 text-slate-700 hover:border-slate-300 hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700/80 dark:bg-slate-800/80 dark:text-slate-300 dark:hover:border-slate-600 dark:hover:bg-slate-700 dark:hover:text-white"
                          )}
                          style={{ appearance: "none", WebkitAppearance: "none", outline: "none", borderRadius: "9999px" }}
                        >
                          {copiedId === m.id ? (
                            <>
                              <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                              <span>Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3.5 w-3.5 text-slate-500 group-hover:text-slate-800 dark:text-slate-400 dark:group-hover:text-slate-200" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing shimmer while awaiting response */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 rounded-2xl rounded-tl-xs bg-slate-100/90 dark:bg-slate-800/90 border border-slate-200/70 dark:border-slate-700/60 px-4 py-3 text-xs text-slate-500 dark:text-slate-400 max-w-[180px]"
            >
              <div className="flex gap-1 items-center">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.3s]" />
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.15s]" />
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce" />
              </div>
              <span className="ml-1 text-[11px] font-medium text-slate-600 dark:text-slate-300">
                AI is typing…
              </span>
            </motion.div>
          )}
        </div>
      )}

      {/* Composer (21st.dev signature AI PromptBox) */}
      <div className="px-5 pb-5 pt-2">
        <div
          data-chat-composer
          className="relative flex flex-col rounded-[24px] border border-slate-200/90 bg-slate-50/70 p-3.5 shadow-xs transition-all duration-200 focus-within:border-emerald-500/60 focus-within:bg-white focus-within:shadow-[0_8px_30px_rgba(16,185,129,0.12)] focus-within:ring-2 focus-within:ring-emerald-500/20 dark:border-slate-800 dark:bg-slate-800/60 dark:focus-within:border-emerald-500/50 dark:focus-within:bg-slate-900 dark:focus-within:ring-emerald-500/15"
        >
          {/* File Attachment Preview Card */}
          {attachedFile && (
            <div className="mb-2.5 flex items-center gap-3 rounded-2xl border border-slate-200/90 bg-white/95 p-2 pr-3 shadow-xs dark:border-slate-700/80 dark:bg-slate-800/95 max-w-fit">
              {attachedFile.isImage ? (
                <img
                  src={attachedFile.preview}
                  alt={attachedFile.name}
                  className="h-12 w-12 rounded-xl object-cover border border-slate-200/80 dark:border-slate-700/80"
                />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
                  <FileText className="h-6 w-6" />
                </div>
              )}
              <div className="flex flex-col text-left pr-1">
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-100 max-w-[190px] truncate">
                  {attachedFile.name}
                </span>
                <span className="text-[10px] text-slate-400 dark:text-slate-500">
                  {attachedFile.size} • Ready to upload & analyze
                </span>
              </div>
              <button
                type="button"
                onClick={() => setAttachedFile(null)}
                title="Remove attachment"
                aria-label="Remove attachment"
                className="ai-chat-btn flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 text-slate-500 hover:bg-red-50 hover:text-red-600 dark:bg-slate-700 dark:text-slate-400 dark:hover:bg-red-950/60 dark:hover:text-red-400 transition-colors"
                style={{ appearance: "none", WebkitAppearance: "none", outline: "none", borderRadius: "9999px" }}
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          )}

          {/* Hidden File Picker Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="image/*, .png, .jpg, .jpeg, .webp, .pdf, .txt"
            aria-label="Upload crop image or document"
          />

          {/* Main Input Textarea with Low-Shade Ghost Animated Hint */}
          <div className="relative w-full">
            <textarea
              ref={textareaRef}
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              aria-label="Your farming question"
              className="ai-chat-textarea relative z-10 w-full resize-none border-0 bg-transparent px-1 py-1 text-[15px] font-normal leading-relaxed text-slate-900 focus:outline-none dark:text-slate-100 min-h-[42px] max-h-[160px]"
              style={{
                border: "none",
                outline: "none",
                boxShadow: "none",
                background: "transparent",
                resize: "none",
                appearance: "none",
                WebkitAppearance: "none",
              }}
            />

            {/* Low-shade animated hint example (purely visual ghost placeholder; cannot be clicked, used or submitted) */}
            {!userMessage && (
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 z-0 flex items-start px-1 py-1 select-none overflow-hidden text-[15px] font-normal leading-relaxed text-slate-400/80 dark:text-slate-500/80"
              >
                <span className="truncate">
                  {attachedFile
                    ? "Add any details or ask a question about this crop…"
                    : typedMessage || placeholder}
                </span>
                {!attachedFile && (
                  <motion.span
                    className="ml-0.5 inline-block h-4 w-[1.5px] bg-slate-400/60 dark:bg-slate-500/60 align-middle shrink-0"
                    animate={{ opacity: [1, 1, 0, 0] }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      times: [0, 0.5, 0.5, 1],
                    }}
                  />
                )}
              </div>
            )}
          </div>

          <div className="mt-2.5 flex items-center justify-between border-t border-slate-200/60 dark:border-slate-700/50 pt-2">
            <div className="flex items-center gap-2">
              {/* Attach / Scan leaf action */}
              <motion.button
                type="button"
                onClick={handlePlusClick}
                whileHover={{ scale: 1.06 }}
                whileTap={{ scale: 0.92 }}
                title="Upload crop photo or document"
                aria-label="Upload file"
                className="ai-chat-btn group flex h-[34px] w-[34px] items-center justify-center rounded-full border border-slate-200/90 bg-white text-slate-600 shadow-2xs transition-colors hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-emerald-500/60 dark:hover:bg-slate-750 dark:hover:text-emerald-300"
                style={{
                  appearance: "none",
                  WebkitAppearance: "none",
                  outline: "none",
                  borderRadius: "9999px",
                }}
              >
                <Plus className="h-4 w-4 transition-transform duration-200 group-hover:rotate-90" strokeWidth={2.2} />
              </motion.button>

              {/* Voice / Mic dictate button */}
              {onToggleMic && (
                <motion.button
                  type="button"
                  onClick={onToggleMic}
                  whileHover={{ scale: 1.06 }}
                  whileTap={{ scale: 0.92 }}
                  title={isRecording ? "Stop dictation" : "Dictate in Kannada, Hindi, English…"}
                  aria-label="Voice input"
                  className={cn(
                    "ai-chat-btn flex h-[34px] w-[34px] items-center justify-center rounded-full border shadow-2xs transition-all duration-200",
                    isRecording
                      ? "border-red-500 bg-red-500 text-white shadow-md shadow-red-500/30 animate-pulse"
                      : "border-slate-200/90 bg-white text-slate-600 hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-emerald-500/60 dark:hover:bg-slate-750 dark:hover:text-emerald-300"
                  )}
                  style={{
                    appearance: "none",
                    WebkitAppearance: "none",
                    outline: "none",
                    borderRadius: "9999px",
                  }}
                >
                  {isRecording ? <MicOff className="h-4 w-4" strokeWidth={2.2} /> : <Mic className="h-4 w-4" strokeWidth={2.2} />}
                </motion.button>
              )}

              {/* Multilingual Badge (21st.dev style indicator) */}
              <div className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-emerald-200/60 bg-emerald-50/80 px-2.5 py-1 text-[11px] font-medium text-emerald-800 dark:border-emerald-800/40 dark:bg-emerald-950/40 dark:text-emerald-300 select-none">
                <Sprout className="h-3 w-3 text-emerald-600 dark:text-emerald-400" />
                <span>Multilingual AI</span>
              </div>
            </div>

            {/* Send button: only active when user explicitly typed something or attached a file */}
            {(() => {
              const canSend = (userMessage.trim().length > 0 || Boolean(attachedFile)) && !isLoading;
              return (
                <motion.button
                  type="button"
                  onClick={handleSend}
                  disabled={!canSend}
                  whileHover={
                    canSend
                      ? {
                          scale: 1.08,
                          transition: { type: "spring", bounce: 0.5, duration: 0.3 },
                        }
                      : {}
                  }
                  whileTap={
                    canSend
                      ? {
                          scale: 0.9,
                          transition: { type: "spring", bounce: 0.5, duration: 0.2 },
                        }
                      : {}
                  }
                  aria-label="Send message"
                  className={cn(
                    "ai-chat-btn group flex h-[34px] w-[34px] items-center justify-center rounded-full transition-all duration-200 shadow-sm",
                    canSend
                      ? "bg-emerald-600 text-white shadow-emerald-600/30 hover:bg-emerald-500 hover:shadow-md dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400 cursor-pointer"
                      : "bg-slate-200/80 text-slate-400 dark:bg-slate-800 dark:text-slate-600 border border-slate-200/60 dark:border-slate-700/60 cursor-not-allowed opacity-60"
                  )}
                  style={{
                    appearance: "none",
                    WebkitAppearance: "none",
                    outline: "none",
                    borderRadius: "9999px",
                  }}
                >
                  <ArrowUp className="h-4 w-4 transition-transform duration-200 group-hover:-translate-y-0.5" strokeWidth={2.4} />
                </motion.button>
              );
            })()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AIChatCard;

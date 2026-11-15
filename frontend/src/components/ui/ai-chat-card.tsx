import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  ArrowUp,
  Plus,
  RefreshCw,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Copy,
  Check,
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
  /** Saved ChatMessage id when it differs from `id` (streamed replies keep a stable id). */
  serverId?: string | number;
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
  /** Phone-only back arrow in the header (full-screen chat page). */
  onBack?: () => void;
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
  { label: "Tomato Blight", query: "What are tomato early blight symptoms and treatments?" },
  { label: "Urea Dosage", query: "What is the recommended fertilizer and urea dose for paddy?" },
  { label: "Spray Weather", query: "What are the optimal weather conditions for pesticide spraying?" },
  { label: "PM-KISAN", query: "How does PM-KISAN scheme work and who is eligible?" },
  { label: "Mandi Prices", query: "How to check today's APMC mandi market prices for crops?" },
];

export function AIChatCard({
  title = "Farm Assistant",
  subtitle = "Agricultural Advisory & Field Guidance",
  greeting = "Namaste, Farmer",
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
  onBack,
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

  // Follow a streaming reply as it grows, unless the farmer has scrolled up to read.
  const lastContent = messages[messages.length - 1]?.content;
  React.useEffect(() => {
    const el = messagesContainerRef.current;
    if (!el) return;
    if (el.scrollHeight - el.scrollTop - el.clientHeight < 120) {
      el.scrollTop = el.scrollHeight;
    }
  }, [lastContent]);

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
        "ai-chat-card-surface flex w-full flex-col rounded-2xl overflow-hidden transition-all",
        "border border-slate-200 shadow-sm",
        "dark:border-slate-800 dark:shadow-[0_4px_20px_rgba(0,0,0,0.35)]",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800/80 px-3.5 sm:px-5 py-3 sm:py-4">
        <div className="flex items-center gap-2.5 sm:gap-3">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              aria-label="Back"
              className="ai-chat-btn ai-chat-back flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-600 md:hidden dark:border-slate-800 dark:text-slate-300"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
          )}
          <div className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-700 text-white">
            <Sprout className="h-4 w-4 sm:h-5 sm:w-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 sm:gap-2">
              <h3 className="text-sm sm:text-[15px] font-semibold tracking-tight text-slate-900 dark:text-white">
                {title}
              </h3>
              <span className="rounded-md bg-emerald-50 px-1.5 sm:px-2 py-0.5 text-[9px] sm:text-[10px] font-medium text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60">
                Advisory
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 line-clamp-1">{subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-1.5">
          <motion.button
            type="button"
            onClick={() => {
              setSpins((count) => count + 1);
              setUserMessage("");
              onReset?.();
            }}
            whileTap={{ scale: 0.95 }}
            title="Reset conversation"
            aria-label="Reset conversation"
            className="ai-chat-btn flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:text-slate-900 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-800/80 dark:text-slate-400 dark:hover:text-white"
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
              whileTap={{ scale: 0.95 }}
              title="Close assistant"
              aria-label="Close assistant"
              className="ai-chat-btn flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:text-slate-900 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-800/80 dark:text-slate-400 dark:hover:text-white"
            >
              <X className="h-4 w-4" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Body: Empty State OR Messages Stream */}
      {!hasMessages ? (
        <div className="flex flex-1 flex-col items-center justify-center px-4 sm:px-6 py-6 sm:py-10 text-center">
          <div className="flex h-10 w-10 sm:h-11 sm:w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40">
            {icon ?? <Sprout className="h-5 w-5" />}
          </div>

          <p className="mt-3 sm:mt-4 text-[15px] sm:text-[16px] font-semibold tracking-tight text-slate-900 dark:text-white">
            {greeting}
          </p>
          <p className="mt-1 max-w-[340px] text-xs leading-relaxed text-slate-500 dark:text-slate-400">
            {prompt}
          </p>

          {/* Quick suggestion chips */}
          <div className="mt-4 sm:mt-5 flex flex-wrap justify-center gap-1.5 max-w-full sm:max-w-[440px]">
            {SUGGESTION_CHIPS.map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => {
                  setUserMessage(chip.query);
                  onSend?.(chip.query);
                }}
                className="ai-chat-btn ai-chat-chip rounded-lg border border-slate-200 bg-slate-50 px-2.5 sm:px-3 py-1 sm:py-1.5 text-[11px] sm:text-xs font-medium text-slate-700 transition-colors hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-800 dark:border-slate-800 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-emerald-500/50 dark:hover:bg-emerald-950/40 dark:hover:text-emerald-300"
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div
          ref={messagesContainerRef}
          className="ai-chat-messages flex-1 overflow-y-auto px-3 sm:px-5 py-3 sm:py-4 space-y-3.5 sm:space-y-4 max-h-[500px] min-h-[300px] scroll-smooth"
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
                    "relative max-w-[92%] sm:max-w-[85%] rounded-xl px-3.5 sm:px-4 py-2 sm:py-2.5 text-sm leading-relaxed",
                    m.role === "user"
                      ? "bg-emerald-700 text-white rounded-tr-xs shadow-xs dark:bg-emerald-600"
                      : "bg-slate-100 text-slate-900 border border-slate-200/80 rounded-tl-xs dark:bg-slate-800/90 dark:text-slate-100 dark:border-slate-700/60"
                  )}
                >
                  {/* Attached photo in message bubble if present */}
                  {m.image && (
                    <div className="mb-2 max-w-[260px] overflow-hidden rounded-lg border border-black/10">
                      <img
                        src={m.image}
                        alt="Uploaded crop photo"
                        className="max-h-52 w-full rounded-lg object-cover bg-black/10"
                      />
                    </div>
                  )}

                  {m.isVoice && (
                    <span className="mr-1.5 inline-flex items-center text-xs opacity-90">
                      <Mic className="h-3.5 w-3.5" />
                    </span>
                  )}
                  <FormattedMessage content={m.content} isUser={m.role === "user"} />

                  {/* Actions for assistant message */}
                  {m.role === "assistant" && (
                    <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-200/70 pt-2 dark:border-slate-700/60">
                      <span className="flex items-center gap-1.5 text-[11px] font-medium text-emerald-800 dark:text-emerald-400 select-none">
                        <Sprout className="h-3.5 w-3.5" />
                        <span>Krishi Mitra</span>
                      </span>

                      <div className="flex items-center gap-1.5">
                        {/* Listen Button */}
                        {onListen && (
                          <button
                            type="button"
                            onClick={() => onListen(m.id, m.content)}
                            title={playingMessageId === m.id ? "Stop voice audio" : "Listen to answer"}
                            aria-label="Listen to answer"
                            className={cn(
                              "ai-chat-btn inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors border active:scale-95",
                              playingMessageId === m.id
                                ? "border-emerald-600 bg-emerald-700 text-white"
                                : "border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-200/60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-700"
                            )}
                          >
                            {playingMessageId === m.id ? (
                              <>
                                <VolumeX className="h-3.5 w-3.5 text-white" />
                                <span>Stop</span>
                              </>
                            ) : (
                              <>
                                <Volume2 className="h-3.5 w-3.5 text-slate-500 dark:text-slate-400" />
                                <span>Listen</span>
                              </>
                            )}
                          </button>
                        )}

                        {/* Copy Button */}
                        <button
                          type="button"
                          onClick={() => handleCopy(m.id, m.content)}
                          title="Copy response"
                          aria-label="Copy response"
                          className={cn(
                            "ai-chat-btn inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors border active:scale-95",
                            copiedId === m.id
                              ? "border-emerald-500 bg-emerald-50 text-emerald-800 dark:border-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-300"
                              : "border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-200/60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-700"
                          )}
                        >
                          {copiedId === m.id ? (
                            <>
                              <Check className="h-3.5 w-3.5 text-emerald-700 dark:text-emerald-400" />
                              <span>Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3.5 w-3.5 text-slate-500 dark:text-slate-400" />
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

          {/* Response loading indicator */}
          {isLoading && (
            <div className="flex items-center gap-2 rounded-xl rounded-tl-xs bg-slate-100 dark:bg-slate-800/90 border border-slate-200/70 dark:border-slate-700/60 px-3.5 py-2.5 text-xs text-slate-500 dark:text-slate-400 max-w-[180px]">
              <div className="flex gap-1 items-center">
                <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dark:bg-slate-500 animate-pulse" />
                <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dark:bg-slate-500 animate-pulse [animation-delay:0.2s]" />
                <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dark:bg-slate-500 animate-pulse [animation-delay:0.4s]" />
              </div>
              <span className="ml-1 text-[11px] font-medium text-slate-600 dark:text-slate-300">
                Consulting advisory…
              </span>
            </div>
          )}
        </div>
      )}

      {/* Composer */}
      <div className="px-3 sm:px-5 pb-3 sm:pb-5 pt-1.5 sm:pt-2">
        <div
          data-chat-composer
          className="ai-chat-composer relative flex flex-col rounded-xl border border-slate-200 p-2.5 sm:p-3 shadow-2xs transition-colors focus-within:border-emerald-600 focus-within:ring-1 focus-within:ring-emerald-600 dark:border-slate-800 dark:bg-slate-800 dark:focus-within:border-emerald-500 dark:focus-within:ring-emerald-500"
        >
          {/* File Attachment Preview Card */}
          {attachedFile && (
            <div className="mb-2 flex items-center gap-2.5 rounded-lg border border-slate-200 p-1.5 pr-2.5 shadow-2xs dark:border-slate-700 dark:bg-slate-800 max-w-fit">
              {attachedFile.isImage ? (
                <img
                  src={attachedFile.preview}
                  alt={attachedFile.name}
                  className="h-10 w-10 rounded-md object-cover border border-slate-200 dark:border-slate-700"
                />
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400">
                  <FileText className="h-5 w-5" />
                </div>
              )}
              <div className="flex flex-col text-left pr-1">
                <span className="text-xs font-medium text-slate-800 dark:text-slate-100 max-w-[190px] truncate">
                  {attachedFile.name}
                </span>
                <span className="text-[10px] text-slate-500">
                  {attachedFile.size} • Ready
                </span>
              </div>
              <button
                type="button"
                onClick={() => setAttachedFile(null)}
                title="Remove attachment"
                aria-label="Remove attachment"
                className="ai-chat-btn flex h-5 w-5 items-center justify-center rounded-md text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-slate-200 transition-colors"
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
            aria-label="Upload crop photo or document"
          />

          {/* Main Input Textarea */}
          <div className="relative w-full">
            <textarea
              ref={textareaRef}
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              aria-label="Your farming question"
              className="ai-chat-textarea relative z-10 w-full resize-none border-0 bg-transparent px-1 py-1 text-[14px] font-normal leading-relaxed text-slate-900 focus:outline-none dark:text-slate-100 min-h-[40px] max-h-[160px]"
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

            {!userMessage && (
              <div
                aria-hidden="true"
                className="ai-chat-ghost-placeholder pointer-events-none absolute inset-0 z-0 flex items-start px-1 py-1 select-none overflow-hidden text-[14px] font-normal leading-relaxed text-slate-400 dark:text-slate-500"
              >
                <span className="truncate">
                  {attachedFile
                    ? "Add any details or ask a question about this crop…"
                    : typedMessage || placeholder}
                </span>
              </div>
            )}
          </div>

          <div className="mt-2 flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-2">
            <div className="flex items-center gap-1.5">
              {/* Attach / Scan leaf action */}
              <button
                type="button"
                onClick={handlePlusClick}
                title="Upload crop photo or document"
                aria-label="Upload file"
                className="ai-chat-btn group flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                <Plus className="h-4 w-4" strokeWidth={1.75} />
              </button>

              {/* Voice / Mic dictate button */}
              {onToggleMic && (
                <button
                  type="button"
                  onClick={onToggleMic}
                  title={isRecording ? "Stop dictation" : "Dictate in Kannada, Hindi, English…"}
                  aria-label="Voice input"
                  className={cn(
                    "ai-chat-btn flex h-8 w-8 items-center justify-center rounded-full border transition-colors",
                    isRecording
                      ? "border-red-600 bg-red-600 text-white"
                      : "border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                  )}
                >
                  {isRecording ? <MicOff className="h-4 w-4" strokeWidth={1.75} /> : <Mic className="h-4 w-4" strokeWidth={1.75} />}
                </button>
              )}

              {/* Language guidance */}
              <span className="hidden sm:inline-block text-[11px] text-slate-500 dark:text-slate-400 select-none px-1">
                ಕನ್ನಡ · हिन्दी · English
              </span>
            </div>

            {/* Send button */}
            {(() => {
              const canSend = (userMessage.trim().length > 0 || Boolean(attachedFile)) && !isLoading;
              return (
                <button
                  type="button"
                  onClick={handleSend}
                  disabled={!canSend}
                  aria-label="Send message"
                  className={cn(
                    "ai-chat-btn flex h-8 w-8 items-center justify-center rounded-full transition-colors",
                    canSend
                      ? "bg-emerald-700 text-white hover:bg-emerald-800 dark:bg-emerald-600 dark:hover:bg-emerald-500 cursor-pointer"
                      : "bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-600 border border-slate-200 dark:border-slate-700 cursor-not-allowed opacity-60"
                  )}
                >
                  <ArrowUp className="h-4 w-4" strokeWidth={2} />
                </button>
              );
            })()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AIChatCard;

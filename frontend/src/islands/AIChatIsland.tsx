import { useState, useRef, useEffect } from "react";
import { AIChatCard } from "@/components/ui/ai-chat-card";
import type { ChatMessageItem } from "@/components/ui/ai-chat-card";

interface AIChatIslandProps {
  initialHistory?: Array<{
    id: number | string;
    message: string;
    response: string;
    is_voice?: boolean;
  }>;
  userName?: string;
  isWidget?: boolean;
  apiUrl?: string;
  speakUrl?: string;
  voiceUrl?: string;
}

export default function AIChatIsland({
  initialHistory = [],
  userName = "Farmer",
  isWidget = false,
  apiUrl = "/chat/api/",
  speakUrl = "/chat/api/speak/",
  voiceUrl = "/chat/api/voice/",
}: AIChatIslandProps) {
  // Ensure the page stays at the top on initial mount / refresh:
  useEffect(() => {
    if (typeof window !== "undefined" && !window.location.hash) {
      window.scrollTo(0, 0);
    }
  }, []);

  // When user navigates to another section or leaves the page, clear the messages
  useEffect(() => {
    const triggerClear = () => {
      try {
        const csrf = getCsrfToken();
        if (navigator.sendBeacon) {
          const blob = new Blob([JSON.stringify({})], { type: "application/json" });
          navigator.sendBeacon("/chat/api/clear/", blob);
        } else {
          fetch("/chat/api/clear/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrf,
            },
            keepalive: true,
          }).catch(() => {});
        }
      } catch {
        // ignore navigation unload errors
      }
    };

    const handleBeforeUnload = () => triggerClear();
    const handlePageHide = () => triggerClear();

    // Intercept clicks on links that navigate away to other sections
    const handleAnchorClick = (e: MouseEvent) => {
      const anchor = (e.target as HTMLElement)?.closest("a");
      if (anchor && anchor.href) {
        try {
          const targetUrl = new URL(anchor.href, window.location.href);
          if (
            targetUrl.origin === window.location.origin &&
            targetUrl.pathname !== window.location.pathname
          ) {
            triggerClear();
          }
        } catch {
          // ignore invalid url
        }
      }
    };

    // If restored from bfcache (browser back/forward button), start fresh
    const handlePageShow = (e: PageTransitionEvent) => {
      if (e.persisted) {
        setMessages([]);
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    window.addEventListener("pagehide", handlePageHide);
    window.addEventListener("pageshow", handlePageShow);
    document.addEventListener("click", handleAnchorClick, { capture: true });

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      window.removeEventListener("pagehide", handlePageHide);
      window.removeEventListener("pageshow", handlePageShow);
      document.removeEventListener("click", handleAnchorClick, { capture: true });
    };
  }, []);
  const [messages, setMessages] = useState<ChatMessageItem[]>(() => {
    if (!initialHistory || initialHistory.length === 0) return [];
    const items: ChatMessageItem[] = [];
    initialHistory.forEach((h) => {
      items.push({
        id: `user-${h.id}`,
        role: "user",
        content: h.message,
        isVoice: h.is_voice,
      });
      items.push({
        id: `bot-${h.id}`,
        role: "assistant",
        content: h.response,
      });
    });
    return items;
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [playingId, setPlayingId] = useState<string | number | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const activeMessageIdRef = useRef<string | number | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const stopAnySpeech = () => {
    // 1. Abort in-flight network request for audio
    if (abortControllerRef.current) {
      try {
        abortControllerRef.current.abort();
      } catch {}
      abortControllerRef.current = null;
    }

    // 2. Stop and release HTML5 Audio element
    if (currentAudioRef.current) {
      try {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
        currentAudioRef.current.src = "";
      } catch {}
      currentAudioRef.current = null;
    }

    // 3. Cancel browser native SpeechSynthesis
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      try {
        window.speechSynthesis.cancel();
      } catch {}
    }

    // 4. Reset tracking refs & state
    activeMessageIdRef.current = null;
    setPlayingId(null);
  };

  // Cleanup speech on unmount
  useEffect(() => {
    return () => {
      stopAnySpeech();
    };
  }, []);

  const getCsrfToken = () => {
    const input = document.querySelector<HTMLInputElement>(
      "[name=csrfmiddlewaretoken]"
    );
    if (input) return input.value;
    const cookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  };

  const handleSend = async (text: string, file?: File | null, previewUrl?: string) => {
    if ((!text.trim() && !file) || isLoading) return;

    // Halt any playing voice audio when sending a new message
    stopAnySpeech();

    const tempUserId = `user-${Date.now()}`;
    const userDisplayMsg = text.trim() || (file ? `Attached photo: ${file.name}` : "");
    const newMessages: ChatMessageItem[] = [
      ...messages,
      {
        id: tempUserId,
        role: "user",
        content: userDisplayMsg,
        image: previewUrl,
      },
    ];
    setMessages(newMessages);
    setIsLoading(true);

    // If an image is attached, run Crop Disease & Health Assessment via /disease/api/
    if (file && file.type.startsWith("image/")) {
      try {
        const formData = new FormData();
        formData.append("image", file);
        if (text.trim()) {
          formData.append("notes", text.trim());
        }

        const resp = await fetch("/disease/api/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCsrfToken(),
          },
          body: formData,
        });

        if (!resp.ok) {
          const errData = await resp.json().catch(() => ({}));
          throw new Error(errData.error || `HTTP ${resp.status}`);
        }

        const d = await resp.json();
        const condition = d.label || d.disease || "Crop Assessment";
        const plant = d.plant && d.plant !== "Not identified" ? `• Crop: ${d.plant}\n` : "";
        const diseaseType = d.disease_type && d.disease_type !== "unknown" ? `• Issue Category: ${d.disease_type}\n` : "";
        const summary = d.summary || d.disease_description || "";
        const actions =
          d.immediate_actions && d.immediate_actions.length > 0
            ? `\n\n**Immediate Actions:**\n• ${d.immediate_actions.slice(0, 4).join("\n• ")}`
            : "";
        const chemicals =
          d.chemical_options && d.chemical_options.length > 0
            ? `\n\n**Recommended Treatments:**\n• ${d.chemical_options
                .slice(0, 3)
                .map((c: any) => `${c.active_ingredient}: ${c.purpose}`)
                .join("\n• ")}`
            : "";
        const prevention =
          d.prevention && d.prevention.length > 0
            ? `\n\n**Prevention & Soil Care:**\n• ${d.prevention.slice(0, 3).join("\n• ")}`
            : "";

        const botReply = `🩺 **${condition}**\n${plant}${diseaseType}\n${summary}${actions}${chemicals}${prevention}`.trim();

        setMessages((prev) => [
          ...prev,
          {
            id: `bot-disease-${Date.now()}`,
            role: "assistant",
            content: botReply,
          },
        ]);
      } catch (err: any) {
        setMessages((prev) => [
          ...prev,
          {
            id: `bot-err-${Date.now()}`,
            role: "assistant",
            content:
              err.message ||
              "Could not analyze the photo. Please ensure it is a clear photo of an affected plant leaf and try again.",
          },
        ]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    try {
      const win = window as unknown as { CHAT_API_URL?: string };
      const endpoint = win.CHAT_API_URL || apiUrl;
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ message: text }),
      });

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const data = await resp.json();
      const botReply = data.reply || data.error || "Sorry, I could not process that request.";

      setMessages((prev) => [
        ...prev,
        {
          id: data.message_id ? `bot-${data.message_id}` : `bot-${Date.now()}`,
          role: "assistant",
          content: botReply,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          role: "assistant",
          content:
            "Connection issue. Please verify your network or try asking again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    stopAnySpeech();
    setMessages([]);

    // Persistently clear server-side database history so refreshing won't reload old chats
    try {
      await fetch("/chat/api/clear/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
      });

      // Clear the static history script tag in DOM
      const histScript = document.getElementById("chat-history-data");
      if (histScript) histScript.textContent = "[]";
    } catch (e) {
      console.warn("Failed to clear backend chat history:", e);
    }
  };

  const handleClose = () => {
    stopAnySpeech();
    const widget = document.getElementById("chat-widget");
    if (widget) {
      widget.classList.add("d-none");
    }
  };

  const handleToggleMic = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        if (audioBlob.size < 500) return;

        const formData = new FormData();
        formData.append("audio", audioBlob, "voice.webm");

        setIsLoading(true);
        try {
          const win = window as unknown as { CHAT_VOICE_URL?: string };
          const endpoint = win.CHAT_VOICE_URL || voiceUrl;
          const resp = await fetch(endpoint, {
            method: "POST",
            headers: {
              "X-CSRFToken": getCsrfToken(),
            },
            body: formData,
          });

          if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
          const data = await resp.json();

          if (data.transcript && data.reply) {
            setMessages((prev) => [
              ...prev,
              {
                id: `user-${Date.now()}`,
                role: "user",
                content: data.transcript,
                isVoice: true,
              },
              {
                id: data.message_id ? `bot-${data.message_id}` : `bot-${Date.now()}`,
                role: "assistant",
                content: data.reply,
              },
            ]);
          }
        } catch (err) {
          console.error("Voice request error:", err);
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.warn("Microphone access denied or unavailable:", err);
      alert("Microphone access was denied. Please allow microphone permissions in your browser.");
    }
  };

  const handleListen = async (messageId: string | number, text: string) => {
    // If the user clicked Stop on the currently playing message:
    if (activeMessageIdRef.current === messageId || playingId === messageId) {
      stopAnySpeech();
      return;
    }

    // Stop any existing speech before starting a new one
    stopAnySpeech();

    // Mark this message as active
    activeMessageIdRef.current = messageId;
    setPlayingId(messageId);

    const numericId = String(messageId).replace(/^(bot-|user-)/, "");
    if (!numericId || isNaN(Number(numericId))) {
      playWithSpeechSynthesis(messageId, text);
      return;
    }

    try {
      const abortCtrl = new AbortController();
      abortControllerRef.current = abortCtrl;

      const win = window as unknown as { CHAT_SPEAK_URL?: string };
      const endpoint = `${win.CHAT_SPEAK_URL || speakUrl}${numericId}/`;
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
        signal: abortCtrl.signal,
      });

      if (!resp.ok) throw new Error("TTS endpoint error");
      const data = await resp.json();

      // Check if user clicked Stop while network request was in-flight
      if (activeMessageIdRef.current !== messageId) {
        return;
      }

      if (data.audios && data.audios.length > 0) {
        let chunkIdx = 0;
        const playNext = () => {
          if (activeMessageIdRef.current !== messageId) return;
          if (chunkIdx >= data.audios.length) {
            stopAnySpeech();
            return;
          }
          const audioSrc = `data:audio/mp3;base64,${data.audios[chunkIdx]}`;
          const audio = new Audio(audioSrc);
          currentAudioRef.current = audio;
          chunkIdx++;

          audio.onended = () => {
            if (activeMessageIdRef.current === messageId) {
              playNext();
            }
          };
          audio.onerror = () => {
            stopAnySpeech();
          };

          audio.play().catch(() => {
            if (activeMessageIdRef.current === messageId) {
              playWithSpeechSynthesis(messageId, text);
            }
          });
        };

        playNext();
      } else {
        playWithSpeechSynthesis(messageId, text);
      }
    } catch (err: any) {
      // If user intentionally aborted, don't fall back to speech synthesis
      if (err?.name === "AbortError" || activeMessageIdRef.current !== messageId) {
        return;
      }
      playWithSpeechSynthesis(messageId, text);
    }
  };

  const playWithSpeechSynthesis = (msgId: string | number, textToSpeak: string) => {
    if (activeMessageIdRef.current !== msgId) return;
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      stopAnySpeech();
      return;
    }

    try {
      window.speechSynthesis.cancel();

      // Strip markdown symbols before speaking
      const cleanText = textToSpeak
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .replace(/(?:^|\n)\s*[*•\-+]\s+/g, ". ")
        .replace(/[`#_]/g, "")
        .trim();

      const utterance = new SpeechSynthesisUtterance(cleanText);

      // Detect script to assign correct language and phonetics
      let langCode = "en-IN";
      for (let i = 0; i < cleanText.length; i++) {
        const cp = cleanText.charCodeAt(i);
        if (cp >= 0x0c80 && cp <= 0x0cff) {
          langCode = "kn-IN"; // Kannada
          break;
        }
        if (cp >= 0x0900 && cp <= 0x097f) {
          langCode = "hi-IN"; // Hindi
          break;
        }
        if (cp >= 0x0c00 && cp <= 0x0c7f) {
          langCode = "te-IN"; // Telugu
          break;
        }
        if (cp >= 0x0b80 && cp <= 0x0bff) {
          langCode = "ta-IN"; // Tamil
          break;
        }
      }
      utterance.lang = langCode;

      const voices = window.speechSynthesis.getVoices?.() || [];
      const prefix = langCode.split("-")[0].toLowerCase();
      const matchingVoice = voices.find((v) =>
        v.lang.toLowerCase().replace("_", "-").startsWith(prefix)
      );
      if (matchingVoice) {
        utterance.voice = matchingVoice;
      }

      utterance.onend = () => {
        if (activeMessageIdRef.current === msgId) {
          stopAnySpeech();
        }
      };
      utterance.onerror = () => {
        if (activeMessageIdRef.current === msgId) {
          stopAnySpeech();
        }
      };

      window.speechSynthesis.speak(utterance);
    } catch {
      stopAnySpeech();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto py-2">
      <AIChatCard
        title="Krishi Mitra Farm Assistant"
        subtitle="Expert Agricultural AI Companion"
        greeting={`Namaste, ${userName}!`}
        prompt="Ask anything about crop management, plant pests, fertilizers, spraying weather, or mandi prices in any language."
        messages={messages}
        isLoading={isLoading}
        isRecording={isRecording}
        playingMessageId={playingId}
        onSend={handleSend}
        onReset={handleReset}
        onClose={isWidget ? handleClose : undefined}
        onToggleMic={handleToggleMic}
        onListen={handleListen}
        className="w-full min-h-[540px] shadow-2xl"
      />
    </div>
  );
}

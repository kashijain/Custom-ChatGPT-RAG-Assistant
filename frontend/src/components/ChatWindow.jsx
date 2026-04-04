import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { FileSearch } from "lucide-react";
import MessageBubble from "./MessageBubble";

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start"
    >
      <div className="rounded-[28px] border border-line bg-white/5 px-5 py-4 backdrop-blur-xl">
        <div className="flex gap-2">
          {[0, 1, 2].map((dot) => (
            <motion.span
              key={dot}
              animate={{ y: [0, -6, 0], opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: dot * 0.15 }}
              className="h-2.5 w-2.5 rounded-full bg-blue-400"
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-xl rounded-[32px] border border-line bg-panel p-10 text-center shadow-2xl backdrop-blur-xl"
      >
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-[28px] bg-blue-500/10 text-blue-300 shadow-glow">
          <FileSearch size={34} />
        </div>
        <h2 className="text-3xl font-semibold tracking-tight text-white">
          Upload a PDF to start chatting
        </h2>
        <p className="mt-4 text-sm leading-7 text-slate-400">
          Your assistant will answer only from retrieved document chunks and surface source snippets for transparency.
        </p>
      </motion.div>
    </div>
  );
}

function ChatWindow({ messages, isThinking, hasUploadedFiles, activeDocument }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  if (!hasUploadedFiles && messages.length <= 1) {
    return <EmptyState />;
  }

  return (
    <div className="custom-scrollbar flex-1 overflow-y-auto px-4 py-8 md:px-8">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8">
        {activeDocument && (
          <div className="mx-auto rounded-full border border-blue-500/20 bg-blue-500/10 px-5 py-2.5 text-xs uppercase tracking-[0.22em] text-blue-200 backdrop-blur-xl">
            Active document: {activeDocument}
          </div>
        )}

        {messages.map((message, index) => (
          <MessageBubble key={`${message.role}-${index}`} message={message} />
        ))}

        {isThinking && <TypingIndicator />}
        <div ref={endRef} />
      </div>
    </div>
  );
}

export default ChatWindow;

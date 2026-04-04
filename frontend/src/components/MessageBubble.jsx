import { motion } from "framer-motion";
import { Bot, User, BookOpenText } from "lucide-react";
import SourceCard from "./SourceCard";

function renderInlineMarkdown(text) {
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={`${part}-${index}`} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }

    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

function FormattedAnswer({ content, isUser }) {
  const lines = String(content || "").split(/\r?\n/).filter((line) => line.trim() !== "");

  if (isUser) {
    return <p className="whitespace-pre-line text-[15px] leading-7">{content}</p>;
  }

  return (
    <div className="space-y-3">
      {lines.map((line, index) => {
        const bulletMatch = line.match(/^[-*]\s+(.*)$/);

        if (bulletMatch) {
          return (
            <div key={`${line}-${index}`} className="flex gap-3 text-[15px] leading-8 text-slate-100">
              <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-400" />
              <p>{renderInlineMarkdown(bulletMatch[1])}</p>
            </div>
          );
        }

        return (
          <p key={`${line}-${index}`} className="text-[15px] leading-8 text-slate-100">
            {renderInlineMarkdown(line)}
          </p>
        );
      })}
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div className={`flex max-w-[92%] gap-4 md:max-w-[80%] ${isUser ? "flex-row-reverse" : ""}`}>
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl ${
            isUser
              ? "bg-gradient-to-br from-blue-500 to-cyan-400 text-white shadow-glow"
              : "border border-line bg-white/5 text-blue-200"
          }`}
        >
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>

        <div className="space-y-4">
          <div
            className={`rounded-[28px] px-6 py-5 backdrop-blur-xl ${
              isUser
                ? "bg-gradient-to-br from-blue-600 to-blue-500 text-white shadow-glow"
                : "border border-line bg-white/5 text-slate-100 shadow-[0_20px_60px_rgba(15,23,42,0.35)]"
            }`}
          >
            {!isUser && (
              <p className="mb-3 text-xs uppercase tracking-[0.25em] text-blue-200/80">
                Main Answer
              </p>
            )}
            <FormattedAnswer content={message.content} isUser={isUser} />
          </div>

          {!isUser && message.sources?.length > 0 && (
            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-2 px-1 text-xs uppercase tracking-[0.24em] text-slate-500">
                <BookOpenText size={14} className="text-blue-300" />
                Sources from your document
              </div>
              {message.sources.map((source, index) => (
                <SourceCard key={`${source.source || source.filename || "source"}-${index}`} source={source} />
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export default MessageBubble;

import { motion } from "framer-motion";
import { FileText, Sparkles } from "lucide-react";

const MAX_SNIPPET_LENGTH = 320;

function SourceCard({ source }) {
  const label = source.source || source.filename || "Uploaded PDF";
  const rawSnippet = source.text || "Source snippet unavailable.";
  const snippet =
    rawSnippet.length > MAX_SNIPPET_LENGTH
      ? `${rawSnippet.slice(0, MAX_SNIPPET_LENGTH).trim()}...`
      : rawSnippet;
  const score = source.relevance_score || source.score;

  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.01 }}
      className="rounded-[26px] border border-blue-500/10 bg-white/5 p-5 backdrop-blur-xl transition-all duration-300 hover:border-blue-500/30 hover:bg-white/10 hover:shadow-card-hover"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-300">
            <FileText size={18} />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-100">{label}</p>
            <div className="mt-1 inline-flex items-center gap-1.5 rounded-full border border-blue-500/15 bg-blue-500/10 px-2.5 py-1 text-[10px] uppercase tracking-[0.22em] text-blue-200">
              <Sparkles size={11} />
              Retrieved from PDF
            </div>
          </div>
        </div>
        {score !== undefined && (
          <span className="shrink-0 rounded-full border border-line bg-white/5 px-3 py-1.5 text-xs font-medium text-blue-200">
            Score {Number(score).toFixed(2)}
          </span>
        )}
      </div>
      <p className="rounded-3xl border border-line bg-black/20 p-4 text-sm leading-7 text-slate-300">
        {snippet}
      </p>
    </motion.div>
  );
}

export default SourceCard;

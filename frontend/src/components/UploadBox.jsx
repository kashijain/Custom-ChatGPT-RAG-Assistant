import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, UploadCloud } from "lucide-react";

function UploadBox({ onUpload, isUploading, selectedFileName, activeDocument }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (files) => {
    const file = files?.[0];
    if (file) onUpload(file);
  };

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      className={`rounded-[28px] border border-dashed p-6 transition-all duration-300 ${
        isDragging
          ? "border-blue-400 bg-blue-500/10 shadow-glow"
          : "border-slate-700/60 bg-white/5 hover:border-blue-500/40 hover:bg-white/10"
      }`}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />

      <div className="flex flex-col items-center text-center">
        <motion.div
          animate={{ y: [0, -6, 0] }}
          transition={{ duration: 2.4, repeat: Infinity }}
          className="mb-4 flex h-16 w-16 items-center justify-center rounded-3xl bg-blue-500/10 text-blue-300"
        >
          {isUploading ? <Loader2 className="animate-spin" size={28} /> : <UploadCloud size={28} />}
        </motion.div>

        <h3 className="text-base font-semibold text-white">
          {isUploading ? "Uploading PDF..." : "Drag & drop your PDF"}
        </h3>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          Or browse a document to build a private knowledge base instantly.
        </p>

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
          className="mt-5 rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 transition-all duration-300 hover:scale-105 hover:shadow-glow disabled:cursor-not-allowed disabled:opacity-70"
        >
          Choose PDF
        </button>

        {(activeDocument || selectedFileName) && (
          <p className="mt-4 max-w-full truncate text-xs text-blue-200">
            Active: {activeDocument || selectedFileName}
          </p>
        )}
      </div>
    </motion.div>
  );
}

export default UploadBox;

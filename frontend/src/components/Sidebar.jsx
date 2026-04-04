import { motion } from "framer-motion";
import { FileText, ShieldCheck } from "lucide-react";
import UploadBox from "./UploadBox";

function Sidebar({ uploadedFiles, selectedFileName, activeDocument, isUploading, onUpload }) {
  return (
    <motion.aside
      initial={{ opacity: 0, x: -24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="hidden w-[380px] border-r border-line bg-black/40 p-6 backdrop-blur-xl lg:flex lg:flex-col"
    >
      <div className="rounded-[32px] border border-line bg-panel p-6 shadow-2xl">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-glow">
            <ShieldCheck size={24} className="text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold tracking-tight">Custom ChatGPT</h2>
            <p className="text-sm text-slate-400">Private PDF RAG workspace</p>
          </div>
        </div>

        <UploadBox
          onUpload={onUpload}
          isUploading={isUploading}
          selectedFileName={selectedFileName}
          activeDocument={activeDocument}
        />
      </div>

      <div className="mt-6 flex-1 overflow-hidden rounded-[32px] border border-line bg-panel p-6 backdrop-blur-xl">
        <p className="text-sm uppercase tracking-[0.25em] text-slate-500">
          Uploaded PDFs
        </p>

        <div className="custom-scrollbar mt-5 space-y-3 overflow-y-auto pr-1">
          {uploadedFiles.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-slate-700/60 p-6 text-sm leading-6 text-slate-500">
              No files uploaded yet. Drop a PDF above and start asking grounded questions.
            </div>
          ) : (
            uploadedFiles.map((file, index) => (
              <motion.div
                key={`${file.name}-${index}`}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -4, scale: 1.01 }}
                className="rounded-3xl border border-line bg-white/5 p-4 transition-all duration-300 hover:border-blue-500/30 hover:bg-white/10 hover:shadow-card-hover"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-300">
                    <FileText size={20} />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-white">{file.name}</p>
                    <p className="text-xs text-slate-400">{file.chunks} chunks indexed</p>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </motion.aside>
  );
}

export default Sidebar;

import { useState } from "react";
import { motion } from "framer-motion";
import { SendHorizontal } from "lucide-react";

function InputBox({ onSend, disabled }) {
  const [value, setValue] = useState("");

  const submitMessage = () => {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  };

  return (
    <div className="border-t border-line bg-black/30 px-4 py-5 backdrop-blur-xl md:px-8">
      <div className="mx-auto flex max-w-5xl items-end gap-4 rounded-[30px] border border-line bg-white/5 p-3 backdrop-blur-xl">
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              submitMessage();
            }
          }}
          placeholder="Ask a question from your uploaded PDF..."
          rows={1}
          className="max-h-36 min-h-[56px] flex-1 resize-none bg-transparent px-4 py-4 text-sm text-white outline-none placeholder:text-slate-500 md:text-base"
        />

        <motion.button
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          onClick={submitMessage}
          disabled={disabled || !value.trim()}
          className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 text-white shadow-glow transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <SendHorizontal size={22} />
        </motion.button>
      </div>
    </div>
  );
}

export default InputBox;

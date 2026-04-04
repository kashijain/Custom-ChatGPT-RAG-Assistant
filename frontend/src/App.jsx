import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import InputBox from "./components/InputBox";
import UploadBox from "./components/UploadBox";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const toFriendlyBackendMessage = (message, fallbackMessage) => {
  const value = String(message || "").toLowerCase();

  if (value.includes("insufficient_quota") || value.includes("429") || value.includes("rate limit")) {
    return "OpenAI quota is unavailable, so the app is running in demo mode.";
  }

  if (value.includes("openai_api_key") || value.includes("api key")) {
    return "OpenAI API key is missing, so the app is running in demo mode.";
  }

  return message || fallbackMessage;
};

const parseApiError = async (response, fallbackMessage) => {
  try {
    const data = await response.json();
    return toFriendlyBackendMessage(data.detail, fallbackMessage);
  } catch {
    return fallbackMessage;
  }
};

const toNetworkErrorMessage = (error) => {
  if (error instanceof TypeError && error.message === "Failed to fetch") {
    return "Unable to reach the backend at http://127.0.0.1:8000. Please confirm FastAPI is running and CORS allows the Vite frontend origin.";
  }

  return toFriendlyBackendMessage(
    error.message,
    "Something went wrong while contacting the backend."
  );
};

const welcomeMessage = {
  role: "assistant",
  content:
    "Upload a PDF and ask me anything from that document. I'll answer with grounded context and show source snippets below each response.",
  sources: []
};

function App() {
  const [messages, setMessages] = useState([welcomeMessage]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [activeDocument, setActiveDocument] = useState("");
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);

  const handleUpload = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setIsUploading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(await parseApiError(response, "Failed to upload PDF."));
      }

      const data = await response.json();
      const uploadedDocument = data.active_document || data.filename || file.name;
      setIsDemoMode(Boolean(data.demo_mode));

      setUploadedFiles((current) => [
        {
          name: uploadedDocument,
          chunks: data.chunks_count || data.chunks_indexed || 0
        },
        ...current
      ]);
      setSelectedFileName(uploadedDocument);
      setActiveDocument(uploadedDocument);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.message ? `${data.message}. Ask a question when you're ready.` : `Your PDF "${uploadedDocument}" is indexed and ready. Ask a question when you're ready.`,
          sources: []
        }
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: `Upload failed: ${toNetworkErrorMessage(error)}`,
          sources: []
        }
      ]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (question) => {
    if (!question.trim() || isThinking) return;

    const userMessage = { role: "user", content: question, sources: [] };
    setMessages((current) => [...current, userMessage]);
    setIsThinking(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          active_document: activeDocument || selectedFileName || null
        })
      });

      if (!response.ok) {
        throw new Error(await parseApiError(response, "Failed to get AI response."));
      }

      const data = await response.json();
      setIsDemoMode(Boolean(data.demo_mode));

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || []
        }
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: `Chat error: ${toNetworkErrorMessage(error)}`,
          sources: []
        }
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink text-white">
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.18),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(239,68,68,0.12),transparent_28%),linear-gradient(180deg,#020617,#020617_45%,#030712)]" />
      <div className="fixed inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%2394a3b8%22 fill-opacity=%220.08%22%3E%3Ccircle cx=%2230%22 cy=%2230%22 r=%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]" />

      <div className="relative flex h-screen overflow-hidden">
        <Sidebar
          uploadedFiles={uploadedFiles}
          selectedFileName={selectedFileName}
          activeDocument={activeDocument}
          isUploading={isUploading}
          onUpload={handleUpload}
        />

        <main className="flex min-w-0 flex-1 flex-col">
          <motion.header
            initial={{ opacity: 0, y: -18 }}
            animate={{ opacity: 1, y: 0 }}
            className="border-b border-line bg-black/30 px-6 py-5 backdrop-blur-xl"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate-500">
                  RAG Assistant
                </p>
                <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white">
                  Custom ChatGPT
                </h1>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-sm text-blue-200">
                  <Sparkles size={16} />
                  Context-aware answers
                </div>

                {isDemoMode && (
                  <div className="rounded-full border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-200">
                    Demo mode active
                  </div>
                )}
              </div>
            </div>
          </motion.header>

          <div className="border-b border-line bg-black/20 p-4 backdrop-blur-xl lg:hidden">
            <UploadBox
              onUpload={handleUpload}
              isUploading={isUploading}
              selectedFileName={selectedFileName}
              activeDocument={activeDocument}
            />
          </div>

          <ChatWindow
            messages={messages}
            isThinking={isThinking}
            hasUploadedFiles={uploadedFiles.length > 0}
            activeDocument={activeDocument || selectedFileName}
          />

          <InputBox onSend={handleSendMessage} disabled={isThinking} />
        </main>
      </div>
    </div>
  );
}

export default App;



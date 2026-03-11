"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileSpreadsheet, AlertCircle, Loader2, Mail } from "lucide-react";

interface UploadFormProps {
  onSubmit: (file: File, email: string) => void;
  isLoading: boolean;
  error?: string;
}

const ACCEPTED_TYPES: Record<string, string[]> = {
  "text/csv": [".csv"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "application/vnd.ms-excel": [".xls"],
};

const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

export function UploadForm({ onSubmit, isLoading, error }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[], rejected: any[]) => {
    setValidationError(null);
    if (rejected.length > 0) {
      const err = rejected[0]?.errors?.[0];
      if (err?.code === "file-too-large") {
        setValidationError("File exceeds 10 MB limit.");
      } else if (err?.code === "file-invalid-type") {
        setValidationError("Only .csv, .xlsx, and .xls files are accepted.");
      } else {
        setValidationError("Invalid file.");
      }
      return;
    }
    if (accepted.length > 0) {
      setFile(accepted[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_SIZE,
    maxFiles: 1,
    disabled: isLoading,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!file) {
      setValidationError("Please select a file to upload.");
      return;
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email.trim())) {
      setValidationError("Please enter a valid email address.");
      return;
    }

    onSubmit(file, email.trim());
  };

  const displayError = validationError || error;

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6 sm:p-8 space-y-6"
    >
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
          ${isDragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-blue-400 hover:bg-slate-50"}
          ${isLoading ? "opacity-50 pointer-events-none" : ""}
        `}
      >
        <input {...getInputProps()} />

        {file ? (
          <div className="flex flex-col items-center gap-2">
            <FileSpreadsheet className="h-10 w-10 text-green-600" />
            <p className="text-sm font-medium text-slate-800">{file.name}</p>
            <p className="text-xs text-slate-500">
              {(file.size / 1024).toFixed(1)} KB ·{" "}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
                className="text-blue-600 hover:underline"
              >
                Change file
              </button>
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-10 w-10 text-slate-400" />
            <p className="text-sm text-slate-600">
              {isDragActive
                ? "Drop your file here..."
                : "Drag & drop your sales data file, or click to browse"}
            </p>
            <p className="text-xs text-slate-400">CSV, XLSX, XLS · Max 10 MB</p>
          </div>
        )}
      </div>

      {/* Email input */}
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-slate-700 mb-1.5"
        >
          Recipient Email
        </label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            id="email"
            type="email"
            placeholder="sales-team@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            className="w-full rounded-lg border border-slate-300 pl-10 pr-4 py-2.5 text-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
      </div>

      {/* Error banner */}
      {displayError && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <p>{displayError}</p>
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600
          text-white font-semibold py-3 px-4 text-sm
          hover:from-blue-700 hover:to-indigo-700
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          disabled:opacity-60 disabled:cursor-not-allowed
          transition-all"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing & Generating Summary...
          </>
        ) : (
          <>
            <Zap className="h-4 w-4" />
            Generate Executive Summary
          </>
        )}
      </button>

      {isLoading && (
        <p className="text-xs text-center text-slate-500">
          This may take 15–30 seconds depending on the file size.
        </p>
      )}
    </form>
  );
}

function Zap(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z" />
    </svg>
  );
}

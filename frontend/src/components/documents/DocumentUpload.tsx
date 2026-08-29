"use client";

import { useState, useRef } from "react";

interface DocumentUploadProps {
  onUploadComplete?: (document: any) => void;
  onUploadsComplete?: (results: any) => void;
  multiple?: boolean;
  accept?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? `http://${window.location.hostname}:8000` 
    : 'http://localhost:8000');

export default function DocumentUpload({ 
  onUploadComplete, 
  onUploadsComplete,
  multiple = false,
  accept = ".pdf,.doc,.docx,.jpg,.jpeg,.png,.tiff,.txt,.zip"
}: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [processingStatus, setProcessingStatus] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFiles(files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
  };

  const handleFiles = async (files: FileList) => {
    setIsUploading(true);
    setError(null);
    setUploadedFiles([]);
    setProcessingStatus("");

    // Check for ZIP files
    const fileArray = Array.from(files);
    const zipFiles = fileArray.filter(f => f.name.toLowerCase().endsWith('.zip'));
    const regularFiles = fileArray.filter(f => !f.name.toLowerCase().endsWith('.zip'));

    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setError("Please sign in to upload documents");
        setIsUploading(false);
        return;
      }

      // If multiple files or ZIP, use the multi-upload endpoint
      if (multiple || zipFiles.length > 0 || regularFiles.length > 1) {
        const formData = new FormData();
        fileArray.forEach(file => {
          formData.append("files", file);
        });

        setProcessingStatus(`Uploading ${fileArray.length} files...`);

        const response = await fetch(`${API_URL}/api/v1/documents/upload-multiple`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          setUploadedFiles(result.results || []);
          setProcessingStatus(`Upload complete: ${result.successful} files`);
          if (onUploadsComplete) onUploadsComplete(result);
          if (onUploadComplete && result.results && result.results.length > 0) {
            onUploadComplete(result.results[0]);
          }
        } else {
          const error = await response.json();
          setError(error.detail || "Upload failed");
        }
      } else {
        // Single file upload
        const file = files[0];
        const formData = new FormData();
        formData.append("file", file);

        setProcessingStatus(`Uploading ${file.name}...`);

        const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          setUploadedFiles([result]);
          setProcessingStatus("Upload complete");
          if (onUploadComplete) onUploadComplete(result);
        } else {
          const error = await response.json();
          setError(error.detail || "Upload failed");
        }
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return '📄';
    if (['doc', 'docx'].includes(ext || '')) return '📝';
    if (['jpg', 'jpeg', 'png', 'tiff'].includes(ext || '')) return '🖼️';
    if (ext === 'zip') return '📦';
    return '📎';
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            </div>
            <p className="text-sm text-gray-600">{processingStatus || "Uploading..."}</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        ) : uploadedFiles.length > 0 ? (
          <div className="space-y-3">
            <div className="text-4xl">✅</div>
            <p className="font-medium text-gray-900">{uploadedFiles.length} files uploaded</p>
            <div className="max-h-40 overflow-y-auto">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="flex items-center gap-2 text-sm text-gray-600 py-1 border-b border-gray-100">
                  <span>{getFileIcon(file.filename || file.original_filename)}</span>
                  <span className="truncate">{file.filename || file.original_filename}</span>
                  <span className="text-xs text-green-600 ml-auto">✓</span>
                </div>
              ))}
            </div>
            <button
              onClick={() => {
                setUploadedFiles([]);
                setProgress(0);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Upload more files
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-5xl">📄</div>
            <p className="text-gray-600">Drag and drop your files here, or</p>
            <button
              onClick={triggerFileInput}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Browse Files
            </button>
            <p className="text-xs text-gray-500">
              Supported: PDF, DOC, DOCX, JPG, PNG, TIFF, TXT, ZIP
            </p>
            <p className="text-xs text-gray-400">
              {multiple ? "Multiple files allowed" : "Single file upload"}
            </p>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileSelect}
        className="hidden"
      />

      {error && (
        <div className="mt-3 rounded-md bg-red-50 p-3">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
    </div>
  );
}

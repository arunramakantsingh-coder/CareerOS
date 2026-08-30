"use client";

import { useState, useRef } from "react";

interface DocumentUploadProps {
  onUploadComplete?: (document: any) => void;
  category?: string;
  subcategory?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DocumentUpload({ onUploadComplete, category, subcategory }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<any>(null);
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
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setProgress(0);

    // Validate file type
    const validTypes = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
    if (!validTypes.includes(file.type)) {
      setError("Please upload a PDF, DOC, DOCX, or TXT file");
      setIsUploading(false);
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("File size exceeds 5MB limit");
      setIsUploading(false);
      return;
    }

    try {
      // Get token
      const token = localStorage.getItem("access_token");
      if (!token) {
        setError("Please sign in to upload documents");
        setIsUploading(false);
        return;
      }

      // Create form data
      const formData = new FormData();
      formData.append("file", file);
      if (category) formData.append("document_category", category);
      if (subcategory) formData.append("document_subcategory", subcategory);

      // Upload with progress tracking
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_URL}/api/v1/documents/upload`, true);
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setProgress(Math.round(percentComplete));
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200 || xhr.status === 201) {
          const response = JSON.parse(xhr.responseText);
          setUploadedFile(response);
          setProgress(100);
          if (onUploadComplete) onUploadComplete(response);
        } else {
          const error = JSON.parse(xhr.responseText);
          setError(error.detail || "Upload failed");
        }
        setIsUploading(false);
      };

      xhr.onerror = () => {
        setError("Network error. Please try again.");
        setIsUploading(false);
      };

      xhr.send(formData);
    } catch (err) {
      setError("Upload failed. Please try again.");
      setIsUploading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
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
            <p className="text-sm text-gray-600">Uploading...</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500">{progress}%</p>
          </div>
        ) : uploadedFile ? (
          <div className="space-y-3">
            <div className="text-4xl">✅</div>
            <p className="font-medium text-gray-900">{uploadedFile.original_filename}</p>
            <p className="text-sm text-gray-500">
              {(uploadedFile.file_size / 1024).toFixed(1)} KB • {uploadedFile.document_category || "CV"}
            </p>
            <p className="text-sm text-green-600">Upload complete!</p>
            <button
              onClick={() => {
                setUploadedFile(null);
                setProgress(0);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Upload another file
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-5xl">📄</div>
            <p className="text-gray-600">Drag and drop your file here, or</p>
            <button
              onClick={triggerFileInput}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Browse Files
            </button>
            <p className="text-xs text-gray-500">Supported formats: PDF, DOC, DOCX, TXT (max 5MB)</p>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.txt"
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

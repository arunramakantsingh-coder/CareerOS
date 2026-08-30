"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import DocumentUpload from "@/components/documents/DocumentUpload";
import DocumentBulkUpload from "@/components/documents/DocumentBulkUpload";
import { apiClient } from "@/lib/api/client";

interface Document {
  id: string;
  original_filename: string;
  filename?: string;
  file_size: number;
  document_category: string;
  document_subcategory: string | null;
  status: string;
  extraction_status: string;
  classification_confidence?: number;
  created_at: string;
}

export default function DocumentsPage() {
  const { token, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.push("/login");
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && token) fetchDocuments();
  }, [isAuthenticated, token]);

  const fetchDocuments = async () => {
    try {
      setDocuments(await apiClient.get<Document[]>("/api/v1/documents/"));
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch documents");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = (document: Document) => {
    setDocuments((current) => [document, ...current]);
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await apiClient.delete(`/api/v1/documents/${docId}`);
      setDocuments((current) => current.filter((d) => d.id !== docId));
    } catch (err) {
      alert("Failed to delete document");
    }
  };

  const handleExtract = async (docId: string) => {
    try {
      await apiClient.post("/api/v1/extraction/extract", { document_id: docId });
      alert("Extraction started successfully!");
      fetchDocuments();
    } catch (err) {
      alert("Failed to start extraction");
    }
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      cv: "CV / Resume",
      employment: "Employment Evidence",
      certification: "Certification",
      education: "Education",
      project: "Project",
      achievement: "Achievement",
      identity: "Identity",
      other: "Other",
    };
    return labels[category] || category;
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      uploaded: "bg-yellow-100 text-yellow-800",
      processed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      duplicate: "bg-purple-100 text-purple-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getExtractionBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      in_progress: "bg-blue-100 text-blue-800",
      complete: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const categories = [
    { value: "all", label: "All Documents" },
    { value: "cv", label: "CV / Resume" },
    { value: "employment", label: "Employment" },
    { value: "certification", label: "Certifications" },
    { value: "education", label: "Education" },
    { value: "project", label: "Projects" },
    { value: "achievement", label: "Achievements" },
    { value: "identity", label: "Identity" },
    { value: "other", label: "Other" },
  ];

  const filteredDocuments = selectedCategory === "all"
    ? documents
    : documents.filter((d) => d.document_category === selectedCategory);

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8 gap-3">
          <div><h1 className="text-2xl font-bold text-gray-900">Professional Document Vault</h1><p className="text-gray-600">Store and manage your career documents</p></div>
          <div className="flex gap-2"><Link href="/profile/intelligence" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">Career Intelligence →</Link><a href="/profile" className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50">← Back to Profile</a></div>
        </div>

        {error && <div className="rounded-md bg-red-50 p-4 mb-6"><p className="text-sm text-red-800">{error}</p></div>}

        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Bulk Professional Intake</h2>
          <DocumentBulkUpload onComplete={() => fetchDocuments()} />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Single Document Upload</h2>
          <DocumentUpload onUploadComplete={handleUploadComplete} />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-6 gap-3">
            <h2 className="text-lg font-semibold text-gray-900">Your Documents</h2>
            <div className="flex items-center gap-2"><select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm">{categories.map((cat) => <option key={cat.value} value={cat.value}>{cat.label}</option>)}</select><span className="text-sm text-gray-500">{documents.length} files</span></div>
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-12"><div className="text-6xl mb-4">📂</div><p className="text-gray-600">No documents uploaded yet</p><p className="text-sm text-gray-500">Upload your CV or other career documents to get started</p></div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredDocuments.map((doc) => (
                <div key={doc.id} className="py-4 flex items-center justify-between hover:bg-gray-50 px-4 rounded-lg transition-colors gap-3">
                  <div className="flex items-center gap-4 min-w-0"><div className="text-2xl flex-shrink-0">{doc.document_category === "cv" ? "📄" : doc.document_category === "employment" ? "💼" : doc.document_category === "certification" ? "🏆" : doc.document_category === "education" ? "🎓" : "📎"}</div><div className="min-w-0 flex-1"><p className="font-medium text-gray-900 truncate">{doc.filename || doc.original_filename}</p><div className="flex flex-wrap items-center gap-2 text-xs text-gray-500"><span>{getCategoryLabel(doc.document_category)}</span><span>•</span><span>{(doc.file_size / 1024).toFixed(1)} KB</span><span className={`px-2 py-0.5 rounded-full ${getStatusBadge(doc.status)}`}>{doc.status}</span><span className={`px-2 py-0.5 rounded-full ${getExtractionBadge(doc.extraction_status)}`}>{doc.extraction_status}</span>{doc.classification_confidence != null && <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">{Math.round(doc.classification_confidence * 100)}% classified</span>}</div></div></div>
                  <div className="flex items-center gap-2 flex-shrink-0">{doc.extraction_status === "pending" && <button onClick={() => handleExtract(doc.id)} className="text-sm text-blue-600 hover:text-blue-800">Extract</button>}<button onClick={() => handleDelete(doc.id)} className="text-sm text-red-600 hover:text-red-800">Delete</button></div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-lg p-6"><h3 className="text-sm font-medium text-gray-900 mb-4">Document Vault Summary</h3><div className="grid grid-cols-2 md:grid-cols-4 gap-4"><div className="text-center p-3 bg-gray-50 rounded-lg"><p className="text-2xl font-bold text-gray-900">{documents.length}</p><p className="text-xs text-gray-500">Total Documents</p></div><div className="text-center p-3 bg-green-50 rounded-lg"><p className="text-2xl font-bold text-green-600">{documents.filter((d) => d.extraction_status === "complete").length}</p><p className="text-xs text-gray-500">Extracted</p></div><div className="text-center p-3 bg-yellow-50 rounded-lg"><p className="text-2xl font-bold text-yellow-600">{documents.filter((d) => d.extraction_status === "pending").length}</p><p className="text-xs text-gray-500">Pending Extraction</p></div><div className="text-center p-3 bg-blue-50 rounded-lg"><p className="text-2xl font-bold text-blue-600">{documents.filter((d) => d.document_category === "cv").length}</p><p className="text-xs text-gray-500">CVs Uploaded</p></div></div></div>
      </div>
    </div>
  );
}

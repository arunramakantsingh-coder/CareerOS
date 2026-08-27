"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Experience {
  id: string;
  company: string;
  title: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  responsibilities: string[];
  achievements: string[];
  industry: string;
}

export default function ExperiencesPage() {
  const { user, token, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    company: "",
    title: "",
    location: "",
    start_date: "",
    end_date: "",
    is_current: false,
    responsibilities: "",
    achievements: "",
    industry: "",
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchExperiences();
    }
  }, [isAuthenticated, token]);

  const fetchExperiences = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/profile/experiences`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setExperiences(data);
      }
    } catch (err) {
      setError("Failed to fetch experiences");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const payload = {
      ...formData,
      responsibilities: formData.responsibilities.split("\n").filter(Boolean),
      achievements: formData.achievements.split("\n").filter(Boolean),
    };

    try {
      const url = editingId
        ? `${API_URL}/api/v1/profile/experiences/${editingId}`
        : `${API_URL}/api/v1/profile/experiences`;
      
      const response = await fetch(url, {
        method: editingId ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        await fetchExperiences();
        setShowForm(false);
        setEditingId(null);
        resetForm();
      } else {
        const error = await response.json();
        setError(error.detail || "Failed to save experience");
      }
    } catch (err) {
      setError("Network error");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this experience?")) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/profile/experiences/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchExperiences();
      }
    } catch (err) {
      setError("Failed to delete experience");
    }
  };

  const handleEdit = (exp: Experience) => {
    setFormData({
      company: exp.company,
      title: exp.title,
      location: exp.location || "",
      start_date: exp.start_date ? exp.start_date.split("T")[0] : "",
      end_date: exp.end_date ? exp.end_date.split("T")[0] : "",
      is_current: exp.is_current,
      responsibilities: exp.responsibilities?.join("\n") || "",
      achievements: exp.achievements?.join("\n") || "",
      industry: exp.industry || "",
    });
    setEditingId(exp.id);
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      company: "",
      title: "",
      location: "",
      start_date: "",
      end_date: "",
      is_current: false,
      responsibilities: "",
      achievements: "",
      industry: "",
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const value = e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
    });
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Professional Experience</h1>
            <p className="text-gray-600">Manage your work history</p>
          </div>
          <div className="flex gap-3">
            <a
              href="/profile"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
            >
              ← Back to Profile
            </a>
            <button
              onClick={() => {
                resetForm();
                setEditingId(null);
                setShowForm(true);
              }}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              + Add Experience
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editingId ? "Edit Experience" : "Add Experience"}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Company *</label>
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Title *</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Industry</label>
                  <input
                    type="text"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">End Date</label>
                  <input
                    type="date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleChange}
                    disabled={formData.is_current}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_current"
                    checked={formData.is_current}
                    onChange={handleChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-700">Current Position</label>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">Responsibilities (one per line)</label>
                <textarea
                  name="responsibilities"
                  rows={3}
                  value={formData.responsibilities}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Designed network architecture&#10;Led security transformation"
                />
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">Achievements (one per line)</label>
                <textarea
                  name="achievements"
                  rows={2}
                  value={formData.achievements}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Reduced downtime by 40%&#10;Achieved 99.99% uptime"
                />
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  type="submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingId(null);
                    resetForm();
                  }}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Experience List */}
        <div className="bg-white rounded-lg shadow-lg divide-y divide-gray-200">
          {experiences.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">No experience added yet</p>
              <p className="text-sm text-gray-500">Click "Add Experience" to get started</p>
            </div>
          ) : (
            experiences.map((exp) => (
              <div key={exp.id} className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{exp.title}</h3>
                    <p className="text-gray-700">{exp.company}</p>
                    <p className="text-sm text-gray-500">
                      {exp.location && `${exp.location} • `}
                      {exp.start_date ? new Date(exp.start_date).toLocaleDateString() : ""}
                      {exp.is_current ? " - Present" : exp.end_date ? ` - ${new Date(exp.end_date).toLocaleDateString()}` : ""}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(exp)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(exp.id)}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                {exp.responsibilities && exp.responsibilities.length > 0 && (
                  <ul className="mt-2 list-disc list-inside text-sm text-gray-600">
                    {exp.responsibilities.slice(0, 3).map((resp, idx) => (
                      <li key={idx}>{resp}</li>
                    ))}
                    {exp.responsibilities.length > 3 && (
                      <li className="text-gray-400">+{exp.responsibilities.length - 3} more...</li>
                    )}
                  </ul>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

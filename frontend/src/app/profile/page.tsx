"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Profile {
  id: string;
  full_name: string;
  location: string;
  title: string;
  summary: string;
  linkedin_url: string;
  linkedin_username: string;
  primary_email: string;
  primary_phone: string;
  work_preferences: any;
  years_experience: number;
  industries: string[];
  seniority: string;
  completeness_score: number;
  completeness_breakdown: any;
  reconciliation_status: string;
}

interface CompletenessData {
  overall_score: number;
  breakdown: Record<string, number>;
  missing_items: string[];
  suggestions: string[];
}

export default function ProfilePage() {
  const { user, token, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [completeness, setCompleteness] = useState<CompletenessData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    full_name: "",
    location: "",
    title: "",
    summary: "",
    linkedin_url: "",
    primary_email: "",
    primary_phone: "",
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchProfile();
      fetchCompleteness();
    }
  }, [isAuthenticated, token]);

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/profile/`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData({
          full_name: data.full_name || "",
          location: data.location || "",
          title: data.title || "",
          summary: data.summary || "",
          linkedin_url: data.linkedin_url || "",
          primary_email: data.primary_email || user?.email || "",
          primary_phone: data.primary_phone || "",
        });
      } else if (response.status === 404) {
        // Create profile
        await createProfile();
      }
    } catch (err) {
      setError("Failed to fetch profile");
    } finally {
      setLoading(false);
    }
  };

  const fetchCompleteness = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/profile/completeness`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCompleteness(data);
      }
    } catch (err) {
      console.error("Failed to fetch completeness:", err);
    }
  };

  const createProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/profile/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: user?.id,
          full_name: user?.name || "",
          primary_email: user?.email || "",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData({
          full_name: data.full_name || "",
          location: data.location || "",
          title: data.title || "",
          summary: data.summary || "",
          linkedin_url: data.linkedin_url || "",
          primary_email: data.primary_email || user?.email || "",
          primary_phone: data.primary_phone || "",
        });
      }
    } catch (err) {
      setError("Failed to create profile");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/profile/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setSuccess("Profile updated successfully!");
        setIsEditing(false);
        fetchCompleteness();
      } else {
        const error = await response.json();
        setError(error.detail || "Failed to update profile");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

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

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>
            <p className="text-gray-600">Manage your professional profile</p>
          </div>
          <div className="flex items-center gap-3">
            {!isEditing && profile && (
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Edit Profile
              </button>
            )}
            <a
              href="/documents"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
            >
              Documents →
            </a>
          </div>
        </div>

        {/* Completeness Score */}
        {completeness && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-medium text-gray-900">Profile Completeness</h2>
                <p className="text-2xl font-bold text-blue-600">{completeness.overall_score}%</p>
              </div>
              <div className="flex-1 mx-6">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-500 ${
                      completeness.overall_score >= 80 ? "bg-green-500" :
                      completeness.overall_score >= 50 ? "bg-yellow-500" :
                      "bg-red-500"
                    }`}
                    style={{ width: `${completeness.overall_score}%` }}
                  ></div>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {completeness.missing_items.length > 0
                  ? `${completeness.missing_items.length} items needed`
                  : "Complete!"}
              </div>
            </div>

            {/* Breakdown */}
            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(completeness.breakdown).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-xs text-gray-600">{key}</span>
                  <span className={`text-xs font-medium ${
                    value >= 80 ? "text-green-600" :
                    value >= 50 ? "text-yellow-600" :
                    "text-red-600"
                  }`}>
                    {value}%
                  </span>
                </div>
              ))}
            </div>

            {/* Suggestions */}
            {completeness.suggestions.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-xs text-blue-800 font-medium">Suggestions:</p>
                <ul className="mt-1 text-xs text-blue-700 list-disc list-inside">
                  {completeness.suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Profile Form */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {error && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-4 rounded-md bg-green-50 p-4">
              <p className="text-sm text-green-800">{success}</p>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                  }`}
                  required
                />
              </div>

              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Professional Title
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                  }`}
                  placeholder="e.g., Senior Network Architect"
                />
              </div>

              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                  Location
                </label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                  }`}
                  placeholder="e.g., New York, NY"
                />
              </div>

              <div>
                <label htmlFor="primary_email" className="block text-sm font-medium text-gray-700">
                  Primary Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="primary_email"
                  name="primary_email"
                  value={formData.primary_email}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                  }`}
                  required
                />
              </div>

              <div>
                <label htmlFor="primary_phone" className="block text-sm font-medium text-gray-700">
                  Primary Phone
                </label>
                <input
                  type="tel"
                  id="primary_phone"
                  name="primary_phone"
                  value={formData.primary_phone}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                  }`}
                  placeholder="e.g., +1 555-123-4567"
                />
              </div>

              <div>
                <label htmlFor="linkedin_url" className="block text-sm font-medium text-gray-700">
                  LinkedIn URL
                </label>
                <input
                  type="url"
                  id="linkedin_url"
                  name="linkedin_url"
                  value={formData.linkedin_url}
                  onChange={handleChange}
                  disabled={!isEditing}
                  className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                  }`}
                  placeholder="https://linkedin.com/in/yourprofile"
                />
              </div>
            </div>

            <div className="mt-6">
              <label htmlFor="summary" className="block text-sm font-medium text-gray-700">
                Professional Summary
              </label>
              <textarea
                id="summary"
                name="summary"
                rows={4}
                value={formData.summary}
                onChange={handleChange}
                disabled={!isEditing}
                className={`mt-1 block w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                  !isEditing ? "bg-gray-50 border-gray-200" : "border-gray-300"
                }`}
                placeholder="Tell us about your professional background..."
              />
            </div>

            {isEditing && (
              <div className="mt-6 flex items-center gap-3">
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setError(null);
                    setSuccess(null);
                    // Reset form to profile data
                    if (profile) {
                      setFormData({
                        full_name: profile.full_name || "",
                        location: profile.location || "",
                        title: profile.title || "",
                        summary: profile.summary || "",
                        linkedin_url: profile.linkedin_url || "",
                        primary_email: profile.primary_email || user?.email || "",
                        primary_phone: profile.primary_phone || "",
                      });
                    }
                  }}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/documents"
            className="bg-white rounded-lg shadow-lg p-4 text-center hover:shadow-xl transition-shadow"
          >
            <div className="text-3xl mb-2">📄</div>
            <h3 className="font-medium text-gray-900">Upload Documents</h3>
            <p className="text-xs text-gray-500">Add CV, certificates, and more</p>
          </a>
          <a
            href="/profile/experiences"
            className="bg-white rounded-lg shadow-lg p-4 text-center hover:shadow-xl transition-shadow"
          >
            <div className="text-3xl mb-2">💼</div>
            <h3 className="font-medium text-gray-900">Add Experience</h3>
            <p className="text-xs text-gray-500">Add your work history</p>
          </a>
          <a
            href="/profile/skills"
            className="bg-white rounded-lg shadow-lg p-4 text-center hover:shadow-xl transition-shadow"
          >
            <div className="text-3xl mb-2">🛠️</div>
            <h3 className="font-medium text-gray-900">Add Skills</h3>
            <p className="text-xs text-gray-500">Add your technical skills</p>
          </a>
        </div>
      </div>
    </div>
  );
}

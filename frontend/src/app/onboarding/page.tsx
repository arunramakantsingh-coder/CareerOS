"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function OnboardingPage() {
  const { user, token, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchProfile();
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
      } else if (response.status === 404) {
        // Profile doesn't exist yet
        setProfile(null);
      }
    } catch (error) {
      console.error("Failed to fetch profile:", error);
    } finally {
      setProfileLoading(false);
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
      }
    } catch (error) {
      console.error("Failed to create profile:", error);
    }
  };

  if (isLoading || profileLoading) {
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome to CareerOS, {user?.name || "Professional"}! 👋
          </h1>
          <p className="mt-2 text-gray-600">
            Let's get your career profile set up. We'll start by understanding your professional background.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          {profile ? (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Your Profile</h2>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {profile.completeness_score || 0}% Complete
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-md">
                  <p className="text-xs text-gray-500">Full Name</p>
                  <p className="font-medium">{profile.full_name || "Not set"}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-md">
                  <p className="text-xs text-gray-500">Email</p>
                  <p className="font-medium">{profile.primary_email || user?.email}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-md">
                  <p className="text-xs text-gray-500">Title</p>
                  <p className="font-medium">{profile.title || "Not set"}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-md">
                  <p className="text-xs text-gray-500">Location</p>
                  <p className="font-medium">{profile.location || "Not set"}</p>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <a
                  href="/profile"
                  className="flex-1 text-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Complete Your Profile
                </a>
                <a
                  href="/documents"
                  className="flex-1 text-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Upload Documents
                </a>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              <h3 className="text-lg font-medium text-gray-900">Create Your Profile</h3>
              <p className="mt-2 text-sm text-gray-600">
                Start by creating your professional profile. You can upload your CV or fill in your details manually.
              </p>
              <button
                onClick={createProfile}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Create Profile
              </button>
            </div>
          )}
        </div>

        <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Start</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg text-center hover:border-blue-400 transition-colors">
              <div className="text-3xl mb-2">📄</div>
              <h3 className="font-medium text-gray-900">Upload CV</h3>
              <p className="text-xs text-gray-500 mt-1">Extract your profile from your CV</p>
              <a href="/documents" className="mt-2 inline-block text-sm text-blue-600 hover:underline">
                Upload now →
              </a>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg text-center hover:border-blue-400 transition-colors">
              <div className="text-3xl mb-2">📝</div>
              <h3 className="font-medium text-gray-900">Fill Profile</h3>
              <p className="text-xs text-gray-500 mt-1">Add your professional details</p>
              <a href="/profile" className="mt-2 inline-block text-sm text-blue-600 hover:underline">
                Edit profile →
              </a>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg text-center hover:border-blue-400 transition-colors">
              <div className="text-3xl mb-2">🔍</div>
              <h3 className="font-medium text-gray-900">Find Jobs</h3>
              <p className="text-xs text-gray-500 mt-1">Discover opportunities that match you</p>
              <a href="/jobs" className="mt-2 inline-block text-sm text-blue-600 hover:underline">
                Search jobs →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

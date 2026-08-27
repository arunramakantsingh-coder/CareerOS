"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Skill {
  id: string;
  name: string;
  category: string;
  proficiency: string;
  years_experience: number;
}

export default function SkillsPage() {
  const { user, token, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newSkill, setNewSkill] = useState({
    name: "",
    category: "Technical",
    proficiency: "Intermediate",
    years_experience: "",
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && token) {
      fetchSkills();
    }
  }, [isAuthenticated, token]);

  const fetchSkills = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/profile/skills`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSkills(data);
      }
    } catch (err) {
      setError("Failed to fetch skills");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/profile/skills`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...newSkill,
          years_experience: parseFloat(newSkill.years_experience) || 0,
        }),
      });

      if (response.ok) {
        await fetchSkills();
        setNewSkill({
          name: "",
          category: "Technical",
          proficiency: "Intermediate",
          years_experience: "",
        });
      } else {
        const error = await response.json();
        setError(error.detail || "Failed to add skill");
      }
    } catch (err) {
      setError("Network error");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this skill?")) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/profile/skills/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchSkills();
      }
    } catch (err) {
      setError("Failed to delete skill");
    }
  };

  const categories = ["Technical", "Soft", "Leadership", "Domain"];
  const proficiencyLevels = ["Beginner", "Intermediate", "Advanced", "Expert"];

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
            <h1 className="text-2xl font-bold text-gray-900">Skills</h1>
            <p className="text-gray-600">Manage your technical and professional skills</p>
          </div>
          <a
            href="/profile"
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
          >
            ← Back to Profile
          </a>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Add Skill Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Add Skill</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Skill Name *</label>
              <input
                type="text"
                value={newSkill.name}
                onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                required
                placeholder="e.g., Kubernetes"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Category</label>
              <select
                value={newSkill.category}
                onChange={(e) => setNewSkill({ ...newSkill, category: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Proficiency</label>
              <select
                value={newSkill.proficiency}
                onChange={(e) => setNewSkill({ ...newSkill, proficiency: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {proficiencyLevels.map((level) => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Years Experience</label>
              <input
                type="number"
                value={newSkill.years_experience}
                onChange={(e) => setNewSkill({ ...newSkill, years_experience: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., 5"
                min="0"
                step="0.5"
              />
            </div>
            <div className="md:col-span-4">
              <button
                type="submit"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Add Skill
              </button>
            </div>
          </form>
        </div>

        {/* Skills List */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Your Skills</h2>
            <span className="text-sm text-gray-500">{skills.length} skills</span>
          </div>

          {skills.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">No skills added yet</p>
              <p className="text-sm text-gray-500">Add your skills above to get started</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {skills.map((skill) => (
                <div
                  key={skill.id}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div>
                    <span className="font-medium text-gray-900">{skill.name}</span>
                    <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500 mt-1">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full">
                        {skill.category}
                      </span>
                      <span>{skill.proficiency}</span>
                      {skill.years_experience > 0 && (
                        <span>{skill.years_experience} years</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(skill.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

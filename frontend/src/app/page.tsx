'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { HealthStatus } from '@/types';

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await apiClient.healthCheck();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError('Failed to connect to backend');
        console.error('Health check error:', err);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-2 bg-blue-100 rounded-lg mb-4">
            <span className="text-2xl font-bold text-blue-600">CareerOS</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
            AI-Powered Global Career
            <br />
            <span className="text-blue-600">Operating System</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Intelligent career intelligence platform for global opportunities
          </p>
        </div>

        {/* Status Card */}
        <div className="max-w-md mx-auto bg-white rounded-xl shadow-lg overflow-hidden md:max-w-2xl border border-gray-200">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">System Status</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                health?.status === 'healthy' 
                  ? 'bg-green-100 text-green-800' 
                  : health?.status === 'degraded'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {health?.status || 'Unknown'}
              </span>
            </div>
            
            {loading && (
              <div className="space-y-3">
                <div className="animate-pulse flex space-x-4">
                  <div className="flex-1 space-y-4 py-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{error}</p>
                <p className="text-xs text-red-600 mt-1">
                  Make sure the backend is running on port 8000
                </p>
              </div>
            )}

            {health && !error && (
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                  <span className="text-sm text-gray-500">Database</span>
                  <span className={`text-sm font-medium ${
                    health.database === 'healthy' 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {health.database || 'Unknown'}
                  </span>
                </div>
                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                  <span className="text-sm text-gray-500">API Version</span>
                  <span className="text-sm font-medium text-gray-900">
                    {health.version || 'Unknown'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Environment</span>
                  <span className="text-sm font-medium text-gray-900">
                    Development
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto">
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div className="text-blue-600 text-2xl mb-3">📊</div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">Career Vault</h3>
            <p className="mt-2 text-sm text-gray-500">
              Centralized career data and evidence management
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div className="text-blue-600 text-2xl mb-3">🎯</div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">Personas</h3>
            <p className="mt-2 text-sm text-gray-500">
              Multi-career profile management
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div className="text-blue-600 text-2xl mb-3">🔍</div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">Job Discovery</h3>
            <p className="mt-2 text-sm text-gray-500">
              Semantic job search and matching
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-400 border-t border-gray-200 pt-8">
          <p>CareerOS v0.1.0 — Foundation Phase</p>
          <p className="mt-1">Built with Next.js, FastAPI, PostgreSQL + pgvector</p>
        </div>
      </div>
    </div>
  );
}

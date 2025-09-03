/**
 * Dashboard Page
 * 
 * Protected dashboard page that shows user information and logout functionality.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/components/auth/AuthProvider';
import { BentoGrid } from '@/components/dashboard/bento-grid';
import { api } from '@/lib/api';
import { CloudArrowUpIcon, FolderOpenIcon, QuestionMarkCircleIcon } from "@heroicons/react/24/outline";
import type { Project } from '../../../../shared/api-contract';

function DashboardContent() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.projects.getProjects();
        
        if (response.success && response.data) {
          setProjects(response.data.items);
        } else {
          setError(response.error || 'Failed to fetch projects');
        }
      } catch (err) {
        setError('Failed to fetch projects');
        console.error('Project fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchProjects();
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
  };

  const getProjectStats = () => {
    const total = projects.length;
    const ready = projects.filter(p => p.status === 'ready').length;
    const processing = projects.filter(p => p.status === 'processing').length;
    return { total, ready, processing };
  };

  const { total, ready, processing } = getProjectStats();

  const fetchProjects = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.projects.getProjects();
      
      if (response.success && response.data) {
        setProjects(response.data.items);
      } else {
        setError(response.error || 'Failed to fetch projects');
      }
    } catch (err) {
      setError('Failed to fetch projects');
      console.error('Project fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col gap-8">
        {/* Welcome Header */}
        <div className="flex flex-col items-center gap-2 mb-2">
          <h1 className="text-3xl md:text-4xl font-bold text-indigo-700 dark:text-indigo-400 tracking-tight">Welcome back, {user?.name || 'User'}!</h1>
          <p className="text-base md:text-lg text-gray-700 dark:text-gray-200">Your SmartQuery dashboard</p>
        </div>
        {/* User Info Card */}
        <div className="w-full bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col gap-4">
          <h3 className="text-lg font-semibold text-indigo-700 dark:text-indigo-200 mb-2">User Information</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Name</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Email</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">User ID</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.id}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Member Since</dt>
              <dd className="mt-1 text-base text-gray-900 dark:text-gray-100">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</dd>
            </div>
          </div>
        </div>
        {/* Stats Cards */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col items-center">
            <div className="w-12 h-12 bg-indigo-200 dark:bg-indigo-700 rounded-full flex items-center justify-center mb-2">
              <FolderOpenIcon className="w-7 h-7 text-indigo-700 dark:text-indigo-200" />
            </div>
            <div className="text-lg font-semibold text-indigo-700 dark:text-indigo-200">Total Projects</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">{isLoading ? '...' : total}</div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col items-center">
            <div className="w-12 h-12 bg-green-200 dark:bg-green-700 rounded-full flex items-center justify-center mb-2">
              <CloudArrowUpIcon className="w-7 h-7 text-green-700 dark:text-green-200" />
            </div>
            <div className="text-lg font-semibold text-green-700 dark:text-green-200">Ready Projects</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">{isLoading ? '...' : ready}</div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-2xl shadow-xl p-6 flex flex-col items-center">
            <div className="w-12 h-12 bg-yellow-200 dark:bg-yellow-700 rounded-full flex items-center justify-center mb-2">
              <QuestionMarkCircleIcon className="w-7 h-7 text-yellow-700 dark:text-yellow-200" />
            </div>
            <div className="text-lg font-semibold text-yellow-700 dark:text-yellow-200">Processing</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">{isLoading ? '...' : processing}</div>
          </div>
        </div>
        {/* Error Display */}
        {error && (
          <div className="w-full bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Projects Grid */}
        <div className="w-full">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Your Projects</h3>
          <BentoGrid 
            projects={projects}
            isLoading={isLoading}
            onProjectsUpdate={fetchProjects}
            onProjectClick={(projectId) => router.push(`/workspace/${projectId}`)}
          />
        </div>

        {/* Sign Out Button */}
        <div className="flex justify-center mt-4">
          <button
            onClick={handleLogout}
            className="py-2 px-6 rounded-xl bg-red-500 text-white font-semibold text-base hover:bg-red-600 transition-colors shadow"
          >
            Sign Out
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
} 
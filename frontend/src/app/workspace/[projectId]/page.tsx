"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { api } from '@/lib/api';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import type { Project } from '../../../../../shared/api-contract';

interface WorkspaceContentProps {
  projectId: string;
}

function WorkspaceContent({ projectId }: WorkspaceContentProps) {
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await api.projects.getProject(projectId);
        
        if (response.success && response.data) {
          setProject(response.data);
        } else {
          setError(response.error || 'Failed to load project');
        }
      } catch (err) {
        setError('Failed to load project');
        console.error('Project fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (projectId) {
      fetchProject();
    }
  }, [projectId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Project not found'}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                <ArrowLeftIcon className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {project.name}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {project.row_count} rows, {project.column_count} columns
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${
                project.status === 'ready' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : project.status === 'processing'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {project.status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
          {/* Left Panel - Chat */}
          <div className="bg-white dark:bg-gray-950 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Chat</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Ask questions about your data</p>
            </div>
            <div className="flex-1 p-4">
              <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
                Chat interface coming soon...
              </div>
            </div>
          </div>

          {/* Right Panel - Data */}
          <div className="bg-white dark:bg-gray-950 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Data Preview</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">CSV data and query results</p>
            </div>
            <div className="flex-1 p-4">
              <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
                Data preview coming soon...
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function WorkspacePage({ params }: { params: { projectId: string } }) {
  return (
    <ProtectedRoute>
      <WorkspaceContent projectId={params.projectId} />
    </ProtectedRoute>
  );
}
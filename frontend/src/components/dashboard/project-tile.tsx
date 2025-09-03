"use client";

import React from 'react';
import { FolderOpenIcon, TrashIcon } from '@heroicons/react/24/outline';
import type { Project } from '../../../../shared/api-contract';

interface ProjectTileProps {
  project: Project;
  onClick: () => void;
  onDelete?: (projectId: string) => void;
}

export function ProjectTile({ project, onClick, onDelete }: ProjectTileProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && confirm(`Are you sure you want to delete "${project.name}"?`)) {
      onDelete(project.id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900';
      case 'processing':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900';
      case 'uploading':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900';
      case 'error':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900';
    }
  };

  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-950 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 cursor-pointer border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 group"
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center">
              <FolderOpenIcon className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg leading-tight">
                {project.name}
              </h3>
              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium capitalize mt-1 ${getStatusColor(project.status)}`}>
                {project.status}
              </span>
            </div>
          </div>
          {onDelete && (
            <button
              onClick={handleDelete}
              className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all duration-200"
            >
              <TrashIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        {project.description && (
          <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">
            {project.description}
          </p>
        )}

        <div className="space-y-2 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex justify-between">
            <span>Rows:</span>
            <span className="font-medium">{project.row_count?.toLocaleString() || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span>Columns:</span>
            <span className="font-medium">{project.column_count || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span>Created:</span>
            <span className="font-medium">{new Date(project.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        {project.status === 'ready' && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium">
              Ready for analysis →
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
"use client";

import React, { useState } from 'react';
import { ProjectTile } from './project-tile';
import { NewProjectTile } from './new-project-tile';
import { NewProjectModal } from './new-project-modal';
import { api } from '@/lib/api';
import type { Project } from '../../../../shared/api-contract';

interface BentoGridProps {
  projects: Project[];
  isLoading: boolean;
  onProjectsUpdate: () => void;
  onProjectClick: (projectId: string) => void;
}

export function BentoGrid({ projects, isLoading, onProjectsUpdate, onProjectClick }: BentoGridProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  const handleDeleteProject = async (projectId: string) => {
    try {
      setIsDeleting(projectId);
      const response = await api.projects.deleteProject(projectId);
      
      if (response.success) {
        onProjectsUpdate();
      } else {
        console.error('Delete failed:', response.error);
      }
    } catch (error) {
      console.error('Delete error:', error);
    } finally {
      setIsDeleting(null);
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-950 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 h-48 animate-pulse"
          >
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24" />
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                </div>
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full" />
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 auto-rows-max">
        <NewProjectTile onClick={() => setIsModalOpen(true)} />
        
        {projects.map((project) => (
          <ProjectTile
            key={project.id}
            project={project}
            onClick={() => onProjectClick(project.id)}
            onDelete={isDeleting === project.id ? undefined : handleDeleteProject}
          />
        ))}
      </div>

      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onProjectCreated={onProjectsUpdate}
      />
    </>
  );
}
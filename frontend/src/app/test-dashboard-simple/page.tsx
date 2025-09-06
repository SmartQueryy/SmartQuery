'use client';

import React from 'react';
import { useProjects } from '@/lib/store/project';

export default function TestDashboardSimplePage() {
  const { projects, isLoading, error } = useProjects();

  console.log('Render TestDashboardSimplePage', { projects: projects.length, isLoading, error });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Simple Test Dashboard</h1>
      <div>
        <p>Projects: {projects.length}</p>
        <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
        <p>Error: {error || 'None'}</p>
      </div>
    </div>
  );
}
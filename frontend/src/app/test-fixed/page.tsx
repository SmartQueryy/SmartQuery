'use client';

import React, { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useProjectsData, useProjectsActions } from '@/lib/store/project-fixed';

export default function TestFixedPage() {
  const { projects, isLoading, error, total } = useProjectsData();
  const { fetchProjects, clearError } = useProjectsActions();

  // Use effect with no dependencies that could cause loops
  useEffect(() => {
    console.log('TestFixedPage mounted, fetching projects...');
    fetchProjects();
  }, []); // Empty dependency array - run only once on mount

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Test Fixed Store Page</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Store State</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p>Total Projects: {total}</p>
            <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-red-700">{error}</p>
                <Button 
                  onClick={clearError} 
                  size="sm" 
                  variant="outline"
                  className="mt-2"
                >
                  Clear Error
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Projects ({projects.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading projects...</p>
          ) : projects.length === 0 ? (
            <p className="text-gray-500">No projects found</p>
          ) : (
            <div className="space-y-2">
              {projects.map((project) => (
                <div key={project.id} className="p-3 border rounded">
                  <h3 className="font-semibold">{project.name}</h3>
                  <p className="text-sm text-gray-600">{project.description}</p>
                  <p className="text-xs text-gray-500">Status: {project.status}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mt-6 flex gap-2">
        <Button onClick={() => fetchProjects()}>
          Refresh Projects
        </Button>
      </div>
    </div>
  );
}
'use client';

import React from 'react';
import { useProjects, useProjectActions, useUploadStatus } from '@/lib/store/project';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function ProjectStoreDemo() {
  const { projects, isLoading, error, total } = useProjects();
  const { createProject, deleteProject, fetchProjects, clearError } = useProjectActions();
  const { uploadStatus, isUploading } = useUploadStatus();

  React.useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async () => {
    const result = await createProject({
      name: `Test Project ${Date.now()}`,
      description: 'A demo project created from the store test',
    });
    
    if (result) {
      console.log('Project created:', result);
    }
  };

  const handleDeleteProject = async (id: string) => {
    const success = await deleteProject(id);
    if (success) {
      console.log('Project deleted successfully');
    }
  };

  return (
    <div className="space-y-4 p-4">
      <Card>
        <CardHeader>
          <CardTitle>Project Store Demo</CardTitle>
          <CardDescription>
            Testing the Zustand project store integration with API client
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded">
              {error}
              <Button onClick={clearError} size="sm" variant="outline" className="ml-2">
                Clear
              </Button>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Button onClick={() => fetchProjects()} disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Refresh Projects'}
            </Button>
            <Button onClick={handleCreateProject} variant="outline">
              Create Test Project
            </Button>
            <span className="text-sm text-gray-500">
              Total projects: {total}
            </span>
          </div>

          {isUploading && (
            <div className="bg-blue-50 border border-blue-200 text-blue-700 p-3 rounded">
              Uploading file...
            </div>
          )}

          {uploadStatus && (
            <div className="bg-gray-50 border border-gray-200 p-3 rounded">
              <div className="font-semibold">Upload Status</div>
              <div className="text-sm">Status: {uploadStatus.status}</div>
              <div className="text-sm">Message: {uploadStatus.message}</div>
              {uploadStatus.progress !== undefined && (
                <div className="text-sm">Progress: {uploadStatus.progress}%</div>
              )}
            </div>
          )}

          <div className="space-y-2">
            <h3 className="font-semibold">Projects ({projects.length})</h3>
            {projects.map((project) => (
              <div
                key={project.id}
                className="flex items-center justify-between p-3 border rounded"
              >
                <div>
                  <div className="font-medium">{project.name}</div>
                  <div className="text-sm text-gray-500">{project.description}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={project.status === 'ready' ? 'default' : 'secondary'}>
                    {project.status}
                  </Badge>
                  <Button
                    onClick={() => handleDeleteProject(project.id)}
                    size="sm"
                    variant="destructive"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
            {projects.length === 0 && !isLoading && (
              <div className="text-gray-500 text-center py-8">
                No projects found. Create one to get started!
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
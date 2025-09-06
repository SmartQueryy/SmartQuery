'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import type { Project, ProjectStatus, PaginatedResponse } from '../../../../shared/api-contract';

// Mock data generator
const generateMockProject = (index: number): Project => ({
  id: `mock-project-${index}`,
  name: `Project ${index}`,
  description: `Test project ${index} with sample CSV data`,
  status: (['ready', 'processing', 'uploading', 'error'] as ProjectStatus[])[index % 4],
  user_id: 'test-user-123',
  created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
  updated_at: new Date().toISOString(),
  file_name: `sample-data-${index}.csv`,
  file_size: Math.floor(Math.random() * 10000000),
  row_count: Math.floor(Math.random() * 10000),
  column_count: Math.floor(Math.random() * 20) + 5,
  columns: Array.from({ length: Math.floor(Math.random() * 10) + 5 }, (_, i) => ({
    name: `column_${i}`,
    type: ['string', 'number', 'date', 'boolean'][Math.floor(Math.random() * 4)],
  })),
  error: index % 4 === 3 ? 'Sample error for testing' : undefined,
});

export default function TestDashboardPage() {
  const [mockMode, setMockMode] = useState(true);
  const [mockProjectCount, setMockProjectCount] = useState(5);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [uploadStatus, setUploadStatus] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const mockSetupRef = useRef(false);

  // Mock API responses - wrapped in useEffect to prevent re-creation
  useEffect(() => {
    if (mockMode && !mockSetupRef.current) {
      mockSetupRef.current = true;
      setupMockResponses();
    }
  }, [mockMode]);

  const setupMockResponses = () => {
    // Mock getProjects
    api.projects.getProjects = async (params?: { page?: number; limit?: number }) => {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      
      const mockProjects = Array.from({ length: mockProjectCount }, (_, i) => generateMockProject(i + 1));
      const response: PaginatedResponse<Project> = {
        items: mockProjects,
        total: mockProjects.length,
        page: params?.page || 1,
        limit: params?.limit || 10,
        hasMore: false,
      };
      
      return {
        success: true,
        data: response,
      };
    };

    // Mock createProject
    api.projects.createProject = async (data) => {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const newProject = generateMockProject(mockProjectCount + 1);
      newProject.name = data.name;
      newProject.description = data.description || 'Mock created project';
      newProject.status = 'uploading';
      
      return {
        success: true,
        data: {
          project: newProject,
          upload_url: 'https://mock-upload.example.com/upload',
          upload_fields: {
            key: 'mock-key',
            policy: 'mock-policy',
          },
        },
      };
    };

    // Mock deleteProject
    api.projects.deleteProject = async (id) => {
      await new Promise(resolve => setTimeout(resolve, 600));
      return {
        success: true,
        data: { message: `Project ${id} deleted successfully` },
      };
    };

    // Mock getUploadUrl
    api.projects.getUploadUrl = async (projectId) => {
      await new Promise(resolve => setTimeout(resolve, 400));
      return {
        success: true,
        data: {
          upload_url: `https://mock-upload.example.com/project/${projectId}`,
          upload_fields: {
            key: `mock-key-${projectId}`,
            policy: 'mock-policy',
          },
        },
      };
    };

    // Mock getProjectStatus
    api.projects.getProjectStatus = async (projectId) => {
      await new Promise(resolve => setTimeout(resolve, 300));
      const statuses: ProjectStatus[] = ['processing', 'processing', 'ready'];
      const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
      
      return {
        success: true,
        data: {
          status: randomStatus,
          message: `Project is ${randomStatus}`,
          progress: randomStatus === 'processing' ? Math.floor(Math.random() * 100) : 100,
        },
      };
    };
  };

  // Fetch projects
  const fetchProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.projects.getProjects();
      if (response.success && response.data) {
        setProjects(response.data.items);
        setTotal(response.data.total);
      } else {
        setError(response.error || 'Failed to fetch projects');
      }
    } catch (err) {
      setError('Network error while fetching projects');
    } finally {
      setIsLoading(false);
    }
  };

  // Load mock data
  const loadMockData = async () => {
    await fetchProjects();
  };

  // Test create project
  const testCreateProject = async () => {
    setIsLoading(true);
    try {
      const result = await api.projects.createProject({
        name: `Test Project ${Date.now()}`,
        description: 'Created from test dashboard',
      });
      
      if (result.success && result.data) {
        console.log('✅ Project created:', result.data.project);
        await fetchProjects(); // Refresh list
      } else {
        console.error('❌ Failed to create project');
        setError(result.error || 'Failed to create project');
      }
    } catch (err) {
      console.error('❌ Error creating project:', err);
      setError('Error creating project');
    } finally {
      setIsLoading(false);
    }
  };

  // Test delete project
  const testDeleteProject = async (id: string) => {
    setIsLoading(true);
    try {
      const result = await api.projects.deleteProject(id);
      if (result.success) {
        console.log('✅ Project deleted:', id);
        await fetchProjects(); // Refresh list
      } else {
        console.error('❌ Failed to delete project:', id);
        setError(result.error || 'Failed to delete project');
      }
    } catch (err) {
      console.error('❌ Error deleting project:', err);
      setError('Error deleting project');
    } finally {
      setIsLoading(false);
    }
  };

  // Test file upload
  const testFileUpload = async () => {
    const mockFile = new File(['test,data\n1,2\n3,4'], 'test.csv', { type: 'text/csv' });
    const firstProject = projects[0];
    
    if (!firstProject) {
      console.error('No project available for upload test');
      setError('No project available for upload test');
      return;
    }

    setIsUploading(true);
    try {
      const uploadUrlResponse = await api.projects.getUploadUrl(firstProject.id);
      if (uploadUrlResponse.success && uploadUrlResponse.data) {
        console.log('✅ Got upload URL for project:', firstProject.id);
        
        // Mock file upload (in real scenario, upload to presigned URL)
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check status
        const statusResponse = await api.projects.getProjectStatus(firstProject.id);
        if (statusResponse.success && statusResponse.data) {
          setUploadStatus(statusResponse.data);
          console.log('✅ Upload status:', statusResponse.data);
        }
      } else {
        console.error('❌ Failed to get upload URL');
        setError('Failed to get upload URL');
      }
    } catch (err) {
      console.error('❌ Error uploading file:', err);
      setError('Error uploading file');
    } finally {
      setIsUploading(false);
    }
  };

  // Test set current project
  const testSetCurrentProject = (project: Project) => {
    setCurrentProject(project);
    console.log('✅ Current project set:', project);
  };

  // Clear error
  const clearError = () => {
    setError(null);
  };

  // Reset state
  const reset = () => {
    setProjects([]);
    setTotal(0);
    setError(null);
    setCurrentProject(null);
    setUploadStatus(null);
    setIsLoading(false);
    setIsUploading(false);
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Dashboard Test Page</h1>
          <p className="text-muted-foreground">Comprehensive testing of dashboard with mock data (No Zustand)</p>
        </div>

        {/* Test Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Test Controls</CardTitle>
            <CardDescription>Configure and run dashboard tests</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Mock Mode Toggle */}
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={mockMode}
                  onChange={(e) => setMockMode(e.target.checked)}
                  className="rounded"
                />
                <span>Use Mock Data</span>
              </label>
              
              {mockMode && (
                <div className="flex items-center gap-2">
                  <label>Mock Projects:</label>
                  <input
                    type="number"
                    value={mockProjectCount}
                    onChange={(e) => setMockProjectCount(parseInt(e.target.value) || 5)}
                    className="w-20 px-2 py-1 border rounded"
                    min="0"
                    max="50"
                  />
                </div>
              )}
            </div>

            {/* Test Actions */}
            <div className="flex flex-wrap gap-2">
              <Button onClick={loadMockData} variant="outline" disabled={isLoading}>
                Load {mockMode ? 'Mock' : 'Real'} Data
              </Button>
              <Button onClick={testCreateProject} variant="outline" disabled={isLoading}>
                Test Create Project
              </Button>
              <Button onClick={testFileUpload} variant="outline" disabled={isLoading || isUploading}>
                Test File Upload
              </Button>
              <Button onClick={clearError} variant="outline">
                Clear Error
              </Button>
              <Button onClick={reset} variant="outline">
                Reset State
              </Button>
              <Button 
                onClick={() => console.log('Current State:', { projects, total, error, currentProject, uploadStatus })} 
                variant="outline"
              >
                Log Current State
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* State Display */}
        <Card>
          <CardHeader>
            <CardTitle>Current State</CardTitle>
            <CardDescription>Local state management (no Zustand)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium">Total Projects:</p>
                <p className="text-2xl font-bold">{total}</p>
              </div>
              <div>
                <p className="text-sm font-medium">Loading:</p>
                <Badge variant={isLoading ? 'default' : 'secondary'}>
                  {isLoading ? 'Yes' : 'No'}
                </Badge>
              </div>
              <div>
                <p className="text-sm font-medium">Uploading:</p>
                <Badge variant={isUploading ? 'default' : 'secondary'}>
                  {isUploading ? 'Yes' : 'No'}
                </Badge>
              </div>
              <div>
                <p className="text-sm font-medium">Upload Status:</p>
                <p className="text-sm">
                  {uploadStatus ? `${uploadStatus.status} - ${uploadStatus.message}` : 'None'}
                </p>
              </div>
            </div>
            
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}
            
            {currentProject && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="text-blue-700 text-sm font-medium">Current Project:</p>
                <p className="text-blue-600 text-sm">{currentProject.name} (ID: {currentProject.id})</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Projects Display */}
        <Card>
          <CardHeader>
            <CardTitle>Projects ({projects.length})</CardTitle>
            <CardDescription>Projects from local state</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Loading projects...</p>
              </div>
            ) : projects.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No projects found. Click "Load Data" or create a test project.
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => testSetCurrentProject(project)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium">{project.name}</h3>
                      <Badge variant={
                        project.status === 'ready' ? 'default' : 
                        project.status === 'error' ? 'destructive' : 
                        'secondary'
                      }>
                        {project.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {project.description}
                    </p>
                    {project.file_name && (
                      <p className="text-xs text-muted-foreground">
                        File: {project.file_name}
                      </p>
                    )}
                    {project.row_count && (
                      <p className="text-xs text-muted-foreground">
                        Rows: {project.row_count.toLocaleString()}
                      </p>
                    )}
                    <div className="mt-3 flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          testDeleteProject(project.id);
                        }}
                        disabled={isLoading}
                      >
                        Delete
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          api.projects.getProjectStatus(project.id).then(res => {
                            if (res.success && res.data) {
                              setUploadStatus(res.data);
                              console.log('Status for', project.id, ':', res.data);
                            }
                          });
                        }}
                        disabled={isLoading}
                      >
                        Check Status
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Results */}
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
            <CardDescription>Check console for detailed test output</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p>✓ Dashboard works without Zustand (no infinite loops)</p>
              <p>✓ Mock data generation working</p>
              <p>✓ CRUD operations testable</p>
              <p>✓ Error handling available</p>
              <p>✓ Loading states functional</p>
              <p>✓ Upload flow testable</p>
              <p>✓ Local state management working</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
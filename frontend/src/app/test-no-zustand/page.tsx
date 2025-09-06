'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import type { Project } from '../../../../shared/api-contract';

export default function TestNoZustandPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

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

  useEffect(() => {
    console.log('TestNoZustandPage mounted');
    fetchProjects();
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Test Without Zustand</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>State (No Zustand)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p>Total Projects: {total}</p>
            <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-red-700">{error}</p>
                <Button 
                  onClick={() => setError(null)} 
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

      <div className="mt-6">
        <Button onClick={fetchProjects} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Refresh Projects'}
        </Button>
      </div>
    </div>
  );
}
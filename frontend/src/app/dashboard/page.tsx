/**
 * Dashboard Page
 * 
 * Protected dashboard page with modern shadcn/ui components and professional design.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/components/auth/AuthProvider';
import { BentoGrid } from '@/components/dashboard/bento-grid';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { FolderIcon, CheckCircleIcon, ClockIcon, AlertCircleIcon, LogOutIcon } from 'lucide-react';
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
    <div className="min-h-screen bg-background">
      <div className="border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold">SmartQuery</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">Welcome back, {user?.name || 'User'}</span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOutIcon className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* User Info Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Account Information</CardTitle>
              <CardDescription>
                Your SmartQuery account details and membership information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-muted-foreground">Name</dt>
                  <dd className="text-sm">{user?.name}</dd>
                </div>
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-muted-foreground">Email</dt>
                  <dd className="text-sm">{user?.email}</dd>
                </div>
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-muted-foreground">User ID</dt>
                  <dd className="text-sm font-mono">{user?.id}</dd>
                </div>
                <div className="space-y-1">
                  <dt className="text-sm font-medium text-muted-foreground">Member Since</dt>
                  <dd className="text-sm">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>
          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <FolderIcon className="h-4 w-4 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Total Projects</p>
                    <p className="text-2xl font-bold">{isLoading ? '...' : total}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                    <CheckCircleIcon className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Ready Projects</p>
                    <p className="text-2xl font-bold">{isLoading ? '...' : ready}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                    <ClockIcon className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">Processing</p>
                    <p className="text-2xl font-bold">{isLoading ? '...' : processing}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          {/* Error Display */}
          {error && (
            <Card className="border-destructive">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <AlertCircleIcon className="h-4 w-4 text-destructive" />
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Projects Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Your Projects</h2>
                <p className="text-muted-foreground">Manage and query your CSV datasets</p>
              </div>
            </div>
            <BentoGrid 
              projects={projects}
              isLoading={isLoading}
              onProjectsUpdate={fetchProjects}
              onProjectClick={(projectId) => router.push(`/workspace/${projectId}`)}
            />
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
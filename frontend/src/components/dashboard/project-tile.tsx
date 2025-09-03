"use client";

import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FolderIcon, Trash2 } from 'lucide-react';
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

  const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
    switch (status) {
      case 'ready':
        return 'default';
      case 'processing':
        return 'secondary';
      case 'uploading':
        return 'secondary';
      case 'error':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  return (
    <Card 
      onClick={onClick}
      className="cursor-pointer hover:shadow-md transition-shadow group h-40"
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
              <FolderIcon className="h-4 w-4 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-medium text-sm leading-tight truncate">
                {project.name}
              </h3>
              <Badge 
                variant={getStatusVariant(project.status)} 
                className="text-xs capitalize mt-1"
              >
                {project.status}
              </Badge>
            </div>
          </div>
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-1">
        <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
          <div className="flex justify-between">
            <span>Rows:</span>
            <span className="font-medium">{project.row_count?.toLocaleString() || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span>Columns:</span>
            <span className="font-medium">{project.column_count || 'N/A'}</span>
          </div>
        </div>
        
        <div className="text-xs text-muted-foreground pt-1">
          <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
        </div>

        {project.status === 'ready' && (
          <div className="pt-2 text-xs text-primary font-medium">
            Ready for analysis →
          </div>
        )}
      </CardContent>
    </Card>
  );
}
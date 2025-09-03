"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Plus } from 'lucide-react';

interface NewProjectTileProps {
  onClick: () => void;
}

export function NewProjectTile({ onClick }: NewProjectTileProps) {
  return (
    <Card 
      onClick={onClick}
      className="cursor-pointer border-2 border-dashed border-muted-foreground/25 hover:border-primary/50 transition-colors group h-40 flex items-center justify-center"
    >
      <CardContent className="p-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto group-hover:bg-primary/20 transition-colors">
            <Plus className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="font-medium text-sm mb-1">
              New Project
            </h3>
            <p className="text-xs text-muted-foreground">
              Upload a CSV file to get started
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
"use client";

import React, { useState } from 'react';
import { useProjectActions, useUploadStatus } from '@/lib/store/project';
import { XMarkIcon, CloudArrowUpIcon, DocumentIcon } from '@heroicons/react/24/outline';
import type { CreateProjectRequest } from '../../../../shared/api-contract';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProjectCreated: () => void;
}

export function NewProjectModal({ isOpen, onClose, onProjectCreated }: NewProjectModalProps) {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const { createProject, uploadFile, checkUploadStatus } = useProjectActions();
  const { uploadStatus } = useUploadStatus();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        setError('File size must be less than 100MB');
        return;
      }
      setCsvFile(file);
      setError(null);
    }
  };

  // uploadFileToUrl functionality is now handled by the project store

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      setError('Project name is required');
      return;
    }

    if (!csvFile) {
      setError('Please select a CSV file');
      return;
    }

    try {
      setIsCreating(true);
      setError(null);
      setUploadProgress(0);

      // Step 1: Create project
      const projectData: CreateProjectRequest = {
        name: projectName.trim(),
        description: description.trim() || undefined,
      };

      const project = await createProject(projectData);

      if (!project) {
        setError('Failed to create project');
        return;
      }

      setUploadProgress(25);

      // Step 2: Upload file using project store
      const uploadSuccess = await uploadFile(project.id, csvFile);
      
      if (!uploadSuccess) {
        setError('Failed to upload file');
        return;
      }
      
      setUploadProgress(75);

      // Step 3: Wait for processing to complete
      let attempts = 0;
      const maxAttempts = 30; // 30 seconds max wait
      
      while (attempts < maxAttempts) {
        await checkUploadStatus(project.id);
        
        if (uploadStatus?.status === 'ready') {
          setUploadProgress(100);
          onProjectCreated();
          handleClose();
          return;
        } else if (uploadStatus?.status === 'error') {
          setError(uploadStatus.error || 'File processing failed');
          return;
        }
        
        // Still processing, wait and check again
        setUploadProgress(75 + (attempts / maxAttempts) * 20);
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }

      setError('File processing timed out. Please check the project status later.');
    } catch (err) {
      setError('Failed to create project and upload file');
      console.error('Project creation error:', err);
    } finally {
      setIsCreating(false);
      setUploadProgress(0);
    }
  };

  const handleClose = () => {
    setProjectName('');
    setDescription('');
    setCsvFile(null);
    setUploadProgress(0);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Create New Project</h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-700 dark:text-red-200 text-sm">{error}</p>
            </div>
          )}

          <div className="mb-4">
            <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Project Name *
            </label>
            <input
              type="text"
              id="projectName"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              placeholder="Enter project name"
              required
              disabled={isCreating}
            />
          </div>

          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description (optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              placeholder="Describe your project (optional)"
              disabled={isCreating}
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              CSV File *
            </label>
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors">
              {csvFile ? (
                <div className="flex items-center justify-center gap-3">
                  <DocumentIcon className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{csvFile.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {(csvFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCsvFile(null)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                    disabled={isCreating}
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <div>
                  <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <label htmlFor="csvFile" className="cursor-pointer">
                    <span className="text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-500 dark:hover:text-indigo-300">
                      Click to upload
                    </span>
                    <span className="text-gray-500 dark:text-gray-400"> or drag and drop</span>
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">CSV files up to 100MB</p>
                  <input
                    type="file"
                    id="csvFile"
                    accept=".csv,text/csv"
                    onChange={handleFileChange}
                    className="hidden"
                    disabled={isCreating}
                  />
                </div>
              )}
            </div>
          </div>

          {isCreating && uploadProgress > 0 && (
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-700 dark:text-gray-300">Upload Progress</span>
                <span className="text-gray-700 dark:text-gray-300">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              disabled={isCreating}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating || !projectName.trim() || !csvFile}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isCreating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {uploadProgress < 25 ? 'Creating...' : uploadProgress < 75 ? 'Uploading...' : 'Processing...'}
                </>
              ) : (
                <>
                  <CloudArrowUpIcon className="w-4 h-4" />
                  Create & Upload
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
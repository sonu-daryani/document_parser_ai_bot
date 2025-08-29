
import React, { useState, useEffect } from "react";

interface File {
  file_id?: string;
  filename?: string;
  name?: string;
  size?: number;
  type?: string;
  upload_time?: string;
  chunk_count?: number;
  file_path?: string;
  [key: string]: any;
}

// Mock toast functions for demonstration
const toast = {
  success: (message: string) => console.log("Success:", message),
  error: (message: string) => console.log("Error:", message)
};


import { api } from '../../app/lib/api';

export default function FileUpload({setIsUploading}: {setIsUploading?: React.Dispatch<React.SetStateAction<boolean>>}) {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const [isUploadingLocal, setIsUploadingLocal] = useState(false);

    // Always use a function for uploadingSetter
    const uploadingSetter = typeof setIsUploading === 'function' ? setIsUploading : (val: boolean) => setIsUploadingLocal(val);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files) {
          for (let i = 0; i < files.length; i++) {
            setSelectedFiles((oldArray) => [...oldArray, files[i]]);
          }
        }
    };

    // user_id comes from cookie; backend reads it. Keep local for display only if needed
    const [userId, setUserId] = useState<string | null>(null);
    // Fetch uploaded files from backend
    useEffect(() => {
      api.get(`/api/auth/ensure`).then((r) => setUserId(r.data?.user_id)).catch(() => {});
      api.get(`/api/documents`)
        .then(res => {
          setUploadedFiles(res.data.documents || []);
        })
        .catch(() => setUploadedFiles([]));
    }, []);

    const handleDelete = async (file_id: string) => {
      uploadingSetter(true);
      try {
        await api.delete(`/api/documents/${file_id}`);
        setUploadedFiles((old) => old.filter((file) => file.file_id !== file_id));
        uploadingSetter(false);
        toast.success('File deleted successfully');
      } catch(error) {
        console.error(error);
        uploadingSetter(false);
        toast.error('Error deleting file');
      }
    }

    const handleUpload = async (e: React.FormEvent) => {
      e.preventDefault();
      uploadingSetter(true);
      const formData = new FormData();
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i] as any);
      }
      // user_id is taken from cookie on the server side
      try {
        const response = await api.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        if (response.data.user_id) setUserId(response.data.user_id);
        setUploadedFiles((old) => [...old, ...response.data.files]);
        uploadingSetter(false);
        toast.success('Files uploaded successfully');
      } catch (error) {
        console.error('Error uploading files:', error);
        uploadingSetter(false);
        toast.error('Error uploading files');
      }
    };

    // Cloud Upload Icon Component
    const CloudUploadIcon = () => (
      <svg className="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    );

    // Close Icon Component
    const CloseIcon = () => (
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
      </svg>
    );

    // PDF Icon Component
    const PDFIcon = () => (
      <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
      </svg>
    );

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-lg p-8">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="w-60 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-2xl font-bold">PDF GPT</span>
            </div>
          </div>

          {/* Toast Container Placeholder */}
          <div className="fixed top-4 right-4 z-50">
            {/* Toast notifications would appear here */}
          </div>

          {/* File Upload Container */}
          <div className="space-y-6">
            <label className="group relative flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-xl cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <div className="text-gray-400 group-hover:text-gray-600 transition-colors duration-200">
                  <CloudUploadIcon />
                </div>
                <p className="mb-2 text-sm text-gray-500 group-hover:text-gray-700">
                  <span className="font-semibold">Click to upload file</span>
                </p>
                <p className="text-xs text-gray-500">PDF files only</p>
              </div>
              <input 
                accept=".pdf" 
                onChange={handleFileChange} 
                multiple 
                type="file" 
                id="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
            </label>
            { selectedFiles.length > 0 && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Selected Files</h3>
                <ul className="space-y-2">
                  {selectedFiles.map((file, index) => (
                    <li key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                      <div className="flex items-center space-x-3"> 
                        <PDFIcon />
                        <div>
                          <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {file.name || file.filename}
                          </p>
                          <p className="text-xs text-gray-500">
                            {file.size ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : ''}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedFiles((old) => old.filter((_, i) => i !== index))}
                        className="text-red-500 hover:text-red-700 transition-colors duration-200 p-1 rounded-full hover:bg-red-50"
                        type="button"
                      >
                        <CloseIcon />
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <button 
              onClick={handleUpload}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              disabled={selectedFiles.length === 0}
            >
              {(isUploadingLocal) ? 'Uploading...' : 'Upload'}
            </button>
          </div>

          {/* Uploaded Files List */}
          {uploadedFiles.length > 0 && (
            <div className="mt-8 space-y-3">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Uploaded Files</h3>
              {uploadedFiles.map((file: any) => (
                <div key={file.file_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <div className="flex items-center space-x-3">
                    <PDFIcon />
                    <div>
                      <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                        {file.filename || file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {file.size ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : ''}
                        {file.upload_time ? ` | Uploaded: ${new Date(file.upload_time).toLocaleString()}` : ''}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(file.file_id)}
                    className="text-red-500 hover:text-red-700 transition-colors duration-200 p-1 rounded-full hover:bg-red-50"
                    type="button"
                  >
                    <CloseIcon />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
}
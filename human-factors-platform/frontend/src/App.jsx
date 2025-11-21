import React, { useState } from 'react';
import { Upload, AlertCircle, CheckCircle, Loader2, FileText, BarChart3 } from 'lucide-react';
import axios from 'axios';
import MetricsDisplay from './components/MetricsDisplay';
import InsightsDisplay from './components/InsightsDisplay';
import VisualizationDisplay from './components/VisualizationDisplay';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [imageContext, setImageContext] = useState('');
  const [generateInsights, setGenerateInsights] = useState(true);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResults(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('image_context', imageContext);
      formData.append('generate_llm_insights', generateInsights);

      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResults(response.data);
      } else {
        setError(response.data.message || 'Analysis failed');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResults(null);
      setError(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Human Factors Analysis Platform
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                AI-powered ergonomic assessment using SAM 3D Body + LLM
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Upload Image for Analysis</h2>
          
          {/* Drag and Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer"
          >
            <input
              type="file"
              id="file-upload"
              className="hidden"
              accept="image/*"
              onChange={handleFileSelect}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-lg text-gray-700 mb-2">
                Drop your image here or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports JPG, PNG, WebP (max 10MB)
              </p>
            </label>
          </div>

          {/* Preview */}
          {previewUrl && (
            <div className="mt-6">
              <img
                src={previewUrl}
                alt="Preview"
                className="max-h-64 mx-auto rounded-lg shadow-md"
              />
              <p className="text-center text-sm text-gray-600 mt-2">
                {selectedFile?.name}
              </p>
            </div>
          )}

          {/* Context Input */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Image Context (Optional)
            </label>
            <input
              type="text"
              value={imageContext}
              onChange={(e) => setImageContext(e.target.value)}
              placeholder="e.g., Office worker at desk, Factory worker lifting box..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* LLM Insights Toggle */}
          <div className="mt-4 flex items-center">
            <input
              type="checkbox"
              id="generate-insights"
              checked={generateInsights}
              onChange={(e) => setGenerateInsights(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="generate-insights" className="ml-2 text-sm text-gray-700">
              Generate AI-powered insights (requires API key)
            </label>
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || loading}
            className="mt-6 w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin mr-2 h-5 w-5" />
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 className="mr-2 h-5 w-5" />
                Analyze Posture
              </>
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 flex items-start">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {results && results.success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8 flex items-start">
            <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-green-800">Analysis Complete</h3>
              <p className="text-sm text-green-700 mt-1">
                Detected {results.num_people} person(s) in the image
              </p>
            </div>
          </div>
        )}

        {/* Results Display */}
        {results && results.success && (
          <div className="space-y-8">
            {/* Visualization */}
            {results.visualization && (
              <VisualizationDisplay
                originalImage={previewUrl}
                visualization={results.visualization}
              />
            )}

            {/* Metrics */}
            {results.metrics && (
              <MetricsDisplay metrics={results.metrics} />
            )}

            {/* LLM Insights */}
            {results.llm_insights && !results.llm_insights.error && (
              <InsightsDisplay insights={results.llm_insights} />
            )}
          </div>
        )}

        {/* Info Footer */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start">
            <FileText className="h-6 w-6 text-blue-600 mt-1 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                About This Platform
              </h3>
              <p className="text-sm text-blue-800 mb-3">
                This platform combines SAM 3D Body (Meta's state-of-the-art 3D human mesh recovery model)
                with advanced LLM analysis to provide comprehensive ergonomic assessments for Human Factors research.
              </p>
              <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                <li>Automatic 3D pose reconstruction from single images</li>
                <li>70-keypoint skeletal analysis with detailed hand/foot tracking</li>
                <li>Research-grade ergonomic metrics extraction</li>
                <li>AI-powered insights based on actual measurements</li>
                <li>OSHA and ISO compliance assessment</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

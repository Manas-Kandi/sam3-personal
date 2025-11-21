import React, { useState } from 'react';
import { Image as ImageIcon, Maximize2 } from 'lucide-react';

const VisualizationDisplay = ({ originalImage, visualization }) => {
  const [showModal, setShowModal] = useState(false);
  const [modalImage, setModalImage] = useState(null);

  const openModal = (imageSrc) => {
    setModalImage(imageSrc);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setModalImage(null);
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex items-center mb-6">
          <ImageIcon className="w-6 h-6 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">3D Pose Visualization</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Original Image */}
          <div className="relative group">
            <div className="bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={originalImage}
                alt="Original"
                className="w-full h-auto"
              />
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Original Image</span>
              <button
                onClick={() => openModal(originalImage)}
                className="flex items-center text-sm text-blue-600 hover:text-blue-700"
              >
                <Maximize2 className="w-4 h-4 mr-1" />
                Enlarge
              </button>
            </div>
          </div>

          {/* 3D Reconstruction */}
          <div className="relative group">
            <div className="bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={`data:image/jpeg;base64,${visualization}`}
                alt="3D Reconstruction"
                className="w-full h-auto"
              />
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">SAM 3D Body Reconstruction</span>
              <button
                onClick={() => openModal(`data:image/jpeg;base64,${visualization}`)}
                className="flex items-center text-sm text-blue-600 hover:text-blue-700"
              >
                <Maximize2 className="w-4 h-4 mr-1" />
                Enlarge
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Visualization includes:</strong> Original image with bounding box, 3D mesh overlay,
            front view reconstruction, and side view reconstruction. The 70-keypoint skeletal structure
            is used to generate accurate body pose and measurements.
          </p>
        </div>
      </div>

      {/* Modal for enlarged view */}
      {showModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
          onClick={closeModal}
        >
          <div className="relative max-w-6xl max-h-full">
            <button
              onClick={closeModal}
              className="absolute top-4 right-4 bg-white rounded-full p-2 hover:bg-gray-100 transition-colors"
            >
              <svg
                className="w-6 h-6 text-gray-700"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
            <img
              src={modalImage}
              alt="Enlarged view"
              className="max-w-full max-h-[90vh] rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default VisualizationDisplay;

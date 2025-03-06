import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16 text-center">
      <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="text-gray-600 mb-8">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link to="/" className="px-4 py-2 bg-blue-600 text-white rounded font-medium">
        Return to Home
      </Link>
    </div>
  );
};

export default NotFound;

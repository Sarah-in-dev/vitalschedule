import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-50 py-6 mt-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} Vital Care Innovations. All rights reserved.</p>
          <p className="mt-1">VitalSchedule: Predictive No-Show Analytics for Community Health Centers</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

import React, { useState } from 'react';

interface NewClaimFormProps {
  onSubmit: (claimData: ClaimData) => void;
  onCancel: () => void;
}

interface ClaimData {
  vehicle: string;
  damageDescription: string;
  photos: File[];
}

export default function NewClaimForm({ onSubmit, onCancel }: NewClaimFormProps) {
  const [formData, setFormData] = useState<ClaimData>({
    vehicle: '',
    damageDescription: '',
    photos: []
  });

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData(prev => ({
        ...prev,
        photos: [...Array.from(e.target.files!)]
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-4">
      <h3 className="text-xl font-semibold mb-4">Submit New Claim</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Vehicle Details
          </label>
          <input
            type="text"
            value={formData.vehicle}
            onChange={(e) => setFormData(prev => ({ ...prev, vehicle: e.target.value }))}
            className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            placeholder="Year, Make, Model"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Damage Description
          </label>
          <textarea
            value={formData.damageDescription}
            onChange={(e) => setFormData(prev => ({ ...prev, damageDescription: e.target.value }))}
            className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="Describe the damage to your vehicle"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Upload Photos
          </label>
          <input
            type="file"
            onChange={handlePhotoChange}
            className="w-full"
            accept="image/*"
            multiple
          />
          {formData.photos.length > 0 && (
            <p className="text-sm text-gray-500 mt-1">
              {formData.photos.length} photo(s) selected
            </p>
          )}
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Submit Claim
          </button>
        </div>
      </div>
    </form>
  );
}

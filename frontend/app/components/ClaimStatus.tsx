import React from "react";

interface ClaimStatusProps {
  claim: {
    id: string;
    status: string;
    lastUpdate: string;
    description: string;
  };
}

export default function ClaimStatus({ claim }: ClaimStatusProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "approved":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "under review":
        return "bg-blue-100 text-blue-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold">Claim #{claim.id}</h3>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
            claim.status
          )}`}
        >
          {claim.status}
        </span>
      </div>
      <div className="space-y-3">
        <div>
          <p className="text-gray-600">Description</p>
          <p className="font-medium">{claim.description}</p>
        </div>
        <div>
          <p className="text-gray-600">Last Update</p>
          <p className="font-medium">
            {new Date(claim.lastUpdate).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
}

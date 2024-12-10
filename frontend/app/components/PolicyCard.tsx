import React from "react";

interface PolicyCardProps {
  policyDetails: {
    type: string;
    coverage: string;
    limit: string;
    features: string[];
  };
}

export default function PolicyCard({ policyDetails }: PolicyCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <h3 className="text-xl font-semibold mb-4">{policyDetails.type}</h3>
      <div className="space-y-3">
        <div>
          <p className="text-gray-600">Coverage</p>
          <p className="font-medium">{policyDetails.coverage}</p>
        </div>
        <div>
          <p className="text-gray-600">Limit</p>
          <p className="font-medium">{policyDetails.limit}</p>
        </div>
        <div>
          <p className="text-gray-600">Features</p>
          <ul className="list-disc list-inside">
            {policyDetails.features.map((feature, index) => (
              <li key={index} className="text-sm">
                {feature}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

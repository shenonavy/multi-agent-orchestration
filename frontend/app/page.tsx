'use client';

import dynamic from 'next/dynamic';
import { Suspense, useState, useEffect } from 'react';

const ChatInterface = dynamic(() => import('./components/ChatInterface'), {
  loading: () => <div>Loading chat interface...</div>
});

const LoginForm = dynamic(() => import('./components/LoginForm'), {
  loading: () => <div>Loading login form...</div>
});

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return (
      <Suspense fallback={<div>Loading...</div>}>
        <LoginForm onLoginSuccess={handleLoginSuccess} />
      </Suspense>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Insurance Assistant</h1>
          <button
            onClick={() => {
              localStorage.removeItem('token');
              setIsAuthenticated(false);
            }}
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex">
          <Suspense fallback={<div>Loading...</div>}>
            <ChatInterface />
          </Suspense>
        </div>
      </main>
    </div>
  );
}

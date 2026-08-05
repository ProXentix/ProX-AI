import React from 'react';
import { MainLayout } from './components/layout/MainLayout';
import { Toaster } from 'sonner';

export function App() {
  return (
    <>
      <MainLayout />
      <Toaster position="top-right" theme="dark" richColors />
    </>
  );
}

export default App;

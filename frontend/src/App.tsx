// frontend/src/App.tsx
import React from 'react';
import { ChakraProvider, CSSReset } from '@chakra-ui/react';
import TranscriptionUpload from './components/TranscriptionUpload';

function App() {
  return (
    <ChakraProvider>
      <CSSReset />
      <TranscriptionUpload />
    </ChakraProvider>
  );
}

export default App;
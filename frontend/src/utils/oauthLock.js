// src/utils/oauthLock.js
const processedCallbackCodes = new Set();

export const hasProcessedCode = (code) => processedCallbackCodes.has(code);

export const markCodeAsProcessed = (code) => {
  processedCallbackCodes.add(code);
};

export const resetProcessedCodes = () => {
  processedCallbackCodes.clear();
};

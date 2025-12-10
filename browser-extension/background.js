// Background service worker for the extension

chrome.runtime.onInstalled.addListener(() => {
  console.log('CrewAI Job Extractor installed');
});

// Handle messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'processJob') {
    // Handle job processing requests
    console.log('Processing job:', request.jobData);
    sendResponse({status: 'processing'});
  }
  return true;
});

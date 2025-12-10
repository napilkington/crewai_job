document.addEventListener('DOMContentLoaded', function() {
  const extractBtn = document.getElementById('extractBtn');
  const statusDiv = document.getElementById('status');
  const serverUrlInput = document.getElementById('serverUrl');
  
  // Load saved server URL
  chrome.storage.sync.get(['serverUrl'], function(result) {
    if (result.serverUrl) {
      serverUrlInput.value = result.serverUrl;
    }
  });
  
  // Save server URL on change
  serverUrlInput.addEventListener('change', function() {
    chrome.storage.sync.set({serverUrl: serverUrlInput.value});
  });
  
  extractBtn.addEventListener('click', async function() {
    extractBtn.disabled = true;
    updateStatus('Extracting job posting...', 'loading');
    
    try {
      // Get the active tab
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      
      if (!tab.url.includes('linkedin.com/jobs')) {
        updateStatus('Please navigate to a LinkedIn job posting first', 'error');
        extractBtn.disabled = false;
        return;
      }
      
      // Execute content script to extract job data
      const results = await chrome.scripting.executeScript({
        target: {tabId: tab.id},
        function: extractJobData
      });
      
      if (!results || !results[0] || !results[0].result) {
        updateStatus('Failed to extract job data. Make sure you\'re on a job posting page.', 'error');
        extractBtn.disabled = false;
        return;
      }
      
      const jobData = results[0].result;
      
      updateStatus('Job extracted! Sending to CrewAI...', 'loading');
      
      // Send to local server
      const serverUrl = serverUrlInput.value || 'http://localhost:5000';
      const response = await fetch(`${serverUrl}/process-job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData)
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const result = await response.json();
      
      updateStatus('✅ Success! CV and cover letter generated. Check your output folder.', 'success');
      
      // Keep success message for 5 seconds
      setTimeout(() => {
        updateStatus('Ready to extract job posting', '');
        extractBtn.disabled = false;
      }, 5000);
      
    } catch (error) {
      console.error('Error:', error);
      updateStatus(`❌ Error: ${error.message}. Make sure the local server is running.`, 'error');
      extractBtn.disabled = false;
    }
  });
  
  function updateStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + type;
  }
});

// This function runs in the context of the LinkedIn page
function extractJobData() {
  const data = {
    title: '',
    company: '',
    location: '',
    description: '',
    url: window.location.href,
    extractedAt: new Date().toISOString()
  };
  
  // Try multiple selectors for job title
  const titleSelectors = [
    'h1.top-card-layout__title',
    'h1.t-24',
    'h2.t-24',
    '.job-details-jobs-unified-top-card__job-title h1',
    '.jobs-unified-top-card__job-title'
  ];
  
  for (const selector of titleSelectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      data.title = element.textContent.trim();
      break;
    }
  }
  
  // Try multiple selectors for company name
  const companySelectors = [
    'a.topcard__org-name-link',
    '.topcard__org-name-link',
    '.job-details-jobs-unified-top-card__company-name a',
    '.jobs-unified-top-card__company-name a'
  ];
  
  for (const selector of companySelectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      data.company = element.textContent.trim();
      break;
    }
  }
  
  // Try multiple selectors for location
  const locationSelectors = [
    '.topcard__flavor--bullet',
    '.job-details-jobs-unified-top-card__bullet',
    '.jobs-unified-top-card__bullet'
  ];
  
  for (const selector of locationSelectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim()) {
      data.location = element.textContent.trim();
      break;
    }
  }
  
  // Try multiple selectors for job description
  const descriptionSelectors = [
    '.show-more-less-html__markup',
    '.jobs-description__content',
    '.jobs-description-content__text',
    'article.jobs-description'
  ];
  
  for (const selector of descriptionSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      data.description = element.innerText || element.textContent;
      if (data.description.trim()) {
        break;
      }
    }
  }
  
  // If we still don't have description, try getting all visible text
  if (!data.description.trim()) {
    const mainContent = document.querySelector('.jobs-search__job-details') || 
                       document.querySelector('.job-view-layout') ||
                       document.querySelector('main');
    if (mainContent) {
      data.description = mainContent.innerText;
    }
  }
  
  return data;
}

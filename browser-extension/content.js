// Content script that runs on LinkedIn job pages
// This can be extended for additional functionality

console.log('CrewAI Job Extractor loaded on LinkedIn');

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractJob') {
    const jobData = extractJobData();
    sendResponse(jobData);
  }
  return true;
});

function extractJobData() {
  const data = {
    title: '',
    company: '',
    location: '',
    description: '',
    url: window.location.href,
    extractedAt: new Date().toISOString()
  };
  
  // Extract job title
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
  
  // Extract company name
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
  
  // Extract location
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
  
  // Extract job description
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
  
  return data;
}

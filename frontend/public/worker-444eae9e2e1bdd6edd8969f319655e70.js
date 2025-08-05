// Worker placeholder file
// This file is created to prevent 404 errors
// The actual worker functionality is not needed for this application

console.log('Worker placeholder loaded');

// Empty worker to satisfy browser requests
self.addEventListener('message', function(e) {
  console.log('Worker received message:', e.data);
});

self.addEventListener('error', function(e) {
  console.log('Worker error:', e);
}); 
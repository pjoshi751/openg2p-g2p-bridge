// Configuration settings

// Determine API base URL based on environment (optional, but good practice)
// For now, we assume the UI is served by the same origin as the API or a proxy is set up.
const API_BASE_URL = ''; // Use relative path if UI/API on same origin or proxied
// const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // Example for explicit URL

export const config = {
  api: {
    submitProof: `${API_BASE_URL}/api/v1/submit_proof`, // Corrected endpoint
  },
  maxPhotos: 5, // Store max photos constant here too
};

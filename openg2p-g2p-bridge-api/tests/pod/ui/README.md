# OpenG2P Proof Submission Frontend

This is a React frontend for the OpenG2P Proof Submission service. It provides a user interface for submitting proof images for disbursements.

## Features

- Form for submitting proof images with disbursement ID, agent name, and beneficiary ID
- Image preview before submission
- Form validation
- Success/error notifications
- Responsive design
- OpenG2P branding and color scheme

## Setup and Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Configuration

The application is configured to proxy API requests to the backend service running on `http://localhost:8000`. If your backend is running on a different URL, update the `proxy` field in `package.json`.

## Usage

1. Fill in the required fields (Disbursement ID, Agent Name, Beneficiary ID)
2. Upload a proof image
3. Click the "Submit Proof" button
4. You will receive a notification about the success or failure of the submission

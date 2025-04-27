import React from 'react';
import './App.css';
import ProofSubmissionForm from './components/ProofSubmissionForm';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import logo from './assets/OpenG2PHorizontalLogoLightBackground.png';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="App-header-left">
          <img src={logo} className="App-logo" alt="OpenG2P Logo" />
        </div>
        <div className="App-header-title center-title">
          <span className="brand-title" style={{ color: '#001167' }}>Proof Submission Portal</span>
        </div>
      </header>
      <main className="App-main">
        <div className="container">
          <p className="description">
            Submit proof of disbursement for beneficiaries
          </p>
          <ProofSubmissionForm />
        </div>
      </main>
      <footer className="App-footer">
        <p>&copy; {new Date().getFullYear()} OpenG2P. All rights reserved.</p>
      </footer>
      <ToastContainer position="top-right" autoClose={5000} />
    </div>
  );
}

export default App;

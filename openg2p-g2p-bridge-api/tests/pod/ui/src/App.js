import React from 'react';
import './App.css';
import ProofSubmissionForm from './components/ProofSubmissionForm';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="App-main">
        <div className="container">
          <p className="description">
            Submit proof of disbursement for beneficiaries
          </p>
          <ProofSubmissionForm />
        </div>
      </main>
      <Footer />
      <ToastContainer position="top-right" autoClose={5000} />
    </div>
  );
}

export default App;

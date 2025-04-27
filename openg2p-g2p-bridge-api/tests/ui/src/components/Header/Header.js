import React from 'react';
import './Header.css';
import logo from '../../assets/OpenG2PHorizontalLogoLightBackground.png'; // Adjust path

function Header() {
  return (
    <header className="Header">
      <div className="Header-left">
        <img src={logo} className="Header-logo" alt="OpenG2P Logo" />
      </div>
      <div className="Header-title center-title">
        {/* Remove inline style, rely on Header.css */}
        <span className="brand-title">Proof Submission Portal</span>
      </div>
    </header>
  );
}

export default Header;

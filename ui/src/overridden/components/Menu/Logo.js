import React from 'react';
import { Link } from 'react-router-dom';

export const Logo = ({ ...props }) => {
  return (
    <h2>
      <Link to="/" className="logo">
        CERN Library Catalogue
      </Link>
    </h2>
  );
};

export const LogoMobile = ({ ...props }) => {
  return (
    <h3>
      <Link to="/" className="logo">
        CERN Library Catalogue
      </Link>
    </h3>
  );
};

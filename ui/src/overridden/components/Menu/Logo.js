import React from "react";
import { Link } from "react-router-dom";

export const Logo = ({ ...props }) => {
  return (
    <>
      <h2 className="logo">
        <Link to="/" className="logo media-font-size">
          CERN Library Catalogue
        </Link>
      </h2>
      <div className="sublogo">
        A{" "}
        <a
          href="https://cds-blog.web.cern.ch/about/"
          target="_blank"
          rel="noopener noreferrer"
        >
          CDS
        </a>{" "}
        website
      </div>
    </>
  );
};

export const LogoMobile = ({ ...props }) => {
  return (
    <>
      <h3 className="logo">
        <Link to="/" className="logo media-font-size">
          CERN Library Catalogue
        </Link>
      </h3>
      <div className="sublogo">
        A{" "}
        <a
          href="https://cds-blog.web.cern.ch/about/"
          target="_blank"
          rel="noopener noreferrer"
        >
          CDS
        </a>{" "}
        website
      </div>
    </>
  );
};

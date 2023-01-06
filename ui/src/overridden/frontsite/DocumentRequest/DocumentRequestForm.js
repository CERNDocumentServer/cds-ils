/* eslint-disable jsx-a11y/label-has-associated-control */
import { DocumentRequestForm, InfoPopup } from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { parametrize } from "react-overridable";

const customPaymentInfo = {
  label: "Payment information",
  placeholder: "Insert budget code if applicable",
};

const customtitle = {
  label: "Book/Article title",
  placeholder: "Title",
};

const customIssn = {
  placeholder: "ISSN",
  customLabel: (
    <div className="display-flex">
      <label className="custom-label">ISSN</label>
      <InfoPopup message="Series/journal identifier" />
    </div>
  ),
};

const customRequestType = {
  placeholder: "Select type...",
  customLabel: (
    <div className="display-flex required field">
      <label className="custom-label">Request type</label>
      <InfoPopup
        message={
          <>
            <p>
              <strong>Loan:</strong> you want to borrow or suggest a new literature. The
              library will provide it to you from our collections or from another
              library. (No payment required)
            </p>
            <p>
              <strong>Purchase:</strong> you want to purchase this literature for your
              group or yourself. (Payment required)
            </p>
            <p>
              <strong>Article copy:</strong> if the article is not available in our
              collections, we will provide you with a scan. (No payment required)
            </p>
          </>
        }
      />
    </div>
  ),
};

const customNotes = {
  placeholder: "Notes for the library",
  customLabel: (
    <div>
      <label className="custom-label">Notes</label>
      <label className="label-subtitle">
        If you require multiple copies or, in case of purchase, you would like get a
        quote before, please specify it in the notes
      </label>
    </div>
  ),
};

export const DocumentRequestFormFields = parametrize(DocumentRequestForm, {
  paymentInfo: customPaymentInfo,
  title: customtitle,
  requestType: customRequestType,
  notes: customNotes,
  issn: customIssn,
});

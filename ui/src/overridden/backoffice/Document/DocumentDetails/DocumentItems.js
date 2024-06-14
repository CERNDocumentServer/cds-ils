import React from "react";
import { Link } from "react-router-dom";
import {
  BackOfficeRoutes,
  DocumentItems,
} from "@inveniosoftware/react-invenio-app-ils";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import { parametrize } from "react-overridable";

const viewDetails = ({ row }) => {
  return (
    <Link
      to={BackOfficeRoutes.itemDetailsFor(row.metadata.pid)}
      data-test={row.metadata.pid}
    >
      {row.metadata.barcode}
    </Link>
  );
};

const locationFormatter = ({ row }) => {
  return `${row.metadata.internal_location.name} (${row.metadata.internal_location.location.name})`;
};

const callNumberFormatter = ({ row }) => {
  if (!_isEmpty(row.metadata.identifiers)) {
    return row.metadata.identifiers.find(
      (identifier) => identifier.scheme === "CALL_NUMBER"
    ).value;
  }
  return "-";
};

const columnFormat = () => {
  return [
    {
      title: "Barcode",
      field: "metadata.barcode",
      formatter: viewDetails,
    },
    { title: "Status", field: "metadata.status" },
    { title: "Medium", field: "metadata.medium" },
    {
      title: "Location",
      field: "metadata.internal_location.name",
      formatter: locationFormatter,
    },
    {
      title: "Call number",
      field: "metadata.identifiers",
      formatter: callNumberFormatter,
    },
    { title: "Restrictions", field: "metadata.circulation_restriction" },
    {
      title: "Loan Status",
      field: "metadata.circulation.state",
      formatter: ({ row, col }) => {
        if (_get(row, col.field) === "ITEM_ON_LOAN") {
          return (
            <Link
              to={BackOfficeRoutes.loanDetailsFor(row.metadata.circulation.loan_pid)}
            >
              on loan
            </Link>
          );
        }
        return _get(row, col.field) || "-";
      },
    },
  ];
};

export const DocumentItemsLayout = parametrize(DocumentItems, {
  columnFormat: columnFormat,
});

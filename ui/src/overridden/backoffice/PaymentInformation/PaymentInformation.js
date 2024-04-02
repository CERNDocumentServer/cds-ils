import {
  PaymentInformation,
  formatPrice,
  invenioConfig,
} from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { Icon, Popup } from "semantic-ui-react";
import { parametrize } from "react-overridable";

function leftPaymentInfoTable(order, type = "acquisition-order") {
  const { payment } = order;
  if (type === "borrowing-request") {
    order.grand_total = order.total;
    order.grand_total_main_currency = order.total_main_currency;
  }
  return [
    {
      name: order.grand_total_main_currency?.currency
        ? `Total (${order.grand_total_main_currency.currency})`
        : `Total (${invenioConfig.APP.DEFAULT_CURRENCY})`,
      value: formatPrice(order.grand_total_main_currency) || "-",
    },
    {
      name:
        order.grand_total && order.grand_total.currency
          ? `Total (${order.grand_total.currency})`
          : "Total",
      value: formatPrice(order.grand_total) || "-",
    },
    { name: "Payment Mode", value: payment.mode || "-" },
    {
      name: (
        <>
          DAI ID{" "}
          <Popup
            content="Internal purchase requisition ID"
            trigger={<Icon name="info circle" size="large" />}
          />
        </>
      ),
      value: payment.internal_purchase_requisition_id || "-",
    },
    { name: "Notes", value: payment.debit_note || "-" },
  ];
}

export const PaymentInformationGrid = parametrize(PaymentInformation, {
  renderLeftTable: leftPaymentInfoTable,
});

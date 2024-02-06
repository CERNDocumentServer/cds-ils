import { OrderLine } from "@inveniosoftware/react-invenio-app-ils";
import PropTypes from "prop-types";
import React from "react";
import { Icon, Item, Popup } from "semantic-ui-react";
import { parametrize } from "react-overridable";

export const OrderDetailsMiddleColumn = ({ line }) => {
  return (
    <>
      <Item.Description>
        <label htmlFor="Copies ordered">Copies ordered: </label>
        {line.copies_ordered}
      </Item.Description>
      <Item.Description>
        <label htmlFor="Copies received">Copies received: </label>
        {line.copies_received || "-"}
      </Item.Description>
      <Item.Description>
        <label htmlFor="Payment mode">Payment mode: </label>
        {line.payment_mode || "-"}
      </Item.Description>
      <Item.Description>
        <label htmlFor="TID ID">TID ID: </label>
        {line.inter_departmental_transaction_id || "-"}{" "}
        <Popup
          content="Inter departmental transaction ID"
          trigger={<Icon name="info circle" />}
        />
      </Item.Description>
    </>
  );
};

OrderDetailsMiddleColumn.propTypes = {
  line: PropTypes.object.isRequired,
};

export const OrderDetailsLine = parametrize(OrderLine, {
  MiddleColumn: OrderDetailsMiddleColumn,
});

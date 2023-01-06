import React from "react";
import { List } from "semantic-ui-react";

export const NotAvailable = () => {
  return (
    <List.Item>
      <List.Icon name="info" />
      <List.Content>
        There are no physical copies for this literature currently available at the
        library. If you would like to loan it, please place a request. We will do our
        best to provide you with the literature as soon as possible.
      </List.Content>
    </List.Item>
  );
};

import React from "react";
import { Header, Message } from "semantic-ui-react";

export const OpeningHoursDetails = () => {
  return (
    <>
      <Header as="h2">Opening hours</Header>
      <Message info>
        <Message.Content>
          The CERN community can access the library, located in <b>52/1-052, </b>
          <b>
            <u>24/7</u>
          </b>
          !
          <br />
          Staff is available to help at the Library and Bookshop Welcome Desk, located
          in
          <b> 52/1-054</b>, open as per the schedule below :
          <br />
        </Message.Content>
      </Message>
    </>
  );
};

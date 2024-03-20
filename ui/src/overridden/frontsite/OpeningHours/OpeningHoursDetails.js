import React from "react";
import { Header, Message } from "semantic-ui-react";

const libraryLocation = (
  <a
    href="https://maps.cern.ch/?n=[%273/1-003%27,%2752/1-052%27,%2752/1-204%27]"
    target="_blank"
    rel="noreferrer"
  >
    <b>52/1-052</b>
  </a>
);

const deskLocation = (
  <a href="https://maps.cern.ch/?n=[%2752/1-054%27]" target="_blank" rel="noreferrer">
    <b>52/1-054</b>
  </a>
);

export const OpeningHoursDetails = () => {
  return (
    <>
      <Header as="h2">Opening hours</Header>
      <Message info>
        <Message.Content>
          The CERN community can access the library, located in {libraryLocation},{" "}
          <b>
            <u>24/7</u>
          </b>
          !
          <br />
          Staff is available to help at the Library and Bookshop Welcome Desk, located
          in {deskLocation}, open as per the schedule below :
          <br />
        </Message.Content>
      </Message>
    </>
  );
};

import React from "react";
import PropTypes from "prop-types";
import { Divider, Table } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";

export const DocumentConference = ({ conference }) => {
  return (
    <>
      <Divider horizontal>Conference information</Divider>
      {_isEmpty(conference) && "No conference information."}
      {conference.map((conf) => (
        <>
          <Table definition key={conf}>
            <Table.Body>
              <Table.Row>
                <Table.Cell width={4}>Conference</Table.Cell>
                <Table.Cell>{conf.title}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Acronym</Table.Cell>
                <Table.Cell>{conf.acronym}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Dates</Table.Cell>
                <Table.Cell>{conf.dates}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Identifiers</Table.Cell>
                <Table.Cell>
                  {conf.identifiers &&
                    conf.identifiers.map(
                      ({ scheme, value }) =>
                        `${scheme === "CERN" ? "" : `(${scheme})`} ${value}`
                    )}
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Place</Table.Cell>
                <Table.Cell>{conf.place}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Series number</Table.Cell>
                <Table.Cell>{conf.series}</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
          <br />
        </>
      ))}
    </>
  );
};

DocumentConference.propTypes = {
  conference: PropTypes.object,
};

DocumentConference.defaultProps = {
  conference: [],
};

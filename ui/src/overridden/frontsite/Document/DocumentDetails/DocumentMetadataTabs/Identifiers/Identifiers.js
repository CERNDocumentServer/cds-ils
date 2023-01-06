import { InfoPopup, SeparatedList } from "@inveniosoftware/react-invenio-app-ils";
import capitalize from "lodash/capitalize";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Divider, Table, Loader } from "semantic-ui-react";

// component not to be used in search pages
// might trigger a lot of requests
export class Identifiers extends Component {
  componentDidMount() {
    const { fetchVocabularyIdentifiers } = this.props;
    fetchVocabularyIdentifiers();
  }

  render() {
    const { identifiers, loading, vocabularyIdentifiers } = this.props;

    const noIdentifiers = _isEmpty(identifiers);

    if (noIdentifiers) {
      return (
        <>
          <Divider horizontal>Identifiers</Divider>
          No identifiers
        </>
      );
    }

    return (
      <>
        <Divider horizontal>Identifiers</Divider>
        {loading ? (
          <Loader />
        ) : (
          <Table definition>
            <Table.Body>
              <IdentifierRows
                identifiers={identifiers}
                vocabularyIdentifiers={vocabularyIdentifiers}
              />
            </Table.Body>
          </Table>
        )}
      </>
    );
  }
}

Identifiers.propTypes = {
  identifiers: PropTypes.array,
  vocabularyIdentifiers: PropTypes.array,
  fetchVocabularyIdentifiers: PropTypes.func.isRequired,
  loading: PropTypes.bool.isRequired,
};

Identifiers.defaultProps = {
  identifiers: [],
  vocabularyIdentifiers: null,
};

export const IdentifierRows = ({
  includeSchemes,
  identifiers,
  vocabularyIdentifiers,
}) => {
  const idsByScheme = {};

  for (const id of identifiers) {
    // Only include whitelisted schemes if includeSchemes is set
    if (includeSchemes.length === 0 || includeSchemes.includes(id.scheme)) {
      const value = createValueObject(
        vocabularyIdentifiers,
        id.value,
        id.scheme,
        id.material
      );

      if (id.scheme in idsByScheme) {
        idsByScheme[id.scheme].push(value);
      } else {
        idsByScheme[id.scheme] = [value];
      }
    }
  }

  return Object.entries(idsByScheme).map(([scheme, ids]) => {
    const values = ids.map((id) => (
      <>
        {id.urlPath ? (
          <a href={id.urlPath} target="_blank" rel="noreferrer noopener">
            {id.value}
          </a>
        ) : (
          id.value
        )}

        {id.material && (
          <>
            {" "}
            <InfoPopup message="Material for this identifier">
              ({capitalize(id.material)})
            </InfoPopup>
          </>
        )}
      </>
    ));

    return (
      <Table.Row key={scheme}>
        <Table.Cell width={4}>{scheme}</Table.Cell>
        <Table.Cell>
          <SeparatedList items={values} />
        </Table.Cell>
      </Table.Row>
    );
  });
};

const createValueObject = (vocabularyIdentifiers, value, scheme, material) => {
  const noVocabulariesIdentifiers = !vocabularyIdentifiers?.length;
  const defaultValue = { value, material };

  if (noVocabulariesIdentifiers) return defaultValue;

  const matchingVocabularyIdentifier = vocabularyIdentifiers.find(
    (identifier) => identifier.value === scheme
  );

  const notValidForUrl =
    !matchingVocabularyIdentifier || !matchingVocabularyIdentifier.url_path;

  if (notValidForUrl) return defaultValue;

  const urlPath = matchingVocabularyIdentifier.url_path.replace("{identifier}", value);

  return { value, material, urlPath };
};

IdentifierRows.propTypes = {
  includeSchemes: PropTypes.array,
  identifiers: PropTypes.array,
};

IdentifierRows.defaultProps = {
  includeSchemes: [],
};

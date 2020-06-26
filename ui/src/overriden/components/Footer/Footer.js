import { FrontSiteRoutes } from '@inveniosoftware/react-invenio-app-ils';
import Qs from 'qs';
import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Grid, Header, List } from 'semantic-ui-react';
import { config } from '../../../config';

export const Footer = ({ ...props }) => {
  const onClickBookRequestLink = () => {
    const params = Qs.parse(window.location.search);
    const queryString = params['?q'];
    return {
      pathname: FrontSiteRoutes.documentRequestForm,
      state: { queryString },
    };
  };

  return (
    <footer>
      <Container fluid className="footer-upper">
        <Container>
          <Grid columns={3} stackable>
            <Grid.Column>
              <Header as="h4" content="CERN Library" />
              <p>
                Open 24 hours a day <br />
                every day of the year <br />
                <br />
                Staffed from 8.30 to 18.00 <br />
                Monday-Friday
              </p>
            </Grid.Column>
            <Grid.Column>
              <Header as="h4" content="Help" />
              <List>
                <List.Item>
                  <Link to={onClickBookRequestLink()}>
                    Request new literature
                  </Link>
                </List.Item>
                <List.Item>
                  <a href="#" target="_blank" rel="noopener noreferrer">
                    F.A.Q.
                  </a>
                </List.Item>
                <List.Item>
                  <a
                    href=" https://library.web.cern.ch "
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Scientific Information Service
                  </a>
                </List.Item>
              </List>
            </Grid.Column>
            <Grid.Column>
              <Header as="h4" content="Contact us" />
              <List>
                <List.Item>+41 22 767 24 35</List.Item>
                <List.Item>
                  <a href={`mailto:${config.uiConfig.library_email}`}>
                    {config.uiConfig.library_email}
                  </a>
                </List.Item>
              </List>
              <Header as="h4" content="Technical Support" />
              <List>
                <List.Item>
                  <a href={`mailto:${config.uiConfig.support_email}`}>
                    {config.uiConfig.support_email}
                  </a>
                </List.Item>
              </List>
            </Grid.Column>
          </Grid>
        </Container>
      </Container>
      <Container fluid className="footer-lower">
        <Container>
          <Header as="h4" textAlign="center">
            <Header.Content>CERN Library Catalogue</Header.Content>
            <Header.Subheader>
              Powered by{' '}
              <a href="https://inveniosoftware.org" target="_blank">
                INVENIO
              </a>
            </Header.Subheader>
          </Header>
        </Container>
      </Container>
    </footer>
  );
};

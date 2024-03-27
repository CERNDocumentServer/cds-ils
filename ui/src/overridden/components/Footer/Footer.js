import {
  FrontSiteRoutes,
  getStaticPageByName,
} from "@inveniosoftware/react-invenio-app-ils";
import React from "react";
import { Link } from "react-router-dom";
import { Container, Grid, Header, Image, List } from "semantic-ui-react";

export const Footer = ({ ...props }) => {
  const cernLogo = process.env.PUBLIC_URL + "/images/cern-logo-white-150.png";
  return (
    <footer>
      <Container fluid className="footer-upper">
        <Container>
          <Grid columns={4} stackable>
            <Grid.Column>
              <Header as="h4" content="About" />
              <List relaxed>
                <List.Item>
                  <Link to={getStaticPageByName("about").route}>About</Link>
                </List.Item>
                <List.Item>
                  <Link to={getStaticPageByName("terms").route}>
                    Terms and Conditions
                  </Link>
                </List.Item>
                <List.Item>
                  <Link to={getStaticPageByName("privacy-policy").route}>
                    Privacy Policy
                  </Link>
                </List.Item>
              </List>
            </Grid.Column>
            <Grid.Column>
              <Header as="h4" content="Need help?" />
              <List relaxed>
                <List.Item>
                  <Link to={getStaticPageByName("contact").route}>Contact us</Link>
                </List.Item>
                <List.Item>
                  <Link to={getStaticPageByName("faq").route}>F.A.Q.</Link>
                </List.Item>
                <List.Item>
                  <Link to={getStaticPageByName("search-guide").route}>
                    Search guide
                  </Link>
                </List.Item>
                <List.Item>
                  <Link to={FrontSiteRoutes.documentRequestForm}>
                    Request document (loan or purchase)
                  </Link>
                </List.Item>
              </List>
            </Grid.Column>
            <Grid.Column>
              <Header as="h4" content="CERN Library" />
              <List relaxed>
                <List.Item>
                  <Link to={FrontSiteRoutes.openingHours}>Opening hours</Link>
                </List.Item>
                <List.Item>
                  <a
                    href="https://scientific-info.cern"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Scientific Information Service
                  </a>
                </List.Item>
                <List.Item>
                  Location:{" "}
                  <a
                    href="https://maps.cern.ch/?n=['52/1-052','52/1-054','3/1-003']"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Building 52/1-052
                  </a>
                </List.Item>
                <List.Item>
                  Tel.: <a href="tel:+41227672444">+41 22 767 2444</a>
                </List.Item>
              </List>
            </Grid.Column>
            <Grid.Column>
              <Header as="h4" content="CDS - CERN Document Server" />
              <List relaxed>
                <List.Item>
                  <p>
                    This website is part of the{" "}
                    <a
                      href="https://cds-blog.web.cern.ch/about/"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      CDS
                    </a>{" "}
                    service
                  </p>
                </List.Item>
                <List.Item>
                  <a
                    href="https://cds-blog.web.cern.ch"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    What's up on CDS - Blog
                  </a>
                </List.Item>
              </List>
              <Image src={cernLogo} size="tiny" href="https://home.cern" />
            </Grid.Column>
          </Grid>
        </Container>
      </Container>
      <Container fluid className="footer-lower">
        <Container>
          <Header as="h4" textAlign="center">
            <Header.Content>CERN Library Catalogue</Header.Content>
            <Header.Subheader>
              Powered by{" "}
              <a
                href="https://inveniosoftware.org"
                target="_blank"
                rel="noopener noreferrer"
              >
                INVENIO
              </a>
            </Header.Subheader>
          </Header>
        </Container>
      </Container>
    </footer>
  );
};

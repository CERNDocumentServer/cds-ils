import React from "react";
import { Embed, Header, Button } from "semantic-ui-react";
import { shelfLink } from "../../../utils";

export class DocumentCirculationExtras extends React.Component {
  render() {
    return (
      <div className="mt-15">
        <Header as="h4" content="Find it on shelf" />
        <Embed
          active
          // Placeholder links for for now, depending on the review of where it should be placed, will implement redux code to get the location of the first item
          url={shelfLink("05", true)}
          style={{
            "padding-bottom": "30%",
          }}
          iframe={{
            "pointer-events": "none",
          }}
        />
        <Button
          as="a"
          smooth
          href={shelfLink("05")}
          target="_blank"
          rel="noreferrer"
          color="blue"
          fluid
        >
          Open MapCERN
        </Button>
      </div>
    );
  }
}

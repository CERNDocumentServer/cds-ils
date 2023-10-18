import React from "react";
import { Statistic } from "semantic-ui-react";
import PropTypes from "prop-types";

export const RenderStatistics = ({ statistics, selectedResult, applyFilter }) => {
  return (
    <Statistic.Group widths="seven" size="small">
      {Object.keys(statistics).map(function (statisticKey, index) {
        return (
          <Statistic
            className={
              selectedResult === statisticKey
                ? "import-statistic statistic-selected"
                : "import-statistic"
            }
            key={statisticKey}
            onClick={() => applyFilter(statisticKey)}
          >
            <Statistic.Value>{statistics[statisticKey].value}</Statistic.Value>
            <Statistic.Label>{statistics[statisticKey].text}</Statistic.Label>
          </Statistic>
        );
      }, this)}
    </Statistic.Group>
  );
};

RenderStatistics.propTypes = {
  statistics: PropTypes.object.isRequired,
  selectedResult: PropTypes.string.isRequired,
  applyFilter: PropTypes.func.isRequired,
};

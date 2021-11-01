import React from 'react';
import { Statistic } from 'semantic-ui-react';
import PropTypes from 'prop-types';

export const RenderStatistics = ({
  statistics,
  selectedResult,
  applyFilter,
}) => {
  return (
    <Statistic.Group widths="seven">
      {Object.keys(statistics).map(function(statistic, index) {
        return (
          <Statistic
            className={
              selectedResult === statistic
                ? 'import-statistic statistic-selected'
                : 'import-statistic'
            }
            key={statistic}
            onClick={() => applyFilter(statistic)}
          >
            <Statistic.Value>{statistics[statistic].value}</Statistic.Value>
            <Statistic.Label>{statistics[statistic].text}</Statistic.Label>
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

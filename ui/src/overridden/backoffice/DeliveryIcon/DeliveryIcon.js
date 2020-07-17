import React from 'react';
import { Icon, List } from 'semantic-ui-react';
import PropTypes from 'prop-types';

export const DeliveryIcon = ({ ...props }) => {
  const { deliveryMethod, size, showName, asListItem, loanState } = props;
  let iconClass;
  if (
    deliveryMethod === null ||
    (loanState !== null && loanState !== 'PENDING')
  ) {
    return '';
  } else if (deliveryMethod === 'DELIVERY') {
    iconClass = 'dolly';
  } else if (deliveryMethod === 'PICKUP') {
    iconClass = 'warehouse';
  }
  const icon = (
    <>
      {showName && `${deliveryMethod} `}
      <Icon size={size} color="grey" className={iconClass} />
    </>
  );
  return asListItem ? (
    <List>
      <List.Item>
        <List.Content>
          <label>Delivery</label> {icon}
        </List.Content>
      </List.Item>
    </List>
  ) : (
    icon
  );
};

DeliveryIcon.propTypes = {
  deliveryMethod: PropTypes.string,
  size: PropTypes.string,
  showName: PropTypes.bool,
  asListItem: PropTypes.bool,
  loanState: PropTypes.string,
};

DeliveryIcon.defaultProps = {
  deliveryMethod: null,
  size: null,
  showName: false,
  asListItem: false,
  loanState: null,
};

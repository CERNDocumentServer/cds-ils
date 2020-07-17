import { DocumentRequestForm } from '@inveniosoftware/react-invenio-app-ils';
import { parametrize } from 'react-overridable';

const customPaymentInfo = {
  label: 'Payment information',
  placeholder: 'Insert budget code if applicable',
};

export const DocumentRequestFormFields = parametrize(DocumentRequestForm, {
  paymentInfo: customPaymentInfo,
});

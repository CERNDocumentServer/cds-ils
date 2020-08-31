export const config = {
  APP: {
    staticPages: [
      { name: 'about', route: '/about', apiURL: '1' },
      { name: 'terms', route: '/terms', apiURL: '2' },
      { name: 'faq', route: '/faq', apiURL: '3' },
    ],
    supportEmail: 'cds.support@cern.ch',
    libraryEmail: 'library.desk@cern.ch',
  },
  VOCABULARIES: {
    documentRequests: {
      doc_req_type: 'doc_req_type',
      doc_req_payment_method: 'doc_req_payment_method',
      doc_req_medium: 'doc_req_medium',
    },
  },
  DOCUMENTS: {
    extensions: {
      label: 'Other',
      fields: {
        'unit:accelerator': {
          label: 'Accelerator',
          type: 'string',
          default: '',
        },
        'unit:curated_relation': {
          label: 'Curated Relation',
          type: 'boolean',
          default: false,
        },
        'unit:experiment': {
          label: 'Experiment',
          type: 'string',
          default: '',
        },
        'unit:institution': {
          label: 'Institution',
          type: 'string',
          default: '',
        },
        'unit:legacy_name': {
          label: 'Legacy Name',
          type: 'string',
          default: '',
        },
        'unit:project': {
          label: 'Project',
          type: 'string',
          default: '',
        },
        'unit:study': {
          label: 'Study',
          type: 'string',
          default: '',
        },
        'standard_review:applicability': {
          label: 'Status CERN Applicability',
          type: 'string',
          default: '',
        },
        'standard_review:standard_validity': {
          label: 'Status Standard Validity',
          type: 'string',
          default: '',
          isRequired: true,
        },
        'standard_review:checkdate': {
          label: 'Status check date',
          type: 'date',
          default: '',
        },
        'standard_review:comment': {
          label: 'Status comment',
          type: 'string',
          default: '',
        },
        'standard_review:expert': {
          label: 'Status expert',
          type: 'string',
          default: '',
        },
      },
    },
  },
};

export const uiConfig = {
  extensions: {
    document: {
      label: 'Other',
      fields: {
        'accelerator_experiments:accelerator': {
          label: 'Accelerator',
          type: 'string',
          default: '',
        },
        'accelerator_experiments:curated_relation': {
          label: 'Curated Relation',
          type: 'boolean',
          default: false,
        },
        'accelerator_experiments:experiment': {
          label: 'Experiment',
          type: 'string',
          default: '',
        },
        'accelerator_experiments:institution': {
          label: 'Institution',
          type: 'string',
          default: '',
        },
        'accelerator_experiments:legacy_name': {
          label: 'Legacy Name',
          type: 'string',
          default: '',
        },
        'accelerator_experiments:project': {
          label: 'Project',
          type: 'string',
          default: '',
        },
        'accelerator_experiments:study': {
          label: 'Study',
          type: 'string',
          default: '',
        },
        'standard_CERN_status:CERN_applicability': {
          label: 'Status CERN Applicability',
          type: 'string',
          default: '',
        },
        'standard_CERN_status:standard_validity': {
          label: 'Status Standard Validity',
          type: 'string',
          default: '',
          isRequired: true,
        },
        'standard_CERN_status:checkdate': {
          label: 'Status check date',
          type: 'date',
          default: '',
        },
        'standard_CERN_status:comment': {
          label: 'Status comment',
          type: 'string',
          default: '',
        },
        'standard_CERN_status:expert': {
          label: 'Status expert',
          type: 'string',
          default: '',
        },
      },
    },
  },
  staticPages: [
    { name: 'about', route: '/about', apiURL: '1' },
    { name: 'terms', route: '/terms', apiURL: '2' },
    { name: 'faq', route: '/faq', apiURL: '3' },
  ],
  support_email: 'cds.support@cern.ch',
  library_email: 'library.desk@cern.ch',
};

export const config = {
  uiConfig: uiConfig,
};

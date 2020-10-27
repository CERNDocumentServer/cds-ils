export const config = {
  APP: {
    LOGO_SRC: null,
    STATIC_PAGES: [
      { name: 'about', route: '/about', apiURL: '1' },
      { name: 'terms', route: '/terms', apiURL: '2' },
      { name: 'faq', route: '/faq', apiURL: '3' },
      { name: 'contact', route: '/contact', apiURL: '4' },
    ],
    ENABLE_LOCAL_ACCOUNT_LOGIN: false,
    OAUTH_PROVIDERS: {
      github: {
        enabled: false,
      },
      cern: {
        enabled: true,
        label: 'Sign in with CERN',
        name: 'cern',
        url: '/api/oauth/login/cern_openid/',
        icon: '',
        semanticUiColor: 'grey',
        className: '',
      },
    },
    ENVIRONMENTS: [
      {
        name: 'dev',
        display: {
          text: 'Development environment',
          color: 'blue',
          icon: 'code',
        },
      },
      {
        name: 'sandbox',
        display: {
          text: 'Sandbox environment',
          color: 'teal',
          icon: 'camera',
        },
      },
      {
        name: 'production',
        display: {
          roles: ['admin'],
          text: 'Production environment',
          color: 'red',
          icon: 'warning',
        },
      },
    ],
  },
  CIRCULATION: {
    extensionsMaxCount: 10000, // should be infinite
    requestDuration: 120,
    loanWillExpireDays: 3,
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
          type: 'vocabulary',
          vocabularyType: 'document_accelerators',
          default: '',
        },
        'unit:curated_relation': {
          label: 'Curated Relation',
          type: 'boolean',
          default: false,
        },
        'unit:experiment': {
          label: 'Experiment',
          type: 'vocabulary',
          vocabularyType: 'document_experiments',
          default: '',
        },
        'unit:institution': {
          label: 'Institution',
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
          type: 'vocabulary',
          vocabularyType: 'document_standard_reviews',
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
